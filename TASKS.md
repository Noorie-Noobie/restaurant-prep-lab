# Build board · October 28–November 4

A = Arshnoor. T = teammate. Both have technical ownership. Dates are targets; finish dependencies first. Build freeze November 3. Submit manually by **November 4, 4 PM Pacific**; deadline **6 PM Pacific** (November 5, 02:00 UTC).

## Setup + data

| ID / day | Owner | Action / exact location | Depends on | Done criterion | Status |
|---|---|---|---|---|---|
| S1 · Oct 28 | A | Run `sh run.sh`, open localhost:8501 | — | Explain order vs pizza totals on Explore | Starter ready; walkthrough pending |
| S2 · Oct 28 | T | Copy project without `.venv`; README teammate setup | — | Same app runs on teammate computer | Pending |
| S3 · Oct 28 | Both | Agree function inputs/outputs in README | S1 | Explain demand + recipes + stock → plan | Pending |
| D1 · Oct 28 | A | Inspect `data.py`, `data/PROVENANCE.md`, SQLite | — | 49,574 lines, 21,350 orders, $817,860.05; keep repeated items | Implemented; owner review pending |
| D2 · Oct 29 | A | Add coverage report in `data.py` | D1 | Seven missing dates marked unknown, not zero sales | Pending |
| D3 · Oct 29 | A | Create `data/assumptions/recipes.csv`, `inventory.csv`, `capacity.csv` | D1 | Seven names, size-specific recipe weights/units; invented inputs labeled demo assumptions | Pending |

## Analytics + planning

| ID / day | Owner | Action / exact location | Depends on | Done criterion | Status |
|---|---|---|---|---|---|
| A1 · Oct 29 | A | Review `analytics.py`, compare with SQLite query | D1 | Units/revenue and distinct-order heatmap agree | Implemented; owner review pending |
| A2 · Oct 29 | A | Add per-observed-weekday hourly averages in `analytics.py` | D2 | Correct denominators and date coverage labels | Pending |
| A3 · Oct 30 | A | Implement trailing-four-observed-same-weekdays baseline in `planning.py` | D2 | Per-SKU next-day demand, cutoff and observation count; unknown closures handled | Pending |
| A4 · Oct 30 | A | Hold out last four weeks, compare baseline with trailing mean | A3 | MAE on known observed dates, no future-data leakage; menu-selection limitations documented | Pending |
| P1 · Oct 31 | A | Compute ingredient amounts from recipes in `planning.py` | D3,A3 | Correct size-specific demand multiplication; missing recipes fail clearly | Pending |
| P2 · Nov 1 | A | Implement deterministic feasible prep in `planning.py` | P1 | No stock or prep-time overrun; unmet demand shown; allocation policy explained | Pending |
| P3 · Nov 1 | Both | Compare low/base/high demand scenarios | P2 | Reproducible numbers, leftover/shortfall tradeoffs | Pending |

## Meta + user interface

| ID / day | Owner | Action / exact location | Depends on | Done criterion | Status |
|---|---|---|---|---|---|
| M1 · Oct 29 | T | Review `meta.py`; privately check Meta credit/model access | S2 | Model/endpoint/allowance known, no committed secrets | Adapter ready; live untested |
| M2 · Oct 30 | T | Create labeled demo invoice image; run extraction after account approval | M1 | Actual response with quantity/unit/cost/source quote; model/request ID saved | Pending |
| M3 · Oct 31 | T | Add correction + confirmation UI in `app.py`, audit in `data/evidence/` | M2 | Unconfirmed/null/invalid fields blocked; edit history retained; changing image clears old candidate | Pending |
| M4 · Nov 1 | T | Reconcile confirmed purchases to current stock in SQLite | M3,D3 | Purchase is not assumed on-hand stock; units normalized; unknown IDs rejected | Pending |
| M5 · Nov 2 | T | Explain actual `plan_prep` results through Meta | M4,P2 | Numeric function results and evidence references displayed; prose cannot override constraints | Pending |
| U1 · Oct 30 | T | Polish Explore filters/errors/empty states in `app.py` | A1 | Synthetic label, units and date boundaries clear | Starter ready; polish pending |
| U2 · Nov 1 | T | Connect Prep Planner form to Python function | P2 | Scenario controls show genuine stock/time constraints | Pending |
| U3 · Nov 2 | T | Show side-by-side Meta evidence trace | M5 | Source → extracted row → edit → stock → computation → explanation | Pending |

PNG/JPEG extraction is scaffolded. PDF page conversion and recipe extraction are optional later work. Avoid paid requests on Streamlit reruns. User confirms external upload and account usage before live testing.

## Testing + demo

| ID / day | Owner | Action / exact location | Depends on | Done criterion | Status |
|---|---|---|---|---|---|
| Q1 · Oct 28 | A | `PYTHONPATH=src .venv/bin/python -m pytest -q` | D1 | Ingestion, repeated-item/rush counts, UI smoke pass | Starter checks provided |
| Q2 · Nov 2 | A | Add planning/leakage tests in `tests/` | P2,A4 | Impossible stock/time rejected; no future training rows | Pending |
| Q3 · Nov 2 | T | Add timeout/refusal/bad-JSON and confirmation tests | M3 | Recoverable UI; no accidental save or repeated spend | Pending |
| Q4 · Nov 3 | Both | Full suite and clean-start walkthrough | Q2,Q3,U3 | Pages work, synthetic/live state honest, no secrets packaged | Pending |
| V1 · Nov 3 | Both | Rehearse three-minute demo | Q4 | A explains analytics/constraints; T shows Meta evidence flow | Pending |
| V2 · Nov 3 | Both | README, recording, architecture slide | V1 | Actual outputs, limits and simulated-only impact clearly labeled | Pending |
| V3 · Nov 4 | Both | Verify submission fields; submit by 4 PM Pacific | V2 | Receipt before 6 PM deadline | Pending |

## Daily 15-minute joint checkpoint

| Date | Show each other |
|---|---|
| Oct 28 | Same app running; ownership agreed |
| Oct 29 | Clean data, seven-dish assumptions, Meta access status |
| Oct 30 | Baseline and actual extraction (or clearly labeled manual fallback) |
| Oct 31 | Ingredient requirements and correction screen |
| Nov 1 | Confirmed stock feeds feasible prep |
| Nov 2 | Source-to-explanation flow and failure cases |
| Nov 3 | Frozen build and complete rehearsal |
| Nov 4 | Submission fields and receipt |

If time is tight, keep one image format, one baseline, and seven dish names. Defer PDF, basket analysis, accounts and deployment. Preserve source evidence, human confirmation and deterministic checks.
