# Imported-order analytics handoff (backend milestone)

The new `src/restaurant_lab/import_analytics.py` is a read-only backend. The existing pizza Explore screen and Aishwarya's upload UI ownership are unchanged. There is no new source selector in `app.py` yet.

## Try the disposable fixture demo

```sh
python3 scripts/demo_import_analytics.py /tmp/imported-orders-demo.html
```

Open that HTML file in a browser. It shows a labeled synthetic net-sales bar and rush count. The script imports the existing generic sandwich test fixture into a temporary database, computes results, then removes that temporary database. It does not modify either project database. The optional HTML destination must not exist. Omit it to print JSON only. This is a backend integration demonstration, not pizza/wing demand evidence.

Expected: 1 order, 2 lines, 4 fulfilled items, $40 gross less $4 discounts and $5 cumulative refunds = $31 net; Thursday 01:00 local rush count is 1 although the configured 04:00 cutoff puts the order on Wednesday's business date.

## Aishwarya's UI integration

1. Offer two clearly separate choices: **Fictional pizza demo** and **Imported orders**. Keep the old path for the former. Never concatenate their frames.
2. For imported orders, call `available_locations()` and require selection of one returned `LocationConfig`. Show source, location, currency, timezone and cutoff. An empty list means no committed imports; do not silently fall back to pizza data. Do not offer arbitrary database paths to users.
3. Call `dashboard(config, start=date(...), end=date(...))` after an explicit business-date range selection. Handle missing/invalid DB and configuration errors visibly. Refresh after a successful import; no stale chart caching across revisions.
4. Use `items` for item net-sales rankings and `rush_orders` (Monday–Sunday rows, 0–23 hour columns) for the heatmap. Always label currency and units. Do not mix kilograms with counts or combine SKUs just because their names match.

Money remains Python integer minor units; quantities remain integer millionths. Convert to decimal strings for exact display using the currency exponent in `imports.CURRENCY_DIGITS`. Any float conversion is presentation-only. `revision` and `database_id` identify the consistent read snapshot.

Net sales exclude voids and subtract cumulative refunds once; refunds are assigned to the original order business date, **not** an accounting posting date. Completed-order count includes fully refunded completed orders. Fulfilled quantities include voided lines because food may already have been prepared; they are not inventory adjustments. Rush is the local calendar weekday/hour of distinct orders having a completed line, not the business weekday. A repeated DST hour shares the same displayed hour bin. Empty/missing dates are not proof of closure or zero demand. No customer identity, customer satisfaction, profit, seasonality or forecast is inferred.

## Checks

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -p test_import_analytics.py -v
PYTHONPATH=src .venv/bin/python -m pytest -q
```

All 63 pytest cases passed on November 2 after hydration completed (57 existing plus 6 new; 4.16 seconds, one existing Streamlit/pandas warning). The six new cases also pass under standard-library unittest. Earlier attempts timed out while dependency files were downloading; the final full-suite run succeeded. No live POS, Meta or production readiness claim.
