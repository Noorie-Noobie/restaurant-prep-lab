"""Rebuildable local storage; never edits the downloaded CSV."""
import hashlib
import json
import sqlite3
from pathlib import Path
import pandas as pd
from .config import RAW_PATH, DB_PATH, SOURCE_TIMEZONE

SCHEMA = """
CREATE TABLE order_lines (
 line_id TEXT PRIMARY KEY, order_id TEXT NOT NULL, ordered_at TEXT NOT NULL,
 timezone TEXT NOT NULL, item_id TEXT NOT NULL, item_name TEXT NOT NULL,
 size TEXT NOT NULL, category TEXT NOT NULL,
 quantity INTEGER NOT NULL CHECK(quantity > 0),
 unit_price_cents INTEGER NOT NULL CHECK(unit_price_cents >= 0),
 status TEXT NOT NULL, status_basis TEXT NOT NULL
);
CREATE INDEX order_time_idx ON order_lines(ordered_at);
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""

def normalize_orders(raw):
    required = {"rownames", "id", "date", "time", "name", "size", "type", "price"}
    if not required.issubset(raw.columns):
        raise ValueError(f"Missing columns: {sorted(required-set(raw.columns))}")
    if raw[list(required)].isna().any().any():
        raise ValueError("Source contains missing required values")
    if raw.rownames.duplicated().any():
        raise ValueError("Duplicate source row identifiers")
    dates = pd.to_datetime(raw.date.astype(str) + " " + raw.time.astype(str),
                           format="%Y-%m-%d %H:%M:%S", errors="raise")
    prices = pd.to_numeric(raw.price, errors="raise")
    if ((prices < 0) | ~prices.map(lambda x: float('-inf') < x < float('inf'))).any():
        raise ValueError("Invalid price")
    if ((prices*100 - (prices*100).round()).abs() > 0.0001).any():
        raise ValueError("Prices must have cent precision")
    result = pd.DataFrame({
        "line_id": "gt-" + raw.rownames.astype(str), "order_id": raw.id.astype(str),
        "ordered_at": dates.dt.strftime("%Y-%m-%dT%H:%M:%S"),
        "timezone": SOURCE_TIMEZONE,
        "item_id": raw.name.astype(str) + "__" + raw['size'].astype(str),
        "item_name": raw.name, "size": raw['size'], "category": raw.type,
        "quantity": 1, "unit_price_cents": (prices*100).round().astype(int),
        "status": "completed", "status_basis": "assumed_from_sales_dataset_no_status_field",
    })
    if result.groupby('order_id').ordered_at.nunique().gt(1).any():
        raise ValueError("An order has conflicting timestamps")
    return result

def build_database(raw_path=RAW_PATH, db_path=DB_PATH):
    raw_path, db_path = Path(raw_path), Path(db_path)
    frame = normalize_orders(pd.read_csv(raw_path, dtype={"id": str}))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # Build separately, then replace only the project's derived database.
    temp = db_path.with_suffix('.building.sqlite')
    if temp.exists():
        temp.unlink()
    try:
        with sqlite3.connect(temp) as con:
            con.executescript(SCHEMA)
            con.executemany('INSERT INTO order_lines VALUES (' + ','.join(['?']*12) + ')',
                            frame.itertuples(index=False, name=None))
            meta = {'source': 'gt::pizzaplace via Rdatasets', 'synthetic': 'true',
                    'sha256': hashlib.sha256(raw_path.read_bytes()).hexdigest(),
                    'timezone': SOURCE_TIMEZONE, 'rows': str(len(frame))}
            con.executemany('INSERT INTO metadata VALUES (?, ?)', meta.items())
        temp.replace(db_path)
    finally:
        if temp.exists(): temp.unlink()
    return meta

def load_orders(db_path=DB_PATH):
    with sqlite3.connect(f"file:{Path(db_path)}?mode=ro", uri=True) as con:
        return pd.read_sql_query('SELECT * FROM order_lines', con, parse_dates=['ordered_at'])

if __name__ == '__main__':
    print(json.dumps(build_database(), indent=2))
