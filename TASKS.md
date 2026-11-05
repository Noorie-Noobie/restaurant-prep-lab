# Shared checklist · Restaurant Prep Lab

**Owners are proposed:** **You** = Arshnoor, analytics/planning; **Teammate** = app/Meta; **Both** = integration/review. Agree ownership before starting. This file is the single task board; [README → Next to tackle](README.md#next-to-tackle) is its short action summary.

## Next to tackle

**Planner handoff fix:** confirmed Meta stock and submitted manual scenario amounts now live outside temporary widget keys. Reconciled with teammate commit `d9673a5`; 100 tests and offline browser handoff/navigation checks pass. Next: pull latest main and re-record the ending in the normal app with genuine reviewed stock or explicitly manual inputs. The exact all-zero video outcome was not reproduced; navigation-related input loss was reproduced and fixed.

**Presentation update:** Explore/Prep Planner now use a warm restaurant-inspired palette, stronger heading hierarchy and numbered chart sections. Ordinary Chrome visual checks and both prep scenarios passed; calculation and Meta consent logic are unchanged. Both: pull latest main and rehearse current visuals.

This update includes forecasting, the synthetic fixed-recipe planner and offline-tested Meta stock-note integration. No actual Meta response exists. Explore still uses the fictional historical pizza dataset; I3/I6 are not connected. No teammate branch/PR was available at the November 4 repository check.

1. **Teammate · M1/M2/M3:** configure private access/budget, authorize one synthetic request, inspect actual evidence and confirm stock into Prep Planner. Done: live response and the review-to-plan scenario verified. A Team ID alone is not an API credential.
2. **You · V1:** rehearse `docs/DEMO_WALKTHROUGH.md`. Done: explain both resource scenarios and disclose synthetic data and remaining live verification.
3. **Both · I3/I6:** identify the actual teammate UI branch, preserve its work and connect the documented import/analytics interfaces. Done: upload preview/confirm and explicitly selected imported charts reconcile.
4. **Both · release:** resolve `docs/PUBLIC_RELEASE_REVIEW.md`, agree license and separately authorize visibility change; record and submit only after verification. Repository remains private.

- [x] **U1 · Completed · Both — Improve demo presentation.** Location: `app.py`, `presentation.py`, `planner_ui.py`, `.streamlit/config.toml`. Evidence: ordinary Chrome review of Explore and both prep scenarios; 97 regression tests passed. Next: V1 rehearsal; mobile review remains untested.

## How statuses work

| Status | Use it when |
|---|---|
| Working now | The named owner is actively doing it; keep at most one or two active items across the board. |
| Haven't started | Work has not begun, including work blocked on access or a dependency. |
| Almost done | Implementation exists, but the specifically named verification is still outstanding. |
| Completed | The completion check has evidence; check the box and record the result. |

**Working now: none.** I1 backend tests pass; I2/I3/I4 have not started. S4 still awaits user-owned Terminal verification. Only Completed items have checked boxes. Don't mark another person's work started or finished without their update/evidence.

## 1 · Setup and understanding

- [ ] **S4 · Almost done · Both — Keep the local app independent of chat tasks.** Location: `Start App.command`, `run.sh`. Next: user double-clicks `Start App.command` and keeps its Terminal open, then verify health after this chat task ends. Done: Terminal-owned process and Explore remain healthy. Evidence: shell syntax, localhost health, duplicate prevention and nine tests passed in temporary tool execution. Blocker: Terminal UI access denied by Computer Use; durable lifetime is unverified. Start/stop/sleep behavior documented. Local fix only; not yet uploaded.

- [x] **G1 · Completed · Both — Share the starter privately.** Location: this GitHub repository. Done/evidence: private `Noorie-Noobie/restaurant-prep-lab`, starter on `main`, exact initial commit in Git history. Next: S2; existing collaborator `srivastavaaishwarya-analyst` (public profile: Aishwarya Srivastava) has read/write access, verified during UI upload.
- [x] **S0 · Completed · Both — Prepare the local starter.** Location: `run.sh`, `.venv`, `requirements.lock.txt`. Done/evidence: launcher started on localhost and health returned `ok`; stopped after verification. Next: S1/S2 on each person's laptop.
- [ ] **S1 · Haven't started · You — Walk through Explore yourself.** Location: `sh run.sh` → http://127.0.0.1:8501. Depends: S0. Next: filter to one month and compare orders, pizzas and sales. Done: record a bestseller and peak weekday/hour, with date range; explain that revenue is not profit.
- [ ] **S2 · Haven't started · Teammate — Get access and reproduce setup.** Location: GitHub + `CONTRIBUTING.md`. Access verified: `srivastavaaishwarya-analyst` already has read/write permission. Next: clone or pull, install/download/build/test/run. Done: independent app launch and current 97 tests pass.
- [ ] **S3 · Haven't started · Both — Agree one shared input/output contract.** Location: add a compact schema section to README. Depends: S1/S2/I4. Next: write one example containing SKU, ingredient quantity/unit, on-hand stock, minutes and confirmation metadata. Done: both can explain and use the same fields without guessing units.

## 2 · Data and demand · You

- [x] **I5 · Completed · You — Read canonical orders into dashboard analytics.** Location: `import_analytics.py`, `tests/test_import_analytics.py`, `docs/IMPORTED_ANALYTICS.md`. Evidence: all 63 pytest checks pass (57 existing plus 6 new), and disposable import-to-chart demo passes. Next: teammate I6 source selection and chart wiring. Done: full regression suite passes; source/currency isolation, refunds, voids and business-date/local-hour semantics verified. Backend implemented; no app UI claimed.
- [ ] **I6 · Haven't started · Teammate — Select imported data explicitly in Explore.** Location: `app.py`, interface in `docs/IMPORTED_ANALYTICS.md`. Depends: I3/I5. Next: add separate pizza/imported source choice, source/location and business-date selectors. Done: correct labels, empty/error states, no mixed currencies/data, and refreshed chart totals match committed imports. Explore source selection remains unchanged; the separate Prep Planner demo is connected.

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
- [x] **A3 · Completed · You — Build the backend same-weekday baseline.** Location: `forecasting.py`, `docs/FORECASTING.md`, `tests/test_forecasting.py`. Evidence: canonical history replay, last four comparable complete dates, minimum two observations, source/location/unit separation, future-import/correction exclusion and synthetic demo pass. Next: confirm coverage/menu inputs with S3/I4 and connect planner/UI. Backend completion only; real-source integration dependencies remain open.
- [ ] **A4 · Almost done · You — Evaluate the baseline on held-out origins.** Location: `forecasting.py`, `scripts/demo_forecast.py`. Evidence: synthetic rolling-origin evaluation on four Mondays gives MAE 5 items versus 8 for trailing complete dates, four scored each; no real accuracy claim. Depends: I4 and truthful historical coverage/menu/import times. Next: evaluate a permitted representative dataset and record scored/skipped counts. Done: source-specific results and limitations reviewed; bulk imports cannot manufacture historical knowledge.

## 3 · First technical milestone: inputs → deterministic prep

- [x] **P1 · Completed · You — Compute fixed-recipe ingredient requirements.** Location: `planning.py`, `operations_demo.py`. Evidence: 29 demo portions require 7,250 g dough, 2,900 g cheese and 2,320 g sauce; tests cover unit conversion and incompatible units. Next: validate representative restaurant inputs before operational use. One-SKU demo, not seven completed recipes.
- [x] **P2 · Completed · You — Enforce stock and preparation-time limits.** Location: `planning.py`, `tests/test_planning.py`. Evidence: default stock supports 20 portions; 10 minutes supports 5; shared ingredient allocation stays nonnegative. Policy: alphabetical SKU order, whole portions, fixed recipes. Next: review allocation priority with real operators; no optimality claim.
- [x] **U2 · Completed · Both — Wire the narrow planning scenario.** Location: `planner_ui.py`, `app.py`. Evidence: confirmed demo stock form calls forecast and planner; no recipe edits or live writes; two-scenario UI tests pass. User-authorized completion pass integrated the previously unedited app. Next: teammate real-data/source and Meta integration.
- [x] **P3 · Completed · Both — Demonstrate a synthetic complete scenario.** Location: Prep Planner. Evidence: actual Chrome verified 29 expected → 20 feasible / 9 unmet / 900 g cheese shortage, then 3,500 g cheese → 29 feasible / 0 unmet / 58 minutes. Next: rehearse; no live Meta or real restaurant claim.

## 4 · Meta and evidence · Teammate

- [x] **M0 · Completed · Teammate — Prepare the adapter and manual validator only.** Location: `meta.py` (legacy image adapter; current UI uses `meta_stock_ui.py`). Done/evidence: disabled-by-default PNG/JPEG adapter and schema validation exist; disabled-call and invalid-extraction tests pass. **This is not live extraction.** Next: M1/M2.
- [ ] **M1 · Almost done · Teammate — Finish private Meta access and budget setup.** Location: Meta account and app launch environment. Evidence: account sign-in verified; user reports credit form submitted. Latest check: no payment method or API key, credits not displayed. Next: user-controlled billing/key setup and verify budget; configure runtime without exposing secrets. Done: usable access and budget verified. No Team ID, email or credential is stored here.
- [ ] **M2 · Haven't started · Teammate — Verify one actual synthetic stock-note extraction.** Location: `meta_stock.py`, Meta Evidence. Depends: M1 and explicit request/spend consent. Next: submit only the fixed synthetic counted-stock note once. Done: actual response/model/request ID, usage and exact source quotes reviewed; no mocked output presented as live. Image/PDF extraction is outside this narrow milestone.
- [ ] **M3 · Almost done · Teammate — Verify review and planner handoff with actual Meta output.** Location: `meta_stock.py`, `meta_stock_ui.py`, `planner_ui.py`. Implemented: synthetic counted-stock note extraction, exact source-quote validation, correction/confirmation and session-only planner handoff; mocked tests pass. Next: M2 live verification, then persistent audited storage if required. Blockers: no credential/access/spend authorization; no actual response, durable storage or invoice purchase reconciliation. No unconfirmed values enter planner.
- [ ] **M5 · Haven't started · Teammate — Connect tools and a grounded explanation.** Location: `meta.py`, `app.py`. Depends: P3/M3. Next: expose an allowlisted deterministic planning function, show its arguments/result, then request an evidence-linked explanation. Done: judges can follow source → confirmed stock → actual tool result → explanation; prose cannot override feasibility; reruns do not repeat paid requests.

## 5 · Verification and demo · Both

- [x] **Q1 · Completed · Both — Run starter automated checks.** Location: `tests/test_starter.py`, `VALIDATION.md`. Done/evidence: nine tests pass; compilation, fresh dataset download and localhost health pass. One upstream chart deprecation warning. Next: add checks alongside new features; this does not prove visual quality or live Meta success.
- [ ] **U1 · Almost done · Teammate — Complete visual review of all three screens.** Evidence: actual Chrome verified two Prep Planner scenarios; AppTest checks the Meta form. Next: inspect current Meta Evidence, Explore and narrow-window layout after clean setup. Done: readable labels, no clipping and accurate synthetic/live status on every screen. Full current visual QA remains outstanding.
- [x] **Q2 · Completed · You — Verify forecast and constraint boundaries.** Location: `tests/test_forecasting.py`, `tests/test_planning.py`. Evidence: leakage, late corrections, unknown/missing coverage, recipes, units, stock and time limits pass within the 97-test suite. Next: real-source evaluation remains A4, not a tested accuracy claim.
- [x] **Q3 · Completed · Both — Verify offline Meta failure and confirmation handling.** Location: `tests/test_meta_stock.py`. Evidence: mocked timeout, refusal, malformed output, stale source, review and repeat-request prevention pass. Next: actual service verification M2/M3; these tests do not constitute live model evidence.
- [ ] **Q4 · Haven't started · Both — Run the integrated clean-start check.** Location: app + tests. Depends: P3/M5/U1/Q2/Q3. Next: start fresh, run full workflow and inspect Git's staged files. Done: end-to-end demo works; synthetic/live status accurate; secrets and private evidence excluded.
- [ ] **V1 · Almost done · Both — Rehearse and package the demo.** Location: `docs/DEMO_WALKTHROUGH.md`. Evidence: three-minute script prepared, actual deterministic flow verified. Next: rehearse and record after reviewing live Meta limitations. Done: agreed recording under three minutes with accurate evidence and limits. No video recorded.
- [ ] **V3 · Haven't started · Both — Submit manually.** Location: hackathon submission page. Depends: V1. Next: verify required fields and upload the agreed demo. Done: confirmation receipt before **November 4, 6 PM Pacific**. Internal submission target: 4 PM Pacific; not an automatic submission promise.

## Later, only after the core flow

- [ ] **A2 · Haven't started · You — Add hourly averages.** Location: `analytics.py`. Depends: D2/P3. Next: divide by observed weekday counts. Done: coverage and denominators displayed; totals and averages clearly distinct.
- [ ] **M6 · Haven't started · Teammate — Add PDF input if needed.** Location: future PDF-to-image handling and evidence page references. Depends: M5/Q4. Next: support one documented PDF path. Done: page evidence preserved and verified. PDF support is not implemented; current demo uses a counted-stock text note.

Other stretch ideas—basket analysis, accounts, deployment—are outside the current checklist. Keep existing task IDs when updating. Earlier M4 is consolidated into M3's stock-reconciliation completion check; U3 into M5's visible evidence trace; V2 into V1's demo package. These are consolidated scope, not completed work.

## Timing and upkeep

Proposed internal targets: **Oct 28–29** run/reproduce and agree inputs; **Oct 30–31** baseline/form/constraints; **Nov 1–2** integrate evidence and test. **Feature freeze November 2** is an internal target, not a promise; use November 3 for fixes/rehearsal and November 4 for final submission checks.

Whenever this assistant uploads **authorized changes to this project**, update this board's statuses from evidence and refresh README's **Next to tackle** with owner, dependency and done check. Teammates should update their own status when starting/finishing and attach the test/result that supports completion. Use GitHub's pencil editor for a small Markdown change (propose a branch/PR when sharing work), or include `TASKS.md` and README in the normal code PR. No paid Project board or integration is required. This upkeep rule does not authorize unrelated uploads, feature work, merges, public release or deployment.

Current data remains fictional with unspecified local timezone. Raw data, SQLite, keys and private evidence remain excluded from Git. Real-data replacement requires separate provenance/permission checks; it is not represented as completed here.

- [ ] **M4 · Almost done · Both — Preserve confirmed stock across navigation.** Local fix: `meta_stock_ui.py`, `planner_ui.py`; three new regression tests. Evidence: 100 offline tests pass. Remaining: teammate replay using genuine reviewed stock; offline browser handoff/navigation checks passed. Next: verify 10,000 g dough / 2,000 g cheese / 3,000 g sauce before calculating 20 feasible portions. No new live extraction needed if a valid reviewed response remains in the session.
