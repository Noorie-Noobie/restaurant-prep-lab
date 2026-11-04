from datetime import datetime, timedelta, timezone
from pathlib import Path
import runpy
import sqlite3
import pytest
from restaurant_lab.forecasting import forecast, backtest, MenuItem

DEMO=runpy.run_path(str(Path(__file__).resolve().parents[1]/'scripts/demo_forecast.py'))
CONFIG=DEMO['CONFIG']; START=DEMO['START']

@pytest.fixture
def history(tmp_path):
    db=tmp_path/'demo.sqlite';coverage,menu=DEMO['build_demo'](db)
    return db,coverage,menu

def predict(history,week=12,**kwargs):
    db,coverage,menu=history;target=START+timedelta(weeks=week)
    return forecast(CONFIG,target=target,as_of=datetime.combine(target,datetime.min.time(),timezone.utc)+timedelta(hours=4),coverage=coverage,menu=menu,db_path=db,**kwargs)

def test_known_mean_and_no_database_writes(history):
    db,_,_=history;before=db.read_bytes();p=predict(history)['items'][0]
    assert p['forecast_micros']==29000000 and p['observation_count']==4
    assert p['observed_fulfilled_micros']==[26000000,28000000,30000000,32000000]
    assert db.read_bytes()==before

def test_backtest_temporal_origins(history):
    db,c,m=history
    b=backtest(CONFIG,targets=[START+timedelta(weeks=w) for w in range(8,12)],evaluation_as_of=datetime(2026,9,1,tzinfo=timezone.utc),coverage=c,menu=m,db_path=db)
    assert [(x['scored'],x['mae_units']) for x in b['metrics']]==[(4,'5.0'),(4,'8.0')]
    for origin in b['origins']:
        assert all(d<origin['target'] for d in origin['observation_dates'])

def test_insufficient_and_missing_coverage_not_zero(history):
    assert predict(history,week=1)['items'][0]['forecast_micros'] is None
    db,c,m=history
    out=predict((db,{},m))['items'][0]
    assert out['status']=='insufficient_history' and out['observation_count']==0

def test_late_import_and_correction_cannot_leak(history):
    db,c,m=history;before=predict(history,week=8)
    with sqlite3.connect(db) as con:
        # Corrupt future-only snapshots with huge values: old forecast must be unchanged.
        con.execute("UPDATE line_history SET after_json=json_set(after_json,'$.fulfilled_micros',999000000) WHERE batch_id IN (SELECT batch_id FROM import_batches WHERE committed_at > '2026-07-27T04:00:00+00:00')")
    assert predict(history,week=8)==before
    with sqlite3.connect(db) as con:
        con.execute("UPDATE import_batches SET committed_at='2027-01-01T00:00:00+00:00'")
    # Coverage is also learned late; never label it known-complete at an earlier origin.
    late={d:datetime(2027,1,1,tzinfo=timezone.utc) for d in c}
    assert predict((db,late,m))['items'][0]['status']=='insufficient_history'

def test_menu_known_time_zero_day_and_units(history):
    db,c,m=history
    new=MenuItem('new-item','kg',START,datetime(2026,5,31,tzinfo=timezone.utc))
    p=predict((db,c,[new]))['items'][0]
    assert p['forecast_micros']==0 and p['quantity_unit']=='kg'
    future=MenuItem('new-item','each',START,datetime(2027,1,1,tzinfo=timezone.utc))
    assert predict((db,c,[future]))['items'][0]['status']=='insufficient_history'

def test_validation(history):
    with pytest.raises(ValueError):predict(history,minimum=5)
    db,c,m=history
    with pytest.raises(ValueError):predict((db,{START:datetime(2026,6,1,tzinfo=timezone.utc)},m))
    with pytest.raises(ValueError):predict((db,c,m+m))
    with pytest.raises(ValueError):forecast(CONFIG,target=START,as_of=datetime(2026,6,2,tzinfo=timezone.utc),coverage=c,menu=m,db_path=db)

def test_missing_actual_is_skipped(history):
    db,c,m=history;target=START+timedelta(weeks=8);del c[target]
    b=backtest(CONFIG,targets=[target],evaluation_as_of=datetime(2026,9,1,tzinfo=timezone.utc),coverage=c,menu=m,db_path=db)
    assert all(x['scored']==0 and x['skipped']==1 and x['mae_units'] is None for x in b['metrics'])

def test_unknown_location_and_naive_cutoff_rejected(history):
    from restaurant_lab.imports import LocationConfig, ImportRejected
    db,c,m=history;target=START+timedelta(weeks=12)
    with pytest.raises(ImportRejected):
        forecast(LocationConfig('unknown','demo','UTC','USD',4),target=target,as_of=datetime(2026,8,24,4,tzinfo=timezone.utc),coverage=c,menu=m,db_path=db)
    with pytest.raises(ValueError):
        forecast(CONFIG,target=target,as_of=datetime(2026,8,24,4),coverage=c,menu=m,db_path=db)


def test_future_correction_of_old_line_and_money_do_not_leak(history):
    import json
    db,c,m=history;before=predict(history,week=8)
    with sqlite3.connect(db) as con:
        old=json.loads(con.execute("SELECT after_json FROM line_history ORDER BY rowid LIMIT 1").fetchone()[0])
        batch=con.execute("SELECT batch_id FROM import_batches ORDER BY committed_at DESC LIMIT 1").fetchone()[0]
        old.update(fulfilled_micros=999000000,source_updated_at='2026-08-23T12:00:00+00:00')
        con.execute('INSERT INTO line_history VALUES (?,?,?,?,?,?,?)',(batch,CONFIG.source,CONFIG.location_id,old['order_id'],old['line_id'],None,json.dumps(old)))
        con.execute("UPDATE canonical_lines SET gross_minor=999999,refund_minor=999998,discount_minor=0")
    assert predict(history,week=8)==before
