"""Synthetic contract cases only. These are NOT Toast or Square exports."""
import csv
import io
from pathlib import Path
import sqlite3

import pytest

from restaurant_lab.imports import (
    FIELDS, LocationConfig, ImportRejected, StalePreview, preview_csv, commit_preview,
)

FIXTURES = Path(__file__).parent / 'fixtures/canonical_v1'
CONFIG = LocationConfig('synthetic_demo', 'demo_location', 'America/Los_Angeles', 'USD', 4)


def row(**overrides):
    value = dict(schema_version='1', source='synthetic_demo', location_id='demo_location',
                 order_id='0001', line_id='line-001', item_id='sandwich-regular', item_name='Demo sandwich',
                 ordered_at='2026-10-01T01:30:00-07:00', source_updated_at='2026-10-01T10:00:00Z',
                 timezone='America/Los_Angeles', business_date='2026-09-30', currency='USD',
                 quantity_unit='each', quantity='2', fulfilled_quantity='2', status='completed',
                 gross_amount='20.00', discount_amount='2.00', refund_amount='0.00')
    value.update(overrides)
    return value


def csv_bytes(*rows, fields=FIELDS):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def commit(raw, db, config=CONFIG):
    preview = preview_csv(raw, config, db)
    assert preview.can_commit, preview.errors
    return commit_preview(preview, confirmed=True)


def snapshot(db):
    with sqlite3.connect(db) as con:
        return {table: con.execute(f'SELECT * FROM {table}').fetchall()
                for table in ('canonical_lines','import_batches','line_history','import_meta','locations')}


def test_preview_is_read_only_and_confirmation_required(tmp_path):
    db = tmp_path/'orders.sqlite'
    p = preview_csv(csv_bytes(row()), CONFIG, db)
    assert p.can_commit and p.summary['net_minor'] == 1800
    assert not db.exists()
    with pytest.raises(ImportRejected, match='confirmation'):
        commit_preview(p)
    assert not db.exists()


def test_identical_items_with_distinct_line_ids_retained(tmp_path):
    raw = csv_bytes(row(), row(line_id='line-002'))
    result = commit(raw, tmp_path/'orders.sqlite')
    assert result['reconciliation']['order_count'] == 1
    assert result['reconciliation']['line_count'] == 2
    assert result['reconciliation']['quantity_by_unit'] == {'each':'4'}
    assert result['reconciliation']['net_minor'] == 3600


def test_exact_reimport_has_no_mutation(tmp_path):
    db = tmp_path/'orders.sqlite'
    raw = csv_bytes(row())
    commit(raw, db)
    before = snapshot(db)
    p = preview_csv(raw, CONFIG, db)
    assert p.changes == {'inserted':0,'updated':0,'unchanged':1}
    result = commit_preview(p, confirmed=True)
    assert result['already_imported']
    assert snapshot(db) == before


def test_overlapping_import_and_refund_snapshot_update(tmp_path):
    db = tmp_path/'orders.sqlite'
    commit(csv_bytes(row(), row(line_id='line-002')), db)
    result = commit(csv_bytes(row(line_id='line-002'), row(line_id='line-003')), db)
    assert result['changes'] == {'inserted':1,'updated':0,'unchanged':1}
    assert result['reconciliation']['line_count'] == 3
    refund = csv_bytes(row(refund_amount='5.00', source_updated_at='2026-10-02T10:00:00Z'))
    result = commit(refund, db)
    assert result['reconciliation']['net_minor'] == 4900
    assert result['reconciliation']['refund_minor'] == 500
    assert result['reconciliation']['fulfilled_by_unit'] == {'each':'6'}
    again = commit(refund, db)
    assert again['reconciliation']['net_minor'] == 4900
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT count(*) FROM line_history').fetchone()[0] == 4


def test_void_does_not_double_subtract_or_undo_prepared_food(tmp_path):
    result = commit(csv_bytes(row(status='voided', fulfilled_quantity='1')),
                    tmp_path/'orders.sqlite')
    summary = result['reconciliation']
    assert summary['net_minor'] == 0 and summary['gross_minor'] == 0
    assert summary['voided_lines'] == 1 and summary['quantity_by_unit'] == {}
    assert summary['fulfilled_by_unit'] == {'each':'1'}
    bad = preview_csv(csv_bytes(row(status='voided', refund_amount='1')), CONFIG, tmp_path/'other.sqlite')
    assert not bad.can_commit


@pytest.mark.parametrize('change', [
    {'quantity':'NaN'}, {'quantity':'1e2'}, {'quantity':'-1'}, {'quantity':'0'},
    {'quantity':'1.0000001'}, {'fulfilled_quantity':'3'}, {'gross_amount':'10.001'},
    {'discount_amount':'21'}, {'refund_amount':'19'}, {'currency':'CAD'},
    {'status':'open'}, {'business_date':'2026-10-01'}, {'business_date':'20260930'},
    {'ordered_at':'2026-10-01T01:30:00'}, {'ordered_at':'2026-10-01T01:30:00-08:00'},
    {'source_updated_at':'2026-10-01T00:00:00Z'}, {'schema_version':'2'},
    {'line_id':''}, {'quantity_unit':'unknown'}, {'item_name':'bad\nname'},
])
def test_invalid_rows_leave_existing_database_unchanged(tmp_path, change):
    db = tmp_path/'orders.sqlite'
    commit(csv_bytes(row()), db)
    before = snapshot(db)
    p = preview_csv(csv_bytes(row(line_id='new-line'), row(**{'line_id':'bad-line', **change})), CONFIG, db)
    assert not p.can_commit and p.errors
    with pytest.raises(ImportRejected): commit_preview(p, confirmed=True)
    assert snapshot(db) == before


def test_duplicate_identity_in_file_is_rejected(tmp_path):
    p = preview_csv(csv_bytes(row(),row()), CONFIG, tmp_path/'orders.sqlite')
    assert not p.can_commit and 'Duplicate' in p.errors[0].message


@pytest.mark.parametrize('raw', [b'', b'wrong,columns\n1,2\n', b'\xff', b'a\0b'])
def test_bad_file_format_is_rejected_without_database(tmp_path, raw):
    db = tmp_path/'orders.sqlite'
    assert not preview_csv(raw,CONFIG,db).can_commit
    assert not db.exists()


def test_extra_pii_column_rejected(tmp_path):
    p = preview_csv(csv_bytes(row(customer_email='do-not-import@example.invalid'),
                             fields=FIELDS+('customer_email',)), CONFIG, tmp_path/'orders.sqlite')
    assert not p.can_commit
    assert all('example.invalid' not in issue.message for issue in p.errors)


def test_stale_preview_after_other_commit_requires_reconfirmation(tmp_path):
    db = tmp_path/'orders.sqlite'
    commit(csv_bytes(row()), db)
    pending = preview_csv(csv_bytes(row(line_id='line-002')), CONFIG, db)
    commit(csv_bytes(row(line_id='line-003')), db)
    before = snapshot(db)
    with pytest.raises(StalePreview): commit_preview(pending, confirmed=True)
    assert snapshot(db) == before


def test_two_previews_before_first_import_do_not_overwrite(tmp_path):
    db = tmp_path/'orders.sqlite'
    p1 = preview_csv(csv_bytes(row()), CONFIG, db)
    p2 = preview_csv(csv_bytes(row(line_id='line-002')), CONFIG, db)
    commit_preview(p1, confirmed=True)
    with pytest.raises(StalePreview): commit_preview(p2, confirmed=True)


def test_older_or_equal_conflicting_versions_rejected(tmp_path):
    db = tmp_path/'orders.sqlite'
    commit(csv_bytes(row(source_updated_at='2026-10-03T10:00:00Z')), db)
    for updated in ('2026-10-01T10:00:00Z','2026-10-03T10:00:00Z'):
        p = preview_csv(csv_bytes(row(refund_amount='1',source_updated_at=updated)),CONFIG,db)
        assert not p.can_commit


def test_runtime_failure_rolls_back_lines_audit_and_revision(tmp_path):
    db = tmp_path/'orders.sqlite'
    commit(csv_bytes(row()),db)
    with sqlite3.connect(db) as con:
        con.execute("CREATE TRIGGER test_failure BEFORE INSERT ON canonical_lines WHEN NEW.line_id='fail' BEGIN SELECT RAISE(ABORT,'test failure'); END")
    p = preview_csv(csv_bytes(row(line_id='first'),row(line_id='fail')),CONFIG,db)
    before = snapshot(db)
    with pytest.raises(sqlite3.IntegrityError): commit_preview(p,confirmed=True)
    assert snapshot(db) == before


def test_operational_table_preserved_and_other_database_rejected(tmp_path):
    db = tmp_path/'orders.sqlite'
    commit(csv_bytes(row()),db)
    with sqlite3.connect(db) as con:
        con.execute('CREATE TABLE inventory (id INTEGER PRIMARY KEY, amount INTEGER)')
        con.execute('INSERT INTO inventory VALUES(1,99)')
    commit(csv_bytes(row(line_id='line-002')), db)
    with sqlite3.connect(db) as con:
        assert con.execute('SELECT amount FROM inventory').fetchone()[0] == 99
    other = tmp_path/'pizza.sqlite'
    with sqlite3.connect(other) as con: con.execute('CREATE TABLE order_lines (id TEXT)')
    assert not preview_csv(csv_bytes(row()),CONFIG,other).can_commit


def test_config_change_rejected_and_location_ids_isolated(tmp_path):
    db = tmp_path/'orders.sqlite'
    commit(csv_bytes(row()), db)
    wrong = LocationConfig('synthetic_demo','demo_location','America/Los_Angeles','USD',0)
    assert not preview_csv(csv_bytes(row(business_date='2026-10-01')),wrong,db).can_commit
    second = LocationConfig('synthetic_demo','second_location','America/Los_Angeles','USD',4)
    commit(csv_bytes(row(location_id='second_location')),db,second)
    with sqlite3.connect(db) as con: assert con.execute('SELECT count(*) FROM canonical_lines').fetchone()[0] == 2


@pytest.mark.parametrize('currency,amount,expected', [('JPY','100',100),('KWD','1.234',1234),('CAD','12.34',1234)])
def test_currency_minor_units_and_fractional_quantities(tmp_path,currency,amount,expected):
    cfg=LocationConfig('synthetic_demo','demo_location','UTC',currency,0)
    r=row(currency=currency,timezone='UTC',ordered_at='2026-10-01T01:30:00Z',business_date='2026-10-01',
          quantity_unit='kg',quantity='1.250001',fulfilled_quantity='1.25',gross_amount=amount,discount_amount='0')
    result=commit(csv_bytes(r),tmp_path/'orders.sqlite',cfg)
    assert result['reconciliation']['net_minor']==expected
    assert result['reconciliation']['quantity_by_unit']=={'kg':'1.250001'}


def test_dst_fold_offsets_and_nonexistent_wall_time(tmp_path):
    rows=[row(order_id='fall1',line_id='f1',ordered_at='2026-11-01T01:30:00-07:00',
              source_updated_at='2026-11-02T00:00:00Z',business_date='2026-10-31'),
          row(order_id='fall2',line_id='f2',ordered_at='2026-11-01T01:30:00-08:00',
              source_updated_at='2026-11-02T00:00:00Z',business_date='2026-10-31')]
    p=preview_csv(csv_bytes(*rows),CONFIG,tmp_path/'orders.sqlite')
    assert p.can_commit and p.rows[0]['ordered_at'] != p.rows[1]['ordered_at']
    invalid=row(ordered_at='2026-03-08T02:30:00-08:00',source_updated_at='2026-03-09T00:00:00Z',business_date='2026-03-07')
    assert not preview_csv(csv_bytes(invalid),CONFIG,tmp_path/'orders.sqlite').can_commit


def test_order_consistency_across_imports(tmp_path):
    db=tmp_path/'orders.sqlite'
    commit(csv_bytes(row()),db)
    other=row(line_id='line-002',ordered_at='2026-10-01T02:30:00-07:00')
    assert not preview_csv(csv_bytes(other),CONFIG,db).can_commit


def test_mutating_preview_display_cannot_change_saved_values(tmp_path):
    db=tmp_path/'orders.sqlite'
    p=preview_csv(csv_bytes(row()),CONFIG,db)
    p.rows[0]['gross_minor']=999999
    p.summary['net_minor']=999999
    result=commit_preview(p,confirmed=True)
    assert result['reconciliation']['net_minor']==1800


def test_checked_in_synthetic_fixtures(tmp_path):
    good=preview_csv((FIXTURES/'valid.csv').read_bytes(),CONFIG,tmp_path/'orders.sqlite')
    assert good.can_commit and good.summary['net_minor']==3100
    for name in ('invalid_duplicate.csv','invalid_values.csv','malformed.csv'):
        assert not preview_csv((FIXTURES/name).read_bytes(),CONFIG,tmp_path/'orders.sqlite').can_commit


def test_failed_first_transaction_is_retryable(tmp_path, monkeypatch):
    import restaurant_lab.imports as imports
    db = tmp_path/'orders.sqlite'
    real_initialize = imports._initialize
    def failing_initialize(con):
        real_initialize(con)
        raise RuntimeError('synthetic initialization failure')
    p = preview_csv(csv_bytes(row()),CONFIG,db)
    monkeypatch.setattr(imports,'_initialize',failing_initialize)
    with pytest.raises(RuntimeError): commit_preview(p,confirmed=True)
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == []
    monkeypatch.setattr(imports,'_initialize',real_initialize)
    assert commit(csv_bytes(row()),db)['reconciliation']['net_minor']==1800


def test_refund_then_void_correction_counts_reversal_once(tmp_path):
    db=tmp_path/'orders.sqlite'
    commit(csv_bytes(row(refund_amount='5.00')),db)
    result=commit(csv_bytes(row(status='voided',refund_amount='0',source_updated_at='2026-10-03T10:00:00Z')),db)
    assert result['reconciliation']['net_minor']==0
    assert result['reconciliation']['refund_minor']==0
    assert result['reconciliation']['fulfilled_by_unit']=={'each':'2'}


def test_quantity_totals_do_not_mix_units(tmp_path):
    result=commit(csv_bytes(row(),row(line_id='weighted',quantity_unit='kg',quantity='1.5',fulfilled_quantity='1.25')), tmp_path/'orders.sqlite')
    assert result['reconciliation']['quantity_by_unit']=={'each':'2','kg':'1.5'}


def test_renamed_item_keeps_stable_identity(tmp_path):
    db=tmp_path/'orders.sqlite'
    commit(csv_bytes(row()),db)
    result=commit(csv_bytes(row(item_name='New demo name',source_updated_at='2026-10-03T10:00:00Z')),db)
    assert result['changes']['updated']==1 and result['reconciliation']['line_count']==1
