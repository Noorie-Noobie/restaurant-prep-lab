# Restaurant Prep Lab 🍕

## Next to tackle

The repository includes the forecast, fixed-recipe planner and synthetic Meta extraction/review integration code. **No actual Meta response has been verified.** The existing Explore dashboard remains separate from imported-order analytics. No teammate-specific UI branch or pull request was available at the November 4 check.

| Owner | Next action | Dependency / done check |
|---|---|---|
| **Teammate · M1/M2/M3** | Follow [Meta setup and live verification](docs/META_INTEGRATION.md), then run one explicitly authorized synthetic request | Private credentials and billing/credits ready; actual response, source review and planner handoff verified |
| **You · V1** | Rehearse [the three-minute walkthrough](docs/DEMO_WALKTHROUGH.md) | Explain 29 expected → 20 feasible / 900 g cheese shortage → 29 feasible after hypothetical replenishment; keep recipes fixed |
| **Both · I3/I6** | Identify the teammate's actual UI branch and connect upload/preview/confirm and imported-source selection | Use [import contract](docs/ORDER_IMPORT_V1.md) and [analytics interface](docs/IMPORTED_ANALYTICS.md); totals reconcile without mixing datasets |
| **Both · release** | Review [public-release blockers](docs/PUBLIC_RELEASE_REVIEW.md) | Agree license, verify live demonstration, record video and separately authorize public visibility; no submission has occurred |

[Open the shared checklist → TASKS.md](TASKS.md). Statuses: **Working now**, **Haven't started**, **Almost done**, **Completed**. No feature is claimed actively in progress at handoff. Latest automated evidence: **97 tests passed**, including mocked provider tests; this is not proof of live Meta operation or real-world accuracy.

Every authorized upload must refresh this summary and task statuses from evidence. Teammates should update their own tasks in a normal PR or GitHub Markdown edit. This rule does not authorize publication, deployment or unrelated work.

## Run the app

Follow [CONTRIBUTING.md](CONTRIBUTING.md) for first-time setup. From the cloned project folder, run:

```sh
sh run.sh
```

Open the localhost URL printed by Streamlit (normally http://127.0.0.1:8501). Keep your launch Terminal open; stop with Control+C. Closing a browser tab does not stop the server. Sleep or shutdown interrupts availability. This is a local foreground app, not a hosted service. The separate local `Start App.command` launcher repair is not included in this upload.

## Exact tools and locations

| Job | Tool | Where it lives |
|---|---|---|
| Build and view the app | Python 3.12 + Streamlit | `app.py`, browser at localhost:8501 |
| Original transactions | gt fictional pizza dataset, already downloaded | `data/raw/pizzaplace.csv` (do not edit) |
| Queryable data | SQLite, a local file, no account | `data/processed/restaurant.sqlite` |
| Fictional pizza import | pandas + Python sqlite3 | `src/restaurant_lab/data.py` |
| Canonical CSV import (backend only) | Python CSV/Decimal + SQLite | `src/restaurant_lab/imports.py`; [contract v1](docs/ORDER_IMPORT_V1.md) |
| Bestsellers and rush hours | pandas + Altair charts | `src/restaurant_lab/analytics.py` |
| Forecast and feasible prep | deterministic Python | `src/restaurant_lab/forecasting.py`, `planning.py` |
| Counted-stock extraction and review | Meta Muse Spark 1.3, offline-tested integration | `meta_stock.py`, `meta_stock_ui.py`; live verification pending |
| Checks | pytest + Streamlit AppTest | `tests/` |
| Shared work checklist | GitHub Markdown | [TASKS.md](TASKS.md) |

## Already works / remaining

**Works:** canonical v1 preview/explicit commit, idempotent snapshots, exact reconciliation and rollback tests (backend only, no vendor adapter); immutable raw CSV → validated SQLite, date filtering, units/revenue ranking, weekday-hour order heatmap, fixed-recipe synthetic prep scenario, extraction-schema validation. All data is fictional, not actual San Francisco restaurant results.

**Implemented demo:** forecast → one fixed recipe → reviewed stock → ingredient/time-constrained prep. **Still unfinished:** real-source integration, persisted operational stock, live Meta review-and-save workflow and grounded model explanations. Meta adapter follows current official API syntax but has **not been called or verified against a live account**. The Meta Evidence UI now has an explicitly gated synthetic-note call; no live result has been verified.

## Current Meta workflow

1. Show the fixed, clearly synthetic counted-stock note in **Meta Evidence**.
2. With private runtime configuration and explicit consent, send it to Muse Spark for quantities, units and exact source quotes. No live call has yet been verified.
3. Review/correct the candidate and explicitly confirm. The session audit retains before/after values and request identity; it is not durable storage.
4. Open **Prep Planner**. Confirmed stock initializes its form; Python computes fixed-recipe ingredient needs and feasible portions under stock/time limits.

The older invoice-image adapter is separate and unverified. Invoices are purchases, not automatically on-hand inventory. PDF handling and model-generated explanations/tool calls are unfinished. The model cannot change recipes, order stock or override arithmetic.

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

Only Meta inference needs a service account for this stack. The database, charts and local app have no service cost. The `.env.example` contains placeholders only and is not auto-loaded. Do not paste keys into chat or commit `.env`. The current counted-stock API requires explicit `authorized=True` (the older image adapter uses `allow_live=True`) and `META_LIVE_ENABLED=true`, plus `MODEL_API_KEY`. Neither has been enabled. Verify credits, allowed models and spending limits privately before integration testing; unused cloud offers do not need to shape this app.

Official docs checked October 28, 2026: [models](https://dev.meta.ai/docs/models), [structured output](https://dev.meta.ai/docs/structured-output), [image understanding](https://dev.meta.ai/docs/image-understanding). API endpoint: `https://api.meta.ai/v1/chat/completions`; default model: `muse-spark-1.3`. Requests goes directly to Meta; no OpenAI model/API service is involved.
