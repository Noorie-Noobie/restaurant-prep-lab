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
