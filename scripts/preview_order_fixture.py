"""Read-only walkthrough for the synthetic canonical fixture. No commit or server."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from restaurant_lab.imports import LocationConfig, preview_csv

if __name__ == '__main__':
    config = LocationConfig('synthetic_demo','demo_location','America/Los_Angeles','USD',4)
    preview = preview_csv((ROOT/'tests/fixtures/canonical_v1/valid.csv').read_bytes(), config)
    print('SYNTHETIC canonical v1 fixture — NOT a vendor export; preview only, nothing saved.')
    print(json.dumps({'can_commit':preview.can_commit,
                      'errors':[{'row':e.row,'message':e.message} for e in preview.errors],
                      'summary':preview.summary,'changes':preview.changes}, indent=2))
    raise SystemExit(0 if preview.can_commit else 1)
