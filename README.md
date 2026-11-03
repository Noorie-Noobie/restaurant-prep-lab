# Restaurant Prep Lab 🍕

## Next to tackle

**Analytics update:** imported-order analytics backend and six new checks are implemented. [Run the disposable chart demo and see the UI handoff](docs/IMPORTED_ANALYTICS.md). You: review its $31 reconciliation; Aishwarya: add explicit data-source/location selection using the interface. Done: imported charts reconcile without mixing the pizza dataset. All 63 tests pass after hydration completed. App source selection remains teammate UI work.

**[Open the shared checklist → TASKS.md](TASKS.md)** — statuses: **Working now**, **Haven't started**, **Almost done**, **Completed**. No code feature is currently marked Working now.

**Import Orders now comes before forecasting.** The canonical backend is implemented/tested; vendor mapping and upload UI are still pending.

| Who / task | Do next | Depends on | Done check |
|---|---|---|---|
| **You · I2** | Read the synthetic example and run `.venv/bin/python scripts/preview_order_fixture.py` | I1 backend complete | Explain why 1 order / 4 fulfilled items has $31 net sales; preview saves nothing |
| **Teammate · I3** | Build upload → preview/errors → explicit confirm using [the interface](docs/ORDER_IMPORT_V1.md#teammate-interface-preview-first-confirm-second) | S2 access/setup; I1 backend | No writes before confirmation; rejected files preserve data; result shows reconciliation |
| **Both · I4** | Map one permitted, named POS export to the documented contract | I2/I3 and access to a permitted export | Quantities, void/refund semantics, dates and totals match that source; no generic compatibility claim |
| **Both · S3/D3, then A3/U2** | Resume recipe/stock inputs and forecast/planner work after ingestion acceptance | I4, plus existing task dependencies | The planner will consume validated data rather than pizza-only assumptions |

The existing Explore app still uses the fictional pizza dataset; the new canonical importer has no upload screen yet.

Meta access/credit checks (**Teammate · M1**) can proceed in parallel after setup; keep keys private. The adapter is a scaffold, not verified live extraction. Proposed internal feature freeze: **November 2**; hackathon deadline: **November 4, 6 PM Pacific**.

**Keep this current:** every authorized project upload by this assistant must update task statuses from evidence and refresh this summary's owner, dependency and done check. Teammates likewise update their own tasks when starting/finishing via GitHub Markdown editing or their normal PR. This is project upkeep, not authorization for unrelated uploads, feature work, merges or deployment.

## Run the starter

**Start here:** open Terminal and paste this one command. The local environment and database are already prepared on this computer.

```sh
sh "/Users/arshnoorbhatia/Documents/Codex/2026-10-28/task-2/restaurant-prep-lab/run.sh"
```

Open **http://127.0.0.1:8501**. Stop with **Ctrl+C**. This starts a local process only.

## Exact tools and locations

| Job | Tool | Where it lives |
|---|---|---|
| Build and view the app | Python 3.12 + Streamlit | `app.py`, browser at localhost:8501 |
| Original transactions | gt fictional pizza dataset, already downloaded | `data/raw/pizzaplace.csv` (do not edit) |
| Queryable data | SQLite, a local file, no account | `data/processed/restaurant.sqlite` |
| Fictional pizza import | pandas + Python sqlite3 | `src/restaurant_lab/data.py` |
| Canonical CSV import (backend only) | Python CSV/Decimal + SQLite | `src/restaurant_lab/imports.py`; [contract v1](docs/ORDER_IMPORT_V1.md) |
| Bestsellers and rush hours | pandas + Altair charts | `src/restaurant_lab/analytics.py` |
| Forecast and feasible prep | deterministic Python, to implement | `src/restaurant_lab/planning.py` |
| Invoice image extraction | Meta Muse Spark 1.3, adapter prepared | `src/restaurant_lab/meta.py` |
| Checks | pytest + Streamlit AppTest | `tests/test_starter.py` |
| Shared work checklist | GitHub Markdown | [TASKS.md](TASKS.md) |

## Already works / remaining

**Works:** canonical v1 preview/explicit commit, idempotent snapshots, exact reconciliation and rollback tests (backend only, no vendor adapter); immutable raw CSV → validated SQLite, date filtering, units/revenue ranking, weekday-hour order heatmap, seven-dish planning scope, manual extraction-schema validation. All data is fictional, not actual San Francisco restaurant results.

**Scaffold:** forecast, recipe quantities, inventory/capacity planning, review-and-save workflow, grounded model explanations. Meta adapter follows current official API syntax but has **not been called or verified against a live account**. The UI has no live-call button yet.

## How Meta becomes the demo's main workflow

1. Show a demo invoice photo alongside Muse Spark's extracted ingredient, quantity, unit, cost and quoted source evidence.
2. Owner corrects uncertain fields and explicitly confirms them. Preserve before/after values, image hash, model/request ID and source location in an audit record.
3. Only confirmed, normalized stock values enter planning tables. An invoice records purchases, **not automatically current stock**; reconcile usage and existing stock first.
4. Python computes the demand/prep scenario and checks stock plus prep-time limits. Show its actual structured output.
5. Muse Spark explains that result with evidence references. Never let prose override numeric feasibility checks.

This supports a visible “document → checked evidence → feasible action” demo. It is not a chat widget that invents the restaurant's metrics. JPG/PNG extraction is scaffolded; PDF page conversion and recipe-specific extraction schema remain tasks.

## Team workflow

Arshnoor owns `data.py`, `analytics.py`, `planning.py` and their tests. Teammate owns `app.py`, `meta.py`, review UI and its tests. Agree function input/output shapes before editing shared files. See [TASKS.md](TASKS.md) for status, proposed owner, next action, dependencies and completion checks. GitHub synchronizes code and the verified download manifest; each laptop runs its own app/database. The private repository is [Noorie-Noobie/restaurant-prep-lab](https://github.com/Noorie-Noobie/restaurant-prep-lab). Teammates need an invitation before cloning.

## Useful commands (from this folder)

```sh
# Rebuild derived data without changing the downloaded CSV
PYTHONPATH=src .venv/bin/python -m restaurant_lab.data
# Run meaningful checks
PYTHONPATH=src .venv/bin/python -m pytest -q
# Inspect SQLite without installing a database service
sqlite3 data/processed/restaurant.sqlite 'SELECT item_name, SUM(quantity) AS pizzas FROM order_lines GROUP BY item_name ORDER BY pizzas DESC LIMIT 7;'
```

## On your teammate's computer

Once the owner grants you access to the private GitHub repository, follow [CONTRIBUTING.md](CONTRIBUTING.md) for clone/install/run/test and pull requests. Alternatively transfer this folder excluding `.venv` and secrets. Use Python 3.11+ (3.12 recommended). Then:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python scripts/download_data.py
sh run.sh
```

The data download is checksum-verified; see `scripts/download_data.py` and `data/PROVENANCE.md`. The lock file records this computer's tested packages; OS-specific wheel availability can differ. `pyproject.toml` lists supported dependency ranges. `run.sh` sets the import path, so an editable install is unnecessary.

## Credits and credentials: later, once access is confirmed

Only Meta inference needs a service account for this stack. The database, charts and local app have no service cost. The `.env.example` contains placeholders only and is not auto-loaded. Do not paste keys into chat or commit `.env`. Live adapter calls require both explicit `allow_live=True` and `META_LIVE_ENABLED=true`, plus `MODEL_API_KEY`. Neither has been enabled. Verify credits, allowed models and spending limits privately before integration testing; unused cloud offers do not need to shape this app.

Official docs checked October 28, 2026: [models](https://dev.meta.ai/docs/models), [structured output](https://dev.meta.ai/docs/structured-output), [image understanding](https://dev.meta.ai/docs/image-understanding). API endpoint: `https://api.meta.ai/v1/chat/completions`; default model: `muse-spark-1.3`. Requests goes directly to Meta; no OpenAI model/API service is involved.
