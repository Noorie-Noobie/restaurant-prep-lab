"""Canonical CSV v1: explicit snapshots, read-only preview, transactional commit.

Not a vendor adapter. See docs/ORDER_IMPORT_V1.md before mapping any POS export.
The dedicated database never replaces the pizza demo or operational stock tables.
"""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import re
import sqlite3
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .config import ROOT

DEFAULT_DB = ROOT / 'data/processed/canonical_orders.sqlite'
VERSION = '1'
APP_ID = 1380994097
MAX_BYTES = 10 * 1024 * 1024
MAX_ROWS = 50000
QUANTITY_SCALE = 1_000_000
CURRENCY_DIGITS = {'USD': 2, 'CAD': 2, 'EUR': 2, 'GBP': 2, 'JPY': 0, 'KWD': 3}
FIELDS = (
    'schema_version', 'source', 'location_id', 'order_id', 'line_id', 'item_id',
    'item_name', 'ordered_at', 'source_updated_at', 'timezone', 'business_date',
    'currency', 'quantity_unit', 'quantity', 'fulfilled_quantity', 'status',
    'gross_amount', 'discount_amount', 'refund_amount',
)
ID_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z')
DECIMAL_RE = re.compile(r'(?:0|[1-9][0-9]{0,12})(?:\.[0-9]{1,6})?\Z')
TIME_RE = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})\Z')


class ImportRejected(ValueError):
    """A file, database or confirmation failed the import contract."""


class StalePreview(ImportRejected):
    """Database changed since preview; generate a new preview and confirm again."""


@dataclass(frozen=True)
class LocationConfig:
    source: str
    location_id: str
    timezone: str
    currency: str
    business_day_start_hour: int

    def validate(self):
        if not all(ID_RE.fullmatch(v) for v in (self.source, self.location_id)):
            raise ImportRejected('Source/location IDs must be stable nonempty identifiers')
        if self.currency not in CURRENCY_DIGITS:
            raise ImportRejected('Unsupported currency; use one explicitly listed in contract v1')
        if type(self.business_day_start_hour) is not int or not 0 <= self.business_day_start_hour <= 23:
            raise ImportRejected('Business day start hour must be an integer from 0 to 23')
        try:
            ZoneInfo(self.timezone)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ImportRejected('Timezone must be a known IANA timezone') from exc


@dataclass(frozen=True)
class Issue:
    row: int | None  # CSV logical record, header is 1
    message: str


@dataclass(frozen=True)
class Preview:
    # Retain immutable original bytes in server-side session state, not editable UI values.
    raw: bytes
    config: LocationConfig
    db_path: Path
    revision: int
    database_id: str | None
    batch_id: str
    errors: tuple[Issue, ...]
    rows: tuple[dict, ...]
    summary: dict
    changes: dict

    @property
    def can_commit(self):
        return not self.errors


DDL = (
    'CREATE TABLE import_meta (singleton INTEGER PRIMARY KEY CHECK(singleton=1), revision INTEGER NOT NULL, database_id TEXT NOT NULL)',
    'CREATE TABLE locations (source TEXT NOT NULL, location_id TEXT NOT NULL, config_json TEXT NOT NULL, PRIMARY KEY(source,location_id))',
    '''CREATE TABLE canonical_lines (
      source TEXT NOT NULL, location_id TEXT NOT NULL, order_id TEXT NOT NULL,
      line_id TEXT NOT NULL, item_id TEXT NOT NULL, item_name TEXT NOT NULL,
      ordered_at TEXT NOT NULL, source_updated_at TEXT NOT NULL,
      timezone TEXT NOT NULL, business_date TEXT NOT NULL, currency TEXT NOT NULL,
      quantity_unit TEXT NOT NULL, quantity_micros INTEGER NOT NULL CHECK(quantity_micros>0),
      fulfilled_micros INTEGER NOT NULL CHECK(fulfilled_micros>=0 AND fulfilled_micros<=quantity_micros),
      status TEXT NOT NULL CHECK(status IN ('completed','voided')),
      gross_minor INTEGER NOT NULL CHECK(gross_minor>=0),
      discount_minor INTEGER NOT NULL CHECK(discount_minor>=0 AND discount_minor<=gross_minor),
      refund_minor INTEGER NOT NULL CHECK(refund_minor>=0 AND refund_minor<=gross_minor-discount_minor),
      PRIMARY KEY(source,location_id,order_id,line_id))''',
    '''CREATE TABLE import_batches (
      batch_id TEXT PRIMARY KEY, file_sha256 TEXT NOT NULL, config_json TEXT NOT NULL,
      committed_at TEXT NOT NULL, row_count INTEGER NOT NULL, changes_json TEXT NOT NULL,
      reconciliation_json TEXT NOT NULL)''',
    '''CREATE TABLE line_history (
      batch_id TEXT NOT NULL REFERENCES import_batches(batch_id),
      source TEXT NOT NULL, location_id TEXT NOT NULL, order_id TEXT NOT NULL, line_id TEXT NOT NULL,
      before_json TEXT, after_json TEXT NOT NULL,
      PRIMARY KEY(batch_id,source,location_id,order_id,line_id))''',
    'CREATE INDEX canonical_date_idx ON canonical_lines(source,location_id,business_date)',
)
LINE_FIELDS = ('source','location_id','order_id','line_id','item_id','item_name',
               'ordered_at','source_updated_at','timezone','business_date','currency',
               'quantity_unit','quantity_micros','fulfilled_micros','status',
               'gross_minor','discount_minor','refund_minor')
KEY_FIELDS = LINE_FIELDS[:4]


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def _key(row):
    return tuple(row[k] for k in KEY_FIELDS)


def _timestamp(value, field):
    if not TIME_RE.fullmatch(value):
        raise ImportRejected(f'{field} requires ISO 8601 seconds and explicit offset or Z')
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ImportRejected(f'{field} is not a valid timestamp') from exc
    return parsed


def _scaled(value, digits, maximum, field):
    if not DECIMAL_RE.fullmatch(value):
        raise ImportRejected(f'{field} must be a nonnegative plain decimal, no separators or exponent')
    number = Decimal(value)
    scaled = number * (10 ** digits)
    if scaled != scaled.to_integral_value():
        raise ImportRejected(f'{field} exceeds supported decimal precision ({digits})')
    if scaled > maximum:
        raise ImportRejected(f'{field} exceeds contract limit')
    return int(scaled)


def _normalize(row, config):
    if row['schema_version'] != VERSION:
        raise ImportRejected('Unsupported schema_version')
    for field in ('source','location_id','order_id','line_id','item_id'):
        if not ID_RE.fullmatch(row[field]):
            raise ImportRejected(f'{field} must be a stable nonempty identifier')
    for field in ('source','location_id','timezone','currency'):
        if row[field] != getattr(config, field):
            raise ImportRejected(f'{field} differs from the explicitly selected location configuration')
    name = row['item_name']
    if not name or len(name) > 200 or any(ord(c) < 32 or ord(c) == 127 for c in name):
        raise ImportRejected('item_name must be 1–200 characters without control characters')
    ordered = _timestamp(row['ordered_at'], 'ordered_at')
    local = ordered.astimezone(ZoneInfo(config.timezone))
    # Reject ambiguous/nonexistent local wall time by requiring supplied offset to match zone.
    if ordered.utcoffset() != local.utcoffset():
        raise ImportRejected('ordered_at offset does not match timezone at that instant')
    updated = _timestamp(row['source_updated_at'], 'source_updated_at')
    if updated < ordered:
        raise ImportRejected('source_updated_at precedes ordered_at')
    try:
        business_date = date.fromisoformat(row['business_date'])
    except ValueError as exc:
        raise ImportRejected('business_date must be YYYY-MM-DD') from exc
    if business_date.isoformat() != row['business_date']:
        raise ImportRejected('business_date must be YYYY-MM-DD')
    expected_date = local.date() - timedelta(days=int(local.hour < config.business_day_start_hour))
    if business_date != expected_date:
        raise ImportRejected('business_date disagrees with timezone and configured cutoff')
    if row['quantity_unit'] not in {'each','kg','g','l','ml'}:
        raise ImportRejected('Unsupported quantity_unit')
    qty = _scaled(row['quantity'], 6, 10**12, 'quantity')
    fulfilled = _scaled(row['fulfilled_quantity'], 6, 10**12, 'fulfilled_quantity')
    if qty == 0 or fulfilled > qty:
        raise ImportRejected('Require quantity > 0 and 0 <= fulfilled_quantity <= quantity')
    if row['status'] not in {'completed','voided'}:
        raise ImportRejected('status must be completed or voided; open orders are unsupported')
    digits = CURRENCY_DIGITS[config.currency]
    gross, discount, refund = [
        _scaled(row[field], digits, 10**12, field)
        for field in ('gross_amount','discount_amount','refund_amount')
    ]
    if discount > gross or refund > gross - discount:
        raise ImportRejected('Require discount <= gross and refund <= gross - discount')
    if row['status'] == 'voided' and refund != 0:
        raise ImportRejected('Voided lines must have zero refund; do not represent the same reversal twice')
    out = {field: row[field] for field in LINE_FIELDS if field in row}
    out.update(ordered_at=ordered.astimezone(timezone.utc).isoformat(),
               source_updated_at=updated.astimezone(timezone.utc).isoformat(),
               quantity_micros=qty, fulfilled_micros=fulfilled,
               gross_minor=gross, discount_minor=discount, refund_minor=refund)
    return {field: out[field] for field in LINE_FIELDS}


def _parse(raw, config):
    config.validate()
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_BYTES:
        raise ImportRejected('CSV must be nonempty UTF-8 bytes, at most 10 MiB')
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise ImportRejected('CSV must be UTF-8 encoded') from exc
    if '\x00' in text:
        raise ImportRejected('CSV contains a null byte')
    reader = csv.DictReader(io.StringIO(text, newline=''), strict=True)
    errors, rows, seen, orders = [], [], set(), {}
    try:
        if reader.fieldnames is None or len(reader.fieldnames) != len(FIELDS) or set(reader.fieldnames) != set(FIELDS):
            raise ImportRejected('Headers must match canonical v1 exactly; duplicate, missing or extra columns rejected')
        for number, row in enumerate(reader, start=2):
            if number > MAX_ROWS + 1:
                raise ImportRejected('CSV exceeds 50,000 rows')
            try:
                if None in row or any(value is None for value in row.values()):
                    raise ImportRejected('Row has too many or too few fields')
                normalized = _normalize(row, config)
                key = _key(normalized)
                if key in seen:
                    raise ImportRejected('Duplicate line identity inside file; preserve distinct IDs for repeated items')
                seen.add(key)
                order_key = key[:3]
                order_value = tuple(normalized[f] for f in ('ordered_at','business_date','currency','timezone'))
                if order_key in orders and orders[order_key] != order_value:
                    raise ImportRejected('Conflicting order timestamp/business date/currency in file')
                orders[order_key] = order_value
                rows.append(normalized)
            except (ImportRejected, OverflowError) as exc:
                errors.append(Issue(number, str(exc)))
                if len(errors) >= 100:
                    errors.append(Issue(None, 'Stopped after 100 invalid rows; no import allowed'))
                    break
    except csv.Error as exc:
        errors.append(Issue(None, f'Malformed CSV: {exc}'))
    if not rows and not errors:
        errors.append(Issue(None, 'CSV contains no data rows'))
    return tuple(rows), tuple(errors)


def _summary(rows):
    result = {'line_count': len(rows), 'order_count': len({r['order_id'] for r in rows}),
              'completed_lines': 0, 'voided_lines': 0,
              'gross_minor': 0, 'discount_minor': 0, 'refund_minor': 0, 'net_minor': 0,
              'quantity_by_unit': {}, 'fulfilled_by_unit': {}}
    for row in rows:
        unit = row['quantity_unit']
        result['fulfilled_by_unit'][unit] = result['fulfilled_by_unit'].get(unit, 0) + row['fulfilled_micros']
        if row['status'] == 'voided':
            result['voided_lines'] += 1
            continue
        result['completed_lines'] += 1
        result['quantity_by_unit'][unit] = result['quantity_by_unit'].get(unit, 0) + row['quantity_micros']
        for field in ('gross_minor','discount_minor','refund_minor'):
            result[field] += row[field]
    result['net_minor'] = result['gross_minor'] - result['discount_minor'] - result['refund_minor']
    for field in ('quantity_by_unit','fulfilled_by_unit'):
        result[field] = {unit: format(Decimal(amount)/QUANTITY_SCALE, 'f') for unit, amount in result[field].items()}
    return result


def _state(con, config):
    app_id = con.execute('PRAGMA application_id').fetchone()[0]
    version = con.execute('PRAGMA user_version').fetchone()[0]
    if app_id == 0 and version == 0 and not con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
        return 0, None  # An interrupted first transaction may leave an empty SQLite file.
    if app_id != APP_ID or version != 1:
        raise ImportRejected('Not a canonical v1 database; refusing to modify another app/database')
    revision, database_id = con.execute('SELECT revision,database_id FROM import_meta WHERE singleton=1').fetchone()
    saved = con.execute('SELECT config_json FROM locations WHERE source=? AND location_id=?',
                        (config.source, config.location_id)).fetchone()
    if saved and saved[0] != _json(asdict(config)):
        raise ImportRejected('Location configuration changed; explicit migration is required')
    return revision, database_id


def _read_existing(con, config):
    con.row_factory = sqlite3.Row
    return {_key(dict(row)): dict(row) for row in con.execute(
        'SELECT * FROM canonical_lines WHERE source=? AND location_id=?',
        (config.source, config.location_id))}


def _changes(rows, existing):
    counts = {'inserted': 0, 'updated': 0, 'unchanged': 0}
    merged = dict(existing)
    for row in rows:
        old = existing.get(_key(row))
        if old == row:
            counts['unchanged'] += 1
        elif old:
            # Different snapshots require a strictly newer source version.
            if row['source_updated_at'] <= old['source_updated_at']:
                raise ImportRejected('Stale or conflicting source version; reconcile the source before importing')
            counts['updated'] += 1
        else:
            counts['inserted'] += 1
        merged[_key(row)] = row
    order_values = {}
    for key, row in merged.items():
        value = tuple(row[f] for f in ('ordered_at','business_date','currency','timezone'))
        if key[:3] in order_values and order_values[key[:3]] != value:
            raise ImportRejected('Order-level fields conflict with another stored line; supply consistent corrections')
        order_values[key[:3]] = value
    return counts, merged


def preview_csv(raw: bytes, config: LocationConfig, db_path=DEFAULT_DB) -> Preview:
    """No writes. Rejected rows block the whole file. Preview summary is NOT a sales delta."""
    path = Path(db_path).resolve()
    batch_id = hashlib.sha256(VERSION.encode() + b'\0' + _json(asdict(config)).encode() + b'\0' + raw).hexdigest()
    revision, database_id, rows, errors = 0, None, (), ()
    existing, changes = {}, {}
    try:
        rows, errors = _parse(raw, config)
        if path.exists():
            with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as con:
                con.execute('BEGIN')
                revision, database_id = _state(con, config)
                existing = _read_existing(con, config) if database_id is not None else {}
        if not errors:
            changes, _ = _changes(rows, existing)
    except (ImportRejected, sqlite3.Error) as exc:
        errors = errors + (Issue(None, str(exc)),)
    summary = _summary(rows)
    summary.update(currency=config.currency, scope='valid input snapshots only; not incremental sales',
                   valid_rows=len(rows), importable=not errors)
    return Preview(raw, config, path, revision, database_id, batch_id, errors, rows, summary, changes)


def _initialize(con):
    import uuid
    for statement in DDL:
        con.execute(statement)
    con.execute(f'PRAGMA application_id={APP_ID}')
    con.execute('PRAGMA user_version=1')
    con.execute('INSERT INTO import_meta VALUES (1,0,?)', (str(uuid.uuid4()),))


def commit_preview(preview: Preview, *, confirmed=False) -> dict:
    """Explicit local caller confirmation; not authentication. Transaction checks for stale preview.

    Use the SAME preview stored server-side; never accept arbitrary DB paths from UI users.
    """
    if confirmed is not True:
        raise ImportRejected('Explicit confirmation is required; nothing written')
    if not preview.can_commit:
        raise ImportRejected('Preview contains errors; nothing written')
    # Parse again from immutable source bytes; mutable display dictionaries are never trusted.
    fresh = preview_csv(preview.raw, preview.config, preview.db_path)
    if fresh.batch_id != preview.batch_id or fresh.errors:
        raise ImportRejected('Source/configuration no longer validates; preview again')
    preview.db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(preview.db_path, timeout=5, isolation_level=None)
    try:
        con.execute('PRAGMA foreign_keys=ON')
        con.execute('BEGIN IMMEDIATE')
        tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        if not tables:
            if preview.database_id is not None:
                raise StalePreview('Database was replaced; preview again')
            _initialize(con)
            revision, database_id = _state(con, preview.config)
        else:
            revision, database_id = _state(con, preview.config)
            if database_id != preview.database_id:
                raise StalePreview('Database changed since preview; preview again')
        if revision != preview.revision:
            raise StalePreview('Database changed since preview; preview again')
        existing = _read_existing(con, preview.config)
        audit = con.execute('SELECT changes_json,reconciliation_json FROM import_batches WHERE batch_id=?',
                            (preview.batch_id,)).fetchone()
        if audit:
            con.execute('ROLLBACK')
            return {'already_imported': True, 'batch_id': preview.batch_id,
                    'changes': {'inserted':0,'updated':0,'unchanged':len(fresh.rows)},
                    'reconciliation': {**_summary(tuple(existing.values())),
                                       'currency': preview.config.currency,
                                       'scope': 'current snapshots for this source/location'}}
        changes, merged = _changes(fresh.rows, existing)
        reconciliation = _summary(tuple(merged.values()))
        reconciliation.update(currency=preview.config.currency, scope='current snapshots for this source/location')
        con.execute('INSERT OR IGNORE INTO locations VALUES (?,?,?)',
                    (preview.config.source, preview.config.location_id, _json(asdict(preview.config))))
        con.execute('INSERT INTO import_batches VALUES (?,?,?,?,?,?,?)',
                    (preview.batch_id, hashlib.sha256(preview.raw).hexdigest(), _json(asdict(preview.config)),
                     datetime.now(timezone.utc).isoformat(), len(fresh.rows), _json(changes), _json(reconciliation)))
        columns = ','.join(LINE_FIELDS)
        placeholders = ','.join('?' for _ in LINE_FIELDS)
        update = ','.join(f'{field}=excluded.{field}' for field in LINE_FIELDS[4:])
        for row in fresh.rows:
            old = existing.get(_key(row))
            if old == row:
                continue
            con.execute('INSERT INTO line_history VALUES (?,?,?,?,?,?,?)',
                        (preview.batch_id, *_key(row), _json(old) if old else None, _json(row)))
            con.execute(f'INSERT INTO canonical_lines ({columns}) VALUES ({placeholders}) '
                        f'ON CONFLICT(source,location_id,order_id,line_id) DO UPDATE SET {update}',
                        tuple(row[field] for field in LINE_FIELDS))
        con.execute('UPDATE import_meta SET revision=revision+1 WHERE singleton=1')
        con.execute('COMMIT')
        return {'already_imported': False, 'batch_id': preview.batch_id,
                'changes': changes, 'reconciliation': reconciliation}
    except Exception:
        if con.in_transaction:
            con.execute('ROLLBACK')
        raise
    finally:
        con.close()
