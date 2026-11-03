"""Synthetic import -> committed temporary DB -> dashboard JSON and HTML bars.

No existing DB touched; no network, server or app UI changes. Temporary DB removed.
"""
from datetime import date
from html import escape
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from restaurant_lab.imports import LocationConfig, preview_csv, commit_preview
from restaurant_lab.import_analytics import dashboard

root = Path(__file__).resolve().parents[1]
config = LocationConfig('synthetic_demo', 'demo_location', 'America/Los_Angeles', 'USD', 4)
with TemporaryDirectory() as temp:
    db = Path(temp) / 'demo.sqlite'
    candidate = preview_csv((root / 'tests/fixtures/canonical_v1/valid.csv').read_bytes(), config, db)
    commit_preview(candidate, confirmed=True)  # explicitly synthetic, disposable demo only
    result = dashboard(config, start=date(2026, 9, 30), end=date(2026, 9, 30), db_path=db)
    print(json.dumps(result, indent=2))
    # Optional output requires an explicit destination and refuses to overwrite.
    if len(sys.argv) == 2:
        bars = ''.join(f'<p>{escape(r["item_id"])} — {r["net_minor"]} USD cents</p>'
                      f'<meter min="0" max="{max(1,result["totals"]["net_minor"])}" value="{r["net_minor"]}"></meter>' for r in result['items'])
        with open(sys.argv[1], 'x') as out:
            out.write('<!doctype html><meta charset="utf-8"><title>Synthetic imported order demo</title>'
                      '<style>body{font:18px system-ui;max-width:900px;margin:40px auto}meter{width:100%;height:35px}</style>'
                      '<h1>Synthetic imported orders</h1><p>Not real restaurant results. Temporary database removed after this run.</p>'
                      '<p>1 completed order • 4 fulfilled items • USD 31.00 net. Refunds do not reverse fulfillment.</p>' + bars +
                      '<h2>Rush count</h2><p>Thursday 01:00: 1 order (America/Los_Angeles); business date Wednesday September 30, cutoff 04:00.</p>')
