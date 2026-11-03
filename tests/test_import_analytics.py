import csv
from datetime import date
import io
from pathlib import Path
import sqlite3

import unittest
from tempfile import TemporaryDirectory
from restaurant_lab.imports import LocationConfig, ImportRejected, preview_csv, commit_preview
from restaurant_lab.import_analytics import available_locations, dashboard

FIXTURE = Path(__file__).parent / 'fixtures/canonical_v1/valid.csv'
CONFIG = LocationConfig('synthetic_demo','demo_location','America/Los_Angeles','USD',4)
DAY = date(2026,9,30)


def changed(**values):
    rows = list(csv.DictReader(io.StringIO(FIXTURE.read_text())))
    for row in rows:
        row.update(values)
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=rows[0].keys())
    writer.writeheader(); writer.writerows(rows)
    return out.getvalue().encode()


def ingest(db, raw=None, config=CONFIG):
    return commit_preview(preview_csv(raw or FIXTURE.read_bytes(), config, db), confirmed=True)


def read(db, config=CONFIG, **kwargs):
    return dashboard(config, start=kwargs.get('start',DAY), end=kwargs.get('end',DAY), db_path=db)


def test_committed_fixture_reconciles_and_reimports(tmp_path):
    db=tmp_path/'orders.sqlite'
    imported=ingest(db)
    before=db.read_bytes()
    result=read(db)
    assert result['totals']['net_minor']==imported['reconciliation']['net_minor']==3100
    assert result['order_count']==1 and result['line_count']==2
    assert result['items'][0]['quantity_micros']==4000000
    assert sum(map(sum,result['rush_orders']))==1
    assert result['rush_orders'][3][1]==1  # actual Thursday, prior Wednesday business date
    assert result['observed_business_dates']==['2026-09-30']
    assert db.read_bytes()==before
    assert available_locations(db)==[CONFIG]
    ingest(db)
    assert read(db)==result


def test_rejected_import_does_not_change_dashboard(tmp_path):
    db=tmp_path/'orders.sqlite';ingest(db);before=read(db)
    with unittest.TestCase().assertRaises(ImportRejected): ingest(db,changed(quantity='-1'))
    assert read(db)==before


def test_locations_and_currency_never_mix(tmp_path):
    db=tmp_path/'orders.sqlite';ingest(db)
    other=LocationConfig('other','branch','America/Los_Angeles','JPY',4)
    ingest(db,changed(source='other',location_id='branch',currency='JPY',gross_amount='20',discount_amount='2',refund_amount='0'),other)
    assert read(db)['totals']['net_minor']==3100
    assert read(db,other)['totals']['net_minor']==36
    assert read(db,other)['currency']=='JPY'
    assert len(available_locations(db))==2


def test_void_preserves_fulfillment_and_zero_financials(tmp_path):
    db=tmp_path/'orders.sqlite';ingest(db)
    ingest(db,changed(status='voided',refund_amount='0',source_updated_at='2026-10-02T10:00:00Z'))
    result=read(db)
    assert result['totals']['net_minor']==0 and result['order_count']==0
    assert result['fulfilled_micros_by_unit']=={'each':4000000}
    assert sum(map(sum,result['rush_orders']))==0


def test_units_separate_and_latest_snapshot_not_double_counted(tmp_path):
    db=tmp_path/'orders.sqlite';ingest(db)
    ingest(db,changed(quantity_unit='kg',quantity='0.5',fulfilled_quantity='0.5',source_updated_at='2026-10-02T10:00:00Z'))
    result=read(db)
    assert result['quantity_micros_by_unit']=={'kg':1000000}
    assert result['totals']['net_minor']==3100 and result['line_count']==2


def test_empty_dates_missing_db_wrong_db_and_configuration(tmp_path):
    db=tmp_path/'orders.sqlite'
    assert available_locations(db)==[] and not db.exists()
    with unittest.TestCase().assertRaises(sqlite3.OperationalError): read(db)
    assert not db.exists()
    ingest(db)
    result=read(db,start=date(2020,1,1),end=date(2020,1,2))
    assert result['order_count']==0 and result['observed_business_dates']==[]
    with unittest.TestCase().assertRaises(ValueError): read(db,start=date(2027,1,1))
    with unittest.TestCase().assertRaises(ImportRejected): read(db,LocationConfig('synthetic_demo','demo_location','UTC','USD',4))
    with unittest.TestCase().assertRaises(ImportRejected): read(db,LocationConfig('unknown','unknown','UTC','USD',4))
    foreign=tmp_path/'foreign.sqlite'
    with sqlite3.connect(foreign) as con: con.execute('CREATE TABLE untouched (id INTEGER)')
    before=foreign.read_bytes()
    with unittest.TestCase().assertRaises(ImportRejected): available_locations(foreign)
    assert foreign.read_bytes()==before


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for name, test in list(globals().items()):
        if name.startswith('test_') and callable(test):
            def run(test=test):
                with TemporaryDirectory() as directory:
                    test(Path(directory))
            suite.addTest(unittest.FunctionTestCase(run, description=name))
    return suite
