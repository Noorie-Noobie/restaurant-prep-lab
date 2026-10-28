import hashlib
import sqlite3
import pandas as pd
import pytest
from restaurant_lab.config import RAW_PATH, ROOT
from restaurant_lab.data import normalize_orders, build_database, load_orders
from restaurant_lab.analytics import bestsellers, rush_hours, planning_menu
from restaurant_lab.meta import extract_image, validate_extraction
from streamlit.testing.v1 import AppTest

@pytest.fixture
def raw():
    # Intentionally identical business rows: two pizzas in one order, not a duplicate.
    return pd.DataFrame([
        dict(rownames=1,id='o1',date='2015-01-01',time='12:30:00',name='pizza',size='M',type='classic',price=13.25),
        dict(rownames=2,id='o1',date='2015-01-01',time='12:30:00',name='pizza',size='M',type='classic',price=13.25),
    ])

def test_repeated_items_are_preserved(raw):
    lines = normalize_orders(raw)
    lines['ordered_at'] = pd.to_datetime(lines.ordered_at)
    assert bestsellers(lines).iloc[0].units == 2
    assert bestsellers(lines).iloc[0].revenue_usd == 26.50
    assert rush_hours(lines).to_numpy().sum() == 1
    assert lines.timezone.unique().tolist() == ['unspecified_local']

def test_duplicate_source_key_rejected(raw):
    raw.loc[1,'rownames'] = 1
    with pytest.raises(ValueError, match='Duplicate'):
        normalize_orders(raw)

def test_invalid_data_rejected(raw):
    raw.loc[0,'price'] = -1
    with pytest.raises(ValueError, match='price'):
        normalize_orders(raw)

def test_ingest_full_source(tmp_path):
    expected = '243425c7184d31b35b09ae72c468154b1fb3434ec5d4f5cd32c8beb89d1b8801'
    assert hashlib.sha256(RAW_PATH.read_bytes()).hexdigest() == expected
    db = tmp_path/'restaurant.sqlite'
    metadata = build_database(RAW_PATH, db)
    orders = load_orders(db)
    assert len(orders) == 49574
    assert orders.order_id.nunique() == 21350
    assert orders.item_id.nunique() == 91
    assert orders.unit_price_cents.sum() == 81786005
    assert orders.ordered_at.dt.date.nunique() == 358
    assert rush_hours(orders).to_numpy().sum() == 21350
    assert len(planning_menu(orders)) == 7
    assert metadata['sha256'] == expected
    with sqlite3.connect(db) as con:
        assert con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'

def test_live_calls_disabled(monkeypatch):
    monkeypatch.delenv('META_LIVE_ENABLED', raising=False)
    monkeypatch.setattr('requests.post', lambda *a,**k: pytest.fail('Network called'))
    with pytest.raises(RuntimeError, match='disabled'):
        extract_image(b'fixture', 'image/png')

def test_invalid_extraction_rejected():
    row = {'ingredient':'tomatoes','quantity':-2,'unit':'kg','total_cost_usd':3,
           'source_quote':'Tomatoes -2kg','source_location':'row 1'}
    with pytest.raises(ValueError): validate_extraction({'ingredients':[row]})

def test_app_screens():
    app = AppTest.from_file(ROOT / 'app.py').run(timeout=30)
    assert not app.exception
    assert app.metric[0].value == '21,350'
    for page in ['Prep Planner','Meta Evidence']:
        app.sidebar.radio[0].set_value(page).run(timeout=30)
        assert not app.exception

def test_data_download_rejects_modified_source(tmp_path):
    import runpy
    downloader = runpy.run_path(str(ROOT / 'scripts/download_data.py'))
    modified = tmp_path / 'modified.csv'
    modified.write_text('explicit test fixture, not source data')
    with pytest.raises(ValueError, match='checksum mismatch'):
        downloader['verify'](modified)
    assert modified.read_text() == 'explicit test fixture, not source data'


def test_data_download_existing_file_is_offline(monkeypatch):
    import runpy
    import urllib.request
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **k: pytest.fail('Unneeded download'))
    downloader = runpy.run_path(str(ROOT / 'scripts/download_data.py'))
    downloader['main']()
