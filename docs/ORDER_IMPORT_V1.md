# Order import contract v1 · local backend milestone

**Implemented backend; upload UI and vendor mapping remain pending.** This is our explicit canonical CSV format, not a Toast/Square export adapter and not a production-readiness claim. The existing pizza importer/app still use their original database. The new backend uses `data/processed/canonical_orders.sqlite`; it has no Streamlit upload screen yet.

## What you can try now

From the project folder:

```sh
.venv/bin/python scripts/preview_order_fixture.py
```

This only previews [the synthetic example](../tests/fixtures/canonical_v1/valid.csv). It starts no server, makes no API call and saves no database. Expected: 1 order, 2 distinct lines, 4 items, gross $40, discounts $4, cumulative refunds $5, net $31; all 4 items were fulfilled. A financial refund does not imply food returned to stock.

## File contract

UTF-8 CSV (optional UTF-8 BOM), comma separator, standard CSV quoting, one latest **line snapshot** per stable identity. Header names are case-sensitive and must exactly match the set below; column order may vary. Unknown columns, duplicate headers, missing fields, malformed records and unsupported values reject the entire file. Do not silently trim/guess mappings. Maximum 10 MiB and 50,000 data rows per file. Blank physical records follow Python CSV semantics and are skipped; a header-only file is rejected.

| Field | Required meaning |
|---|---|
| `schema_version` | Literal `1`. |
| `source` | Stable source/provider identifier; must match selected location configuration. `synthetic_demo` labels our fixtures. |
| `location_id` | Stable location ID, not its display name; must match configuration. |
| `order_id` | Stable source order ID, stored as text; leading zeros preserved. |
| `line_id` | Stable source line ID within an order. Repeated purchases of the same item need distinct line IDs. |
| `item_id` | Stable item/variation ID, not a name-derived key. Renames may change `item_name` without changing identity. |
| `item_name` | Display name, 1–200 characters; no control characters. Must not contain customer/staff/private notes. |
| `ordered_at` | Order-open timestamp, ISO 8601 with seconds and explicit offset, e.g. `2026-10-01T01:30:00-07:00`. Offset must match the configured IANA zone at that instant; UTC `Z` is appropriate when the location offset is zero. |
| `source_updated_at` | Source revision timestamp, ISO 8601 with seconds and explicit offset or `Z`, no earlier than `ordered_at`. Must increase for changed snapshots. It is **not** file-upload time. |
| `timezone` | IANA zone matching configuration, e.g. `America/Los_Angeles`; unknown timezone rejected for this contract. The original pizza dataset retains its separately documented unknown timezone. |
| `business_date` | `YYYY-MM-DD`, computed from order-open local time and explicit start hour. Before cutoff belongs to prior date. This v1 definition is **not automatically a POS fulfillment business date**. Scheduled/fulfilled-date accounting needs an adapter/contract extension. |
| `currency` | One of `USD`, `CAD`, `EUR`, `GBP` (2 decimals), `JPY` (0), `KWD` (3), matching the location configuration. No FX conversion or mixed currencies within a location. |
| `quantity_unit` | `each`, `kg`, `g`, `l` or `ml`. No implicit conversion. Totals remain separated by unit. |
| `quantity` | Positive ordered quantity, up to 6 decimal places and 1,000,000 units per line. Plain decimal only, no separators/exponents. |
| `fulfilled_quantity` | Explicit quantity actually fulfilled/prepared, same unit, between zero and ordered quantity. Required, never inferred from money/refund. If the source cannot establish it, do not pretend this contract is fully mapped. |
| `status` | `completed` or `voided`. Open/pending/cancelled statuses require an explicitly verified mapping or a later contract; never silently map them to completed. |
| `gross_amount` | Total product-line amount **for all its quantity**, before discount, excluding taxes, tips and service charges. Not unit price. |
| `discount_amount` | Cumulative discount allocated to this line; nonnegative and no greater than gross. |
| `refund_amount` | Cumulative completed product refund for this line **after discounts**, excluding refunded tax/tips/fees; not a new refund event. Must not exceed gross minus discount. For voided lines, must be zero. |

IDs use 1–128 ASCII letters/digits/underscore/dot/colon/hyphen, starting with a letter/digit. Amounts are plain nonnegative decimals; no float input, currency symbols, thousands separators, exponent notation or rounding. Maximum each monetary field: 10^12 minor units. Extra fractional zero digits are accepted only if the amount is exactly representable in the currency's minor units. Quantities are stored as integer millionths; money as integer minor units. Parsing uses Python Decimal, not floating-point arithmetic.

The caller explicitly supplies `LocationConfig(source, location_id, timezone, currency, business_day_start_hour)`. Cutoff is an integer 0–23. Once imported, a source/location's configuration cannot change without a separate migration. All lines of an order must agree on order timestamp, date, zone and currency, including lines already stored.

## Financial and food semantics

- Completed-line net = gross − discount − cumulative refund, exactly once. Voided lines contribute zero gross/discount/refund/net sales. They remain stored and counted as voided.
- `order_count` counts all stored order identities in scope, including all-void orders; it is **not a completed-sales-order count**. `line_count`, `completed_lines` and `voided_lines` are explicit.
- `quantity_by_unit` totals ordered quantities on completed lines. `fulfilled_by_unit` totals explicit fulfilled quantities on all lines, including a line voided after food was prepared. Neither automatically updates inventory.
- Refund/void corrections replace the prior snapshot. Do not add a negative refund row or subtract the refund again downstream.
- Reconciliation shows current snapshots attributed to the original order business date. It is **not a refund-date ledger, payment settlement/payout report, tax report or immutable historical as-of view**. `line_history` retains changes for audit, but no as-of reporting API is implemented.
- Partial returns, open refund requests, order-level adjustments without defensible line allocation, modifier breakdowns, exchanges, gift cards, multi-tender/payment details and deleted-row events are unsupported in v1. A missing row in a later file never means deletion or void.

## Teammate interface: preview first, confirm second

```python
from restaurant_lab.imports import LocationConfig, preview_csv, commit_preview

config = LocationConfig(
    source="synthetic_demo", location_id="demo_location",
    timezone="America/Los_Angeles", currency="USD", business_day_start_hour=4,
)
preview = preview_csv(csv_bytes, config)  # No writes, including no database creation.
# Display preview.errors, preview.rows, preview.summary and preview.changes.
# Keep this exact preview in SERVER-SIDE session state.
# Only an explicit user confirmation button should reach this next call:
result = commit_preview(preview, confirmed=True)
```

`preview.errors` contains logical record numbers (header=1) and explanations without echoing rejected cell values. All errors block commit. At most 100 invalid rows are reported per preview. When errors exist, the summary describes only rows validated so far and is marked `importable=false`; do not display it as an accepted import total.

`preview.summary` describes incoming valid snapshots, **not additional sales**. `preview.changes` forecasts inserted/updated/unchanged counts. `result.reconciliation` describes the current entire source/location after commit, including previously stored rows. Monetary fields end in `_minor`; display using the configured currency exponent. Quantities are decimal strings keyed by unit. Do not add the input summary to existing totals.

Regenerate preview whenever file/configuration changes. If the database changes after preview, commit raises `StalePreview` (or rejects a now-invalid source correction); regenerate and ask for confirmation again. Changed preview display dictionaries cannot alter saved values: commit reparses the immutable source bytes. The confirmation flag is an API safeguard, **not authentication or proof of a human review**; the UI must enforce that interaction.

Do not accept database paths from untrusted users. Use the backend's dedicated path. Local tests may pass a temporary path. HTML-rendered values must remain escaped; no CSV export feature is included here, and spreadsheet formula-safety is a separate requirement if one is added.

## Idempotency, persistence and audit

- Identity is `(source, location_id, order_id, line_id)`, never item name or entire-row deduplication.
- Identical stored snapshots are unchanged. Different snapshots require a strictly newer `source_updated_at`. Equal-version conflicts and older conflicting records are rejected. No fields are guessed or merged silently.
- Exact replay of a current file/configuration is a no-op with `already_imported=true`. Reordered/equivalent files can add a new audit batch, but do not double-count lines. Replaying an obsolete pre-correction file is rejected rather than reverting history, even if that file was once imported.
- A batch digest binds raw bytes, contract version and configuration. Audit includes file hash, configuration, timestamp, row/change counts and reconciliation. Raw upload bytes are not saved automatically; any retained exports must remain in a separately authorized private location.
- SQLite uses `BEGIN IMMEDIATE`, a five-second lock timeout and one transaction for snapshots, configuration, batch audit, before/after history and revision. A mid-write failure rolls all of these back. A failed first transaction may leave an empty SQLite file; the next import can initialize it safely.
- A database instance UUID plus revision detects replacement/other commits after preview. Application ID/schema version rejects unrelated databases, including the pizza demo. Existing unrelated tables within a recognized canonical database are preserved.
- There is no whole-database replacement, inventory clearing or implicit migration. Concurrent writers are serialized/rejected for a fresh preview; distributed deployment is not supported. Keep a tested backup/restore and access-control plan before real operations; this milestone does not supply them.

## Scope and next handoff

Implemented: strict v1 parsing, preview/error report, explicit transactional commit, idempotency/corrections, audit and exact reconciliation; synthetic fixture/edge tests. Original pizza app remains unchanged and **does not read this new database**.

Next teammate work: upload → config selection → preview/errors → explicit confirmation → results. Next joint work: obtain a permitted export, document its exact vendor/report/version mapping and reconcile it with the source report. An arbitrary vendor export must not be relabeled as this CSV. If required fields or safe line allocations are missing, report the gap and change the contract deliberately.

Not implemented: real Toast/Square connector, generic column mapper, live synchronization, restaurant auth/data access enforcement, UI integration, forecasting/planning, Meta use, backups/migrations or production deployment. Extra columns are rejected, but that is not PII detection inside permitted text fields. Synthetic fixtures are the only shipped input examples.
