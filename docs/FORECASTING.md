# Item-demand baseline

Purpose: anticipate quantities that a restaurant may need to prepare. Pizza is one synthetic example; recipes are unchanged. This is a quantity baseline feeding the constrained prep planner, not a feasible prep recommendation or an inventory adjustment.

## Run the reproducible demo

```sh
.venv/bin/python scripts/demo_forecast.py
```

The script creates 12 weeks of explicitly synthetic daily canonical orders in a temporary SQLite database, including simulated historical import times. It removes that database afterward. It never modifies an operational database. The historical-clock patch exists only in this demo builder, not in the forecasting API or normal importer.

Observed result: August 24 forecast = 29 items, mean of prior Monday quantities 26, 28, 30 and 32. Rolling-origin evaluation on the last four Mondays: same-weekday MAE **5 items**, prior-four-complete-dates comparator MAE **8 items**, four scored origins each. Data deliberately contains weekday structure and an increasing trend; neither number estimates real-world accuracy or savings.

## Backend interface

`restaurant_lab.forecasting.forecast(config, target=..., as_of=..., coverage=..., menu=..., db_path=...)`:

- `config`: one registered canonical source/location, with unchanged timezone, currency and business cutoff. No source/currency pooling.
- `target`: business date to predict. `as_of`: timezone-aware prediction issue time, no later than target business-day start. Earlier issue times are allowed.
- `coverage`: `{business_date: confirmed_at}`; explicit assertions that this open business date has complete imported data, confirmed after its business-day close. Missing dates remain unknown, never inferred closed or zero. Confirmations learned after issue time are excluded. The caller is responsible for truthful coverage; a file's presence is not proof of completeness.
- `menu`: `MenuItem(item_id, unit, available_from, known_at)` records for a fixed active menu. Future-known items are excluded from predictions. Missing SKU sales become zero only on explicitly covered days when the item was offered. Menu availability and coverage persistence/forms are **not implemented**; these are explicit integration inputs. Do not infer the menu from the full future dataset.
- Defaults: latest four eligible matching weekdays; at least two observations. `status=insufficient_history` and null quantity when that threshold is not met. Two observations is a transparent starter rule, not a confidence guarantee.

Output: item/unit, observation dates and actual observed quantities, exact mean as numerator/denominator of millionths, and `forecast_micros` rounded upward only to the smallest supported millionth. The prep planner must handle whole-item/batch rounding, fixed recipes, inventory and capacity separately. Never interpret a missing forecast as zero or treat it as feasible prep.

## Temporal integrity

The backend replays `line_history` joined to `import_batches`, using only snapshots whose actual import timestamp **and** source-update timestamp precede the issue time. It does not train from today's corrected current-state table. This protects historical predictions from later corrections and late-arriving imports. A bulk historical CSV imported today does not provide historical application knowledge; retrospective origins may correctly have no usable history. No timestamp rewriting is allowed for real imports.

`backtest(..., targets=..., evaluation_as_of=...)` runs each prediction at that target's business-day start. Ground truth uses evaluation-time snapshots and explicit complete-date assertions. It reports scored/skipped counts and MAE separately per item/unit; missing targets are skipped. Future origins are rejected. Coverage/menu must be supplied with true knowledge timestamps. It does not provide a confidence interval, demand uplift or production accuracy claim.

Quantities are **fulfilled quantities**, including food prepared on later-voided/refunded lines. Money has no effect on this baseline. Fulfilled sales can understate unconstrained demand after stockouts or lost sales. No stockout correction, promotions, holiday adjustment, waste optimization or automatic purchasing is implemented. The current single-order canonical fixture is insufficient for a useful forecast.

## Next integration

You: review the demo's four observations and accept/document coverage and fixed-menu inputs for a permitted dataset. Teammate: consume this interface after source selection; show insufficient-history and observations beside the estimate. Both: validate a representative source before presenting operational recommendations. `planning.py` now computes fixed-recipe resource-constrained scenarios; the separate Prep Planner demo consumes this forecast. No forecast automatically changes recipes or saved inventory.
