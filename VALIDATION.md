# Starter verification · 2026-10-28

- Python 3.12.3; isolated `.venv` installed from official PyPI. No global packages installed.
- `PYTHONPATH=src .venv/bin/python -m pytest -q`: **7 passed** in 3.23 seconds. One upstream Streamlit/pandas deprecation warning; no test failures.
- `PYTHONPATH=src .venv/bin/python -m compileall -q app.py src tests`: passed.
- `sh run.sh`: Streamlit started on **127.0.0.1:8501**. `/_stcore/health` returned `ok`. Test server stopped afterward; no persistent service left running.
- Full SQLite ingest: **49,574 lines, 21,350 orders, 91 SKUs, 358 observed dates, $817,860.05**. Raw CSV hash matches provenance. SQLite integrity check passed.
- Streamlit AppTest ran Explore, Prep Planner and Meta Evidence without exceptions.
- Tests confirm repeated identical item purchases remain separate while rush counts count each order once.
- Test confirms disabled Meta adapter sends no network request.
- No model inference, credentials, billing, credit redemption, publication, remote repository or submission performed. Live Meta integration is **not tested**.
- Visual browser QA remains unperformed. On follow-up, computer-use inventory returned no browser surfaces; creating an isolated hidden in-app browser returned `Browser is not available: iab`. Existing native Chrome was left untouched to avoid disturbing user activity. Interaction/render smoke passed through Streamlit AppTest, which does not verify visual clipping or typography.

Network downloads and localhost binding initially required leaving the restricted execution sandbox; approved scoped checks then succeeded. No remaining environment blocker.

## GitHub preparation follow-up · 2026-10-28

- Local Git repository initialized on `main`. No remote configured, no commit/push, and no external repository or invitations created.
- Added `CONTRIBUTING.md` with macOS/Linux and Windows teammate commands plus small feature-branch/pull-request workflow. Windows instructions are untested.
- Added checksum-verified `scripts/download_data.py`. Original CSV stays local and is excluded from Git. Source license/provenance and downloader are shareable.
- Fresh network download through the new downloader passed in a disposable temporary directory, including the pinned checksum. Existing raw data was untouched.
- Nine tests passed in 4.47 seconds; compilation passed. Tests cover checksum rejection and offline reuse without overwriting raw data. Existing full-data and UI tests also pass.
- Checked 23 Git candidate files for common credential patterns: zero matches. No private export, invoice or generated-database candidates found. This is a scoped pattern scan, not a guarantee against every possible secret.
- `git check-ignore` confirmed `.env`, `.env.local`, `.venv`, generated SQLite, raw CSV, invoice uploads and Streamlit secrets are ignored. Empty `.env.example` remains shareable.
- GitHub CLI read-only status succeeded for Noorie-Noobie using existing keychain authentication. Initial restricted-network status was misleading; network-enabled verification confirmed authentication. No credentials were changed or printed unmasked.
- Connector lookup returned 404 and authenticated CLI could not resolve `Noorie-Noobie/restaurant-prep-lab`. No accessible matching repository was found; this does not prove nonexistence under unavailable permissions.
- Remote readiness remains pending parent/user confirmation of private repository creation and exact teammate handle/access. No remote write attempted.

## Approved GitHub publication · 2026-10-28

The user subsequently authorized private repository creation and starter upload. The private repository is https://github.com/Noorie-Noobie/restaurant-prep-lab. The earlier “pending approval / no remote” entries above describe the prior preparation stage. No teammate has been invited; a handle is still needed.

Before the initial commit, nine tests passed in 3.77 seconds and 23 candidate files had zero common credential-pattern or private-file matches. Ignore rules were reconfirmed. Raw CSV, generated SQLite, credentials, virtual environment and invoice/evidence contents are excluded. The repository holds the verified download script and original attribution/license. Live Meta and deployment remain unperformed.

## Canonical import backend · 2026-10-30

Audit found pizza-only columns and forced quantity/status, whole-file database replacement, missing operational confirmation/stock and placeholder planning. The new importer is independent; those legacy pizza assumptions remain limited to that demo. Existing user edits were preserved.

Added canonical CSV v1 contract, strict preview and explicit commit API, config/currency/timezone validation, stable identity, versioned snapshot updates, import audit/history and atomic rollback. Dedicated default database: `data/processed/canonical_orders.sqlite`; the original app still uses its pizza database. New raw samples are explicitly synthetic, with no vendor-export or real-PII claim.

57 tests passed (48 new parameterized backend cases plus 9 original cases), 3.89s; one upstream Streamlit/pandas chart warning. Verified repeated distinct item lines, exact and overlapping reimports, partial refunds/void corrections, decimal quantities/currencies, DST/nonexistent timestamps, config mismatch, stale preview/version rejection, mid-transaction and initial-transaction rollback, preservation of unrelated tables and rejection of another application's DB. Test databases were temporary.

Read-only fixture preview passed: 1 order, 2 lines, quantity/fulfilled 4 each, gross 4000 USD cents, discounts 400, refunds 500, net 3100. No canonical database was created by preview; implementation used no app server, vendor/Meta calls, credentials or installs.

Not verified/implemented: real vendor mapping, UI confirmation, live synchronization, restaurant authorization, backup/restore/migrations, production performance, forecast/planner or live Meta. The confirmation API is not an authentication system.

## Imported analytics backend · November 2 (backend milestone)

Finder Keep Downloaded was selected for the existing project only. Git/current source files became readable; remote fetch succeeded and main still matches 4f646ece. Original launcher changes preserved. No AGENTS.md found in the project-area search.

Six new read-only analytics checks pass via system Python unittest (0.069s). Fixture demo committed only to a disposable temporary SQLite file and generated /tmp/restaurant-import-analytics-demo.html; expected net 3100 USD cents and one Thursday 01:00 order. Full pytest attempt timed out after 45 seconds while environment hydration remained active; no new full-suite pass claimed. No app server, Meta, POS, credentials, push or deployment. App/upload UI untouched; visual verification of new static demo blocked: supported browser opening returned `Browser is not available: chrome`.

Hydration subsequently completed: Finder's folder progress and iCloud activity indicators disappeared. Final full regression run: **63 passed**, 4.16 seconds, one existing Streamlit/pandas deprecation warning. This supersedes the earlier load timeouts. All started test/check processes exited; no server started. `git diff --check` and syntax parsing passed. I5 is Completed; I6 UI remains Haven't started. Analytics milestone prepared for the authorized upload.
