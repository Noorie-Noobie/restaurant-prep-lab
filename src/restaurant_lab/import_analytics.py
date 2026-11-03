"""Read-only dashboard data for exactly one imported source/location.

Integer minor money units and integer millionths are the authoritative values.
Never concatenate this result with the historical pizza-demo tables.
"""
from contextlib import contextmanager
from datetime import date, datetime
import json
from pathlib import Path
import sqlite3
from zoneinfo import ZoneInfo

from .imports import APP_ID, DEFAULT_DB, ImportRejected, LocationConfig, _state


@contextmanager
def _connection(db_path):
    # mode=ro never creates a missing DB. One transaction gives a consistent snapshot.
    con = sqlite3.connect(Path(db_path).resolve().as_uri() + '?mode=ro', uri=True)
    try:
        con.row_factory = sqlite3.Row
        con.execute('BEGIN')
        if con.execute('PRAGMA application_id').fetchone()[0] != APP_ID or con.execute('PRAGMA user_version').fetchone()[0] != 1:
            raise ImportRejected('Select a canonical v1 database, not the pizza demo database')
        yield con
    finally:
        con.close()


def available_locations(db_path=DEFAULT_DB):
    """Explicit selector choices. Missing DB returns []; malformed DB raises."""
    if not Path(db_path).exists():
        return []
    with _connection(db_path) as con:
        return [LocationConfig(**json.loads(row[0])) for row in con.execute(
            'SELECT config_json FROM locations ORDER BY source,location_id')]


def dashboard(config: LocationConfig, *, start: date, end: date, db_path=DEFAULT_DB):
    """Inclusive BUSINESS-date filter; rush bins use actual local calendar weekday/hour.

    Orders count distinct orders with >=1 completed line, even fully refunded ones.
    Money excludes voids; fulfilled amounts include voids (food may have been prepared).
    Latest snapshot amounts belong to original business date, not refund posting date.
    No absent date is imputed as an open day with zero sales. No average/profit claims.
    """
    config.validate()
    if type(start) is not date or type(end) is not date or start > end:
        raise ValueError('Use date objects with start <= end')
    with _connection(db_path) as con:
        revision, database_id = _state(con, config)
        saved = con.execute('SELECT 1 FROM locations WHERE source=? AND location_id=?',
                            (config.source, config.location_id)).fetchone()
        if not saved:
            raise ImportRejected('Selected source/location has not been imported')
        rows = [dict(r) for r in con.execute('''SELECT * FROM canonical_lines
            WHERE source=? AND location_id=? AND business_date BETWEEN ? AND ?''',
            (config.source, config.location_id, start.isoformat(), end.isoformat()))]
    totals = dict(gross_minor=0, discount_minor=0, refund_minor=0, net_minor=0)
    items, orders, fulfilled, quantity = {}, {}, {}, {}
    for row in rows:
        unit = row['quantity_unit']
        fulfilled[unit] = fulfilled.get(unit, 0) + row['fulfilled_micros']
        key = (row['item_id'], unit)
        item = items.setdefault(key, dict(item_id=key[0], quantity_unit=unit,
            item_name=row['item_name'], label_updated_at=row['source_updated_at'],
            quantity_micros=0, fulfilled_micros=0, net_minor=0))
        if (row['source_updated_at'], row['item_name']) > (item['label_updated_at'], item['item_name']):
            item.update(item_name=row['item_name'], label_updated_at=row['source_updated_at'])
        item['fulfilled_micros'] += row['fulfilled_micros']
        if row['status'] == 'voided':
            continue
        orders[row['order_id']] = row['ordered_at']
        quantity[unit] = quantity.get(unit, 0) + row['quantity_micros']
        item['quantity_micros'] += row['quantity_micros']
        net = row['gross_minor'] - row['discount_minor'] - row['refund_minor']
        item['net_minor'] += net
        for field in ('gross_minor', 'discount_minor', 'refund_minor'):
            totals[field] += row[field]
        totals['net_minor'] += net
    rush = [[0] * 24 for _ in range(7)]
    for timestamp in orders.values():
        local = datetime.fromisoformat(timestamp).astimezone(ZoneInfo(config.timezone))
        rush[local.weekday()][local.hour] += 1
    return dict(source_kind='canonical_import', source=config.source,
        location_id=config.location_id, currency=config.currency, timezone=config.timezone,
        business_day_start_hour=config.business_day_start_hour,
        start=start.isoformat(), end=end.isoformat(), revision=revision, database_id=database_id,
        line_count=len(rows), order_count=len(orders),
        voided_lines=sum(r['status'] == 'voided' for r in rows),
        observed_business_dates=sorted({r['business_date'] for r in rows}),
        quantity_micros_by_unit=quantity, fulfilled_micros_by_unit=fulfilled,
        totals=totals, items=sorted(items.values(), key=lambda r: (-r['net_minor'], r['item_id'], r['quantity_unit'])),
        rush_orders=rush)
