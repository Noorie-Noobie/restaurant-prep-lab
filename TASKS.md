# Shared checklist · Restaurant Prep Lab

**Owners are proposed:** **You** = Arshnoor, analytics/planning; **Teammate** = app/Meta; **Both** = integration/review. Agree ownership before starting. This file is the single task board; [README → Next to tackle](README.md#next-to-tackle) is its short action summary.

## Next to tackle

**Analytics milestone:** I5 analytics backend completed; all 63 tests pass after hydration. Next: You review the disposable demo; Teammate wire the separate source selector and charts (I6).

**Current priority: safe order imports.** Import Orders precedes forecasting after the POS-compatibility audit. I1 is a tested canonical contract/backend, not a real vendor integration.

1. **You · I2:** review the synthetic canonical CSV and run `.venv/bin/python scripts/preview_order_fixture.py`. Done: explain 1 order, 2 lines, 4 fulfilled items, $40 gross − $4 discount − $5 refund = $31 net; nothing is saved by preview.
2. **Teammate · S2 → I3:** after repository access/local setup, build the upload/preview/confirm UI using the documented API. Done: no write before confirmation; all invalid rows block import; stale preview requires review again. UI work has not begun here.
3. **Both · I4:** map and reconcile one permitted actual POS export. Blocker: no representative permitted export validated yet. Done: documented vendor/report/version support and passing source reconciliation; do not relabel synthetic fixtures as Toast data.
4. **Both · S3/D3 then You · A3 / Teammate · U2:** resume planning input contract, baseline and planner UI after import acceptance. S1 Explore orientation and gated M1 account/credit checks may happen alongside this; no live Meta feature is enabled.

## How statuses work

| Status | Use it when |
|---|---|
| Working now | The named owner is actively doing it; keep at most one or two active items across the board. |
| Haven't started | Work has not begun, including work blocked on access or a dependency. |
| Almost done | Implementation exists, but the specifically named verification is still outstanding. |
| Completed | The completion check has evidence; check the box and record the result. |

**Working now: none.** I1 backend tests pass; I2/I3/I4 have not started. Only Completed items have checked boxes. Don't mark another person's work started or finished without their update/evidence.

## 1 · Setup and understanding

- [x] **G1 · Completed · Both — Share the starter privately.** Location: this GitHub repository. Done/evidence: private `Noorie-Noobie/restaurant-prep-lab`, starter on `main`, exact initial commit in Git history. Next: S2; no teammate invited yet.
- [x] **S0 · Completed · Both — Prepare the local starter.** Location: `run.sh`, `.venv`, `requirements.lock.txt`. Done/evidence: launcher started on localhost and health returned `ok`; stopped after verification. Next: S1/S2 on each person's laptop.
- [ ] **S1 · Haven't started · You — Walk through Explore yourself.** Location: `sh run.sh` → http://127.0.0.1:8501. Depends: S0. Next: filter to one month and compare orders, pizzas and sales. Done: record a bestseller and peak weekday/hour, with date range; explain that revenue is not profit.
- [ ] **S2 · Haven't started · Teammate — Get access and reproduce setup.** Location: GitHub + `CONTRIBUTING.md`. Blocker: exact username and authorized invitation. Next: provide username, then accept/clone/install/download/build/test/run. Done: independent app launch and nine starter tests pass (or current expected count).
- [ ] **S3 · Haven't started · Both — Agree one shared input/output contract.** Location: add a compact schema section to README. Depends: S1/S2/I4. Next: write one example containing SKU, ingredient quantity/unit, on-hand stock, minutes and confirmation metadata. Done: both can explain and use the same fields without guessing units.

## 2 · Data and demand · You

- [x] **I5 · Completed · You — Read canonical orders into dashboard analytics.** Location: `import_analytics.py`, `tests/test_import_analytics.py`, `docs/IMPORTED_ANALYTICS.md`. Evidence: all 63 pytest checks pass (57 existing plus 6 new), and disposable import-to-chart demo passes. Next: teammate I6 source selection and chart wiring. Done: full regression suite passes; source/currency isolation, refunds, voids and business-date/local-hour semantics verified. Backend implemented; no app UI claimed.
- [ ] **I6 · Haven't started · Teammate — Select imported data explicitly in Explore.** Location: `app.py`, interface in `docs/IMPORTED_ANALYTICS.md`. Depends: I3/I5. Next: add separate pizza/imported source choice, source/location and business-date selectors. Done: correct labels, empty/error states, no mixed currencies/data, and refreshed chart totals match committed imports. Existing app remains unchanged.

- [x] **I1 · Completed · You — Build a canonical CSV contract and safe import backend.** Location: `src/restaurant_lab/imports.py`, `docs/ORDER_IMPORT_V1.md`, `tests/test_imports.py`. Done/evidence: 48 new backend cases and 9 original tests pass (57 total), including repeat/overlap imports, refund/void handling, DST/currency, stale previews and transactional rollback. Next: I2 review and I3 UI. Backend milestone only; no Toast/Square adapter or production-readiness claim.
- [ ] **I2 · Haven't started · You — Explain and review the canonical sample.** Location: `tests/fixtures/canonical_v1/valid.csv`, `scripts/preview_order_fixture.py`. Depends: I1. Next: run the read-only preview and check each total by hand. Done: explain quantity versus line count and why a $5 refund does not undo four fulfilled items; note any contract questions.
- [ ] **I3 · Haven't started · Teammate — Build Import Orders UI.** Location: future app upload screen using `imports.py`. Depends: I1/S2. Next: retain the preview server-side, show rows/errors/configuration and require a separate confirmation action. Done: no writes on upload/rerun; invalid files and stale previews cannot commit; accepted results reconcile; existing Explore is not silently switched to a different source.
- [ ] **I4 · Haven't started · Both — Validate one real POS mapping.** Location: future provider adapter and source-specific tests. Depends: I2/I3. Blocker: no permitted representative export validated. Next: specify exact vendor/report/version and available fields. Done: source totals and quantity/status/business-date/refund meanings reconcile, reimport is safe, unavailable fields are explicit; no arbitrary-vendor claim.

- [x] **D0 · Completed · You — Download and ingest fictional orders.** Location: `scripts/download_data.py`, `data.py`, `data/PROVENANCE.md`. Done/evidence: checksum-verified source, 49,574 preserved lines, 21,350 orders, 91 SKUs and $817,860.05 in local SQLite. Fresh-download and integrity checks passed. Next: D1.
- [ ] **D1 · Haven't started · You — Understand the source limitations.** Location: `data/PROVENANCE.md`, `data.py`. Depends: D0. Next: inspect one multi-pizza order and the timezone/status assumptions. Done: explain why identical item rows remain, timezone stays unspecified, and absent dates are not confirmed zero-sales days.
- [ ] **D2 · Haven't started · You — Add observed-date coverage.** Location: `data.py` / `analytics.py`. Depends: D1. Next: list observed and missing dates; keep unknown closures separate. Done: seven absent calendar dates are flagged, never silently filled as open/zero-sales days.
- [ ] **D3 · Haven't started · You — Define confirmed planning inputs.** Location: future `data/assumptions/recipes.csv`, `inventory.csv`, `capacity.csv`; validation in `planning.py`. Depends: S3. Next: create one size-specific SKU example, then cover the seven selected names and their sizes. Done: explicit units, recipe amounts, stock and prep minutes validate; invented values are labeled demo assumptions; missing recipes fail clearly.
- [x] **A0 · Completed · You — Calculate starter sales patterns in code.** Location: `analytics.py`, Explore in `app.py`. Done/evidence: bestseller units/revenue, date filters and weekday-hour distinct-order totals work; repeated-item and full-data tests pass. Next: S1/U1; hourly averages remain A2.
- [ ] **A1 · Haven't started · You — Cross-check one sales result with SQL.** Location: README's SQLite query and `analytics.py`. Depends: S1/D1. Next: compare a dish's units with the chart for the same date range. Done: figures agree and you can explain the query; implementation evidence stays recorded separately in A0.
- [ ] **A3 · Haven't started · You — Build the simplest same-weekday baseline.** Location: `planning.py`. Depends: D2/S3/I4. Next: average the last four observed matching weekdays per SKU before a chosen cutoff. Done: returns next-day quantities, cutoff and observation count; future rows excluded and insufficient history handled explicitly.
- [ ] **A4 · Haven't started · You — Check the baseline on held-out dates.** Location: `tests/` plus a small evaluation result. Depends: A3. Next: hold out the last four weeks and compare with a trailing mean. Done: MAE on known observed dates, no future-data leakage, and whole-year demo menu selection disclosed.

## 3 · First technical milestone: inputs → deterministic prep

- [ ] **P1 · Haven't started · You — Translate demand into ingredient requirements.** Location: `planning.py`. Depends: D3/A3. Next: multiply SKU demand by size-specific recipe quantities. Done: unit-consistent totals match a hand-worked example; unknown ingredients/recipes stop calculation.
- [ ] **P2 · Haven't started · You — Enforce stock and prep-time limits.** Location: `planning.py`. Depends: P1. Next: implement a simple documented allocation policy and return prep quantities plus unmet demand. Done: no negative stock, no capacity overrun, reproducible result, tests for insufficient stock/time. Current `plan_prep` raises `NotImplementedError`.
- [ ] **U2 · Haven't started · Teammate — Build the planning input form and wire the result.** Location: `app.py`. Depends: S3/D3 for form; P2 for result. Next: edit labeled demo recipe/stock/capacity inputs and show validation errors; then call the planner. Done: only valid confirmed inputs produce a real Python result, with assumptions and limits visible.
- [ ] **P3 · Haven't started · Both — Demonstrate the first complete scenario.** Location: Prep Planner screen. Depends: P2/U2. Next: try one base case and one stock-shortage case. Done: both trace inputs → requirements → feasible prep → shortfall, with no model inventing the numbers.

## 4 · Meta and evidence · Teammate

- [x] **M0 · Completed · Teammate — Prepare the adapter and manual validator only.** Location: `meta.py`, Meta Evidence in `app.py`. Done/evidence: disabled-by-default PNG/JPEG adapter and schema validation exist; disabled-call and invalid-extraction tests pass. **This is not live extraction.** Next: M1/M2.
- [ ] **M1 · Haven't started · Teammate — Check private Meta access and credits.** Location: your Meta account, `.env.example`, `meta.py`. Depends: S2. Next: privately verify model availability, credit allowance and spending limit. Done: access and budget confirmed and local credential setup understood. Do not paste keys into chat/GitHub; no credentials or paid inference are configured by this starter.
- [ ] **M2 · Haven't started · Teammate — Verify one actual image extraction.** Location: `meta.py`; local labeled demo invoice photo. Depends: M1 plus explicit live-upload/spend authorization. Next: run one PNG/JPEG request and inspect quantity/unit/cost plus quoted evidence. Done: actual response, model/request ID and source references recorded locally; uncertain values remain unresolved. No fake fixture presented as model output.
- [ ] **M3 · Haven't started · Teammate — Add correction, confirmation and persistence.** Location: `app.py`, local `data/evidence/` and validated stock storage. Depends: D3/M2. Next: let the owner correct extracted fields and confirm before saving. Done: invalid/unconfirmed values blocked; edits and source linkage persist; changing the image invalidates an old candidate; purchases reconciled with on-hand stock. Manual JSON validation alone does not satisfy this task.
- [ ] **M5 · Haven't started · Teammate — Connect tools and a grounded explanation.** Location: `meta.py`, `app.py`. Depends: P3/M3. Next: expose an allowlisted deterministic planning function, show its arguments/result, then request an evidence-linked explanation. Done: judges can follow source → confirmed stock → actual tool result → explanation; prose cannot override feasibility; reruns do not repeat paid requests.

## 5 · Verification and demo · Both

- [x] **Q1 · Completed · Both — Run starter automated checks.** Location: `tests/test_starter.py`, `VALIDATION.md`. Done/evidence: nine tests pass; compilation, fresh dataset download and localhost health pass. One upstream chart deprecation warning. Next: add checks alongside new features; this does not prove visual quality or live Meta success.
- [ ] **U1 · Almost done · Teammate — Visually verify the existing three screens.** Location: local app in a browser. Depends: S2 or an available browser. Next: inspect labels, date filters, charts, empty states and narrow-window layout. Done: no clipping; fictional-data and live-Meta-off labels are readable; record observations/screenshots. Implementation and AppTest pass, but visual QA could not run because the isolated browser was unavailable.
- [ ] **Q2 · Haven't started · You — Verify new forecast/constraint behavior.** Location: `tests/`. Depends: A4/P2. Next: test cutoff leakage, unknown recipes and impossible stock/time. Done: meaningful failure and boundary cases pass, with evidence recorded in the task update.
- [ ] **Q3 · Haven't started · Teammate — Verify Meta/confirmation failure handling.** Location: `tests/`, `app.py`. Depends: M3/M5. Next: test timeout, refusal, malformed output and stale confirmation without paid calls. Done: recoverable UI, no unconfirmed save or repeated request.
- [ ] **Q4 · Haven't started · Both — Run the integrated clean-start check.** Location: app + tests. Depends: P3/M5/U1/Q2/Q3. Next: start fresh, run full workflow and inspect Git's staged files. Done: end-to-end demo works; synthetic/live status accurate; secrets and private evidence excluded.
- [ ] **V1 · Haven't started · Both — Rehearse and package the demo.** Location: README and demo recording. Depends: Q4. Next: rehearse three minutes: rush → invoice → correction → constrained plan. Done: You explain calculations, teammate explains Meta; actual outputs and limits shown, no claimed real-world savings.
- [ ] **V3 · Haven't started · Both — Submit manually.** Location: hackathon submission page. Depends: V1. Next: verify required fields and upload the agreed demo. Done: confirmation receipt before **November 4, 6 PM Pacific**. Internal submission target: 4 PM Pacific; not an automatic submission promise.

## Later, only after the core flow

- [ ] **A2 · Haven't started · You — Add hourly averages.** Location: `analytics.py`. Depends: D2/P3. Next: divide by observed weekday counts. Done: coverage and denominators displayed; totals and averages clearly distinct.
- [ ] **M6 · Haven't started · Teammate — Add PDF input if needed.** Location: future PDF-to-image handling and evidence page references. Depends: M5/Q4. Next: support one documented PDF path. Done: page evidence preserved and verified. PDF support is not implemented; image-only demo is acceptable.

Other stretch ideas—basket analysis, accounts, deployment—are outside the current checklist. Keep existing task IDs when updating. Earlier M4 is consolidated into M3's stock-reconciliation completion check; U3 into M5's visible evidence trace; V2 into V1's demo package. These are consolidated scope, not completed work.

## Timing and upkeep

Proposed internal targets: **Oct 28–29** run/reproduce and agree inputs; **Oct 30–31** baseline/form/constraints; **Nov 1–2** integrate evidence and test. **Feature freeze November 2** is an internal target, not a promise; use November 3 for fixes/rehearsal and November 4 for final submission checks.

Whenever this assistant uploads **authorized changes to this project**, update this board's statuses from evidence and refresh README's **Next to tackle** with owner, dependency and done check. Teammates should update their own status when starting/finishing and attach the test/result that supports completion. Use GitHub's pencil editor for a small Markdown change (propose a branch/PR when sharing work), or include `TASKS.md` and README in the normal code PR. No paid Project board or integration is required. This upkeep rule does not authorize unrelated uploads, feature work, merges, public release or deployment.

Current data remains fictional with unspecified local timezone. Raw data, SQLite, keys and private evidence remain excluded from Git. Real-data replacement requires separate provenance/permission checks; it is not represented as completed here.
