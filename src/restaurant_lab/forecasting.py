"""Transparent fulfilled-quantity baseline; no recipe or inventory changes."""
from dataclasses import dataclass
from datetime import date, datetime, time, timezone, timedelta
from fractions import Fraction
import json
from zoneinfo import ZoneInfo

from .import_analytics import _connection
from .imports import DEFAULT_DB, LocationConfig, ImportRejected, _state


@dataclass(frozen=True)
class MenuItem:
    item_id: str
    unit: str
    available_from: date
    known_at: datetime


def _aware(value):
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError('Use timezone-aware timestamps')
    return value.astimezone(timezone.utc)


def _snapshots(config, as_of, db_path):
    """Replay only snapshots actually imported AND source-reported by as_of.

    Never train historical forecasts from today's corrected current-state table.
    A bulk import today cannot establish what the application knew last month.
    """
    as_of = _aware(as_of)
    latest = {}
    with _connection(db_path) as con:
        _state(con, config)
        if not con.execute("SELECT 1 FROM locations WHERE source=? AND location_id=?", (config.source,config.location_id)).fetchone():
            raise ImportRejected("Selected source/location has not been imported")
        for event in con.execute('''SELECT h.after_json,b.committed_at FROM line_history h
            JOIN import_batches b USING(batch_id) WHERE h.source=? AND h.location_id=?''',
            (config.source, config.location_id)):
            committed = _aware(datetime.fromisoformat(event['committed_at']))
            row = json.loads(event['after_json'])
            updated = _aware(datetime.fromisoformat(row['source_updated_at']))
            if max(committed, updated) > as_of:
                continue
            key = (row['order_id'], row['line_id'])
            rank = (updated, committed)
            if key not in latest or rank > latest[key][0]:
                latest[key] = (rank, row)
    return [r for _, r in latest.values()]


def _total(rows, day, item):
    # Fulfilled food remains operational demand even when financially refunded/voided.
    return sum(r['fulfilled_micros'] for r in rows if r['business_date'] == day.isoformat()
               and r['item_id'] == item.item_id and r['quantity_unit'] == item.unit)


def forecast(config: LocationConfig, *, target: date, as_of: datetime,
             coverage: dict[date, datetime], menu: list[MenuItem],
             lookback=4, minimum=2, db_path=DEFAULT_DB, comparable_weekdays=True):
    """coverage maps confirmed complete/open business dates to confirmation time.

    Missing SKU on a covered, available-menu date is zero; other dates are unknown.
    Returns exact mean in millionths as numerator/denominator, plus upward-rounded
    micros for planner handoff. Whole-item/batch rounding belongs to the planner.
    """
    config.validate(); as_of = _aware(as_of)
    if type(target) is not date or type(lookback) is not int or type(minimum) is not int or not 1 <= minimum <= lookback <= 52:
        raise ValueError('Valid target date and 1 <= minimum <= lookback <= 52 required')
    boundary = datetime.combine(target, time(config.business_day_start_hour), ZoneInfo(config.timezone))
    if as_of > boundary:
        raise ValueError('Prediction issue time must not be after target business-day start')
    if len({(m.item_id, m.unit) for m in menu}) != len(menu):
        raise ValueError('Duplicate menu item/unit')
    for day, known in coverage.items():
        if type(day) is not date:
            raise ValueError('Coverage keys must be dates')
        closes = datetime.combine(day + timedelta(days=1), time(config.business_day_start_hour), ZoneInfo(config.timezone))
        if _aware(known) < closes:
            raise ValueError('Coverage can only be confirmed after the business day closes')
    rows = _snapshots(config, as_of, db_path)
    output = []
    for item in menu:
        if type(item.available_from) is not date or item.unit not in {'each','kg','g','l','ml'} or not item.item_id:
            raise ValueError('Menu needs item ID, supported unit and availability date')
        known = _aware(item.known_at)
        eligible = sorted(d for d,k in coverage.items() if d < target and d >= item.available_from
                          and _aware(k) <= as_of and (not comparable_weekdays or d.weekday()==target.weekday()))[-lookback:]
        if known > as_of or item.available_from > target:
            eligible = []
        values = [_total(rows,d,item) for d in eligible]
        # Zero-sales evidence is a caller assertion, not inferred from absent orders.
        ready = len(values) >= minimum
        mean = Fraction(sum(values),len(values)) if ready else None
        output.append(dict(item_id=item.item_id, quantity_unit=item.unit,
            status='ready' if ready else 'insufficient_history',
            observation_dates=[d.isoformat() for d in eligible], observation_count=len(values),
            observed_fulfilled_micros=values,
            mean_micros_numerator=mean.numerator if ready else None,
            mean_micros_denominator=mean.denominator if ready else None,
            forecast_micros=-(-mean.numerator//mean.denominator) if ready else None))
    return dict(source=config.source,location_id=config.location_id,currency=config.currency,
        timezone=config.timezone,target=target.isoformat(),as_of=as_of.isoformat(),
        method='prior_matching_weekdays' if comparable_weekdays else 'prior_complete_dates',
        lookback=lookback,minimum=minimum,items=output,
        limitation='Fulfilled quantities underestimate unconstrained demand when stockouts or lost sales occurred.')


def backtest(config, *, targets, evaluation_as_of, coverage, menu, db_path=DEFAULT_DB,
             lookback=4, minimum=2):
    """Rolling origin; each prediction sees only then-known imports/menu/coverage.

    Ground truth uses evaluation-time snapshots and explicitly complete target dates.
    Metrics stay separate by item/unit. Skipped origins are counted, never filled.
    """
    evaluation_as_of = _aware(evaluation_as_of)
    actual_rows = _snapshots(config,evaluation_as_of,db_path)
    results=[]; errors={}
    for target in sorted(set(targets)):
        cutoff=datetime.combine(target,time(config.business_day_start_hour),ZoneInfo(config.timezone))
        if cutoff >= evaluation_as_of:
            raise ValueError('Evaluation time must follow every target origin')
        for weekday in (True,False):
            prediction=forecast(config,target=target,as_of=cutoff,coverage=coverage,menu=menu,
                lookback=lookback,minimum=minimum,db_path=db_path,comparable_weekdays=weekday)
            for item,pred in zip(menu,prediction['items']):
                complete=target in coverage and _aware(coverage[target]) <= evaluation_as_of
                scored=complete and pred['status']=='ready'
                actual=_total(actual_rows,target,item) if scored else None
                key=(item.item_id,item.unit,prediction['method'])
                bucket=errors.setdefault(key,dict(scored=0,skipped=0,error=Fraction(0)))
                if scored:
                    error=abs(Fraction(pred['mean_micros_numerator'],pred['mean_micros_denominator'])-actual)
                    bucket['error']+=error;bucket['scored']+=1
                else: bucket['skipped']+=1
                results.append(dict(target=target.isoformat(),method=prediction['method'],
                    **pred,actual_micros=actual,scored=scored))
    metrics=[]
    for (item,unit,method),b in errors.items():
        mae=b['error']/b['scored']/1000000 if b['scored'] else None
        metrics.append(dict(item_id=item,quantity_unit=unit,method=method,scored=b['scored'],
            skipped=b['skipped'],mae_units=str(float(mae)) if mae is not None else None))
    return dict(origins=results,metrics=metrics)
