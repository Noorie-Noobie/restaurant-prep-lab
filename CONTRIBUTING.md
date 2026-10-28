# Working together through GitHub

GitHub shares code and the data-download instructions. **Each laptop runs its own Streamlit app and SQLite database.** No cloud deployment is needed. Keys, invoice uploads, generated databases and virtual environments stay local.

## First-time teammate setup

The repository is **private [Noorie-Noobie/restaurant-prep-lab](https://github.com/Noorie-Noobie/restaurant-prep-lab)**. The owner must grant your GitHub account access before you can clone it.

On macOS/Linux, with Python 3.12 and Git installed:

```sh
git clone https://github.com/Noorie-Noobie/restaurant-prep-lab.git
cd restaurant-prep-lab
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python scripts/download_data.py
PYTHONPATH=src .venv/bin/python -m restaurant_lab.data
PYTHONPATH=src .venv/bin/python -m pytest -q
sh run.sh
```

Open http://127.0.0.1:8501. Stop with Ctrl+C. Next time, only `sh run.sh` is needed. No Meta key is needed to explore the starter.

Windows PowerShell equivalents after cloning:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe scripts/download_data.py
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe -m restaurant_lab.data
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false
```

The current lock file was tested on macOS/Python 3.12; Windows commands and package availability have not been tested. If a pinned wheel is unavailable, report the exact error before changing dependencies.

## One task → one branch → one pull request

Pick a task ID from `TASKS.md`. Arshnoor owns data/analytics/planning; teammate owns UI/Meta. Agree shared interfaces before both edit the same function.

```sh
git switch main
git pull --ff-only origin main
git switch -c feature/a2-hourly-averages
# Make the A2 changes in src/restaurant_lab/analytics.py and relevant tests.
PYTHONPATH=src .venv/bin/python -m pytest -q
git status --short
git diff
# Add specific reviewed files, not secrets or generated data.
git add src/restaurant_lab/analytics.py tests/test_starter.py
git commit -m "A2: add average orders by weekday and hour"
git push -u origin feature/a2-hourly-averages
```

On GitHub, open a pull request into `main`. Include the task ID, what changed, a screenshot if UI changed, and the test result. Ask the other person to review it. Merge after review and passing tests, then both run `git switch main` and `git pull --ff-only origin main`.

If Git reports a conflict, stop and resolve the affected lines together; don't force-push or overwrite the other person's file. Keep branches small so each person can explain the result. Use these branch commands for future work. The starter is shared on `main`; teammate invitations are managed separately by the owner.

## What gets shared

| Shared through Git | Local only |
|---|---|
| App, source, tests, docs, dependency lock | `.venv/`, caches |
| `scripts/download_data.py`, provenance and original license | Downloaded `data/raw/pizzaplace.csv` |
| Explicitly labeled, non-sensitive demo assumptions if later added | SQLite files, `.env`, invoice uploads and review logs |

Never put a real restaurant's export or customer data into this repository without permission and a specific data-handling decision. Synthetic current data remains clearly labeled. It can later be replaced behind the ingestion interface with permitted transaction data; availability and licensing have not yet been established for a real replacement.

## Before a push

1. Run tests; inspect `git diff --cached` and `git status --short`.
2. Confirm there are no keys, `.env`, invoices, private exports, databases or `.venv` in the staged files.
3. Preserve provenance and labels. Don't claim a manual fixture is recorded Meta output.
4. Add dependencies deliberately, keep `pyproject.toml` and tested `requirements.lock.txt` consistent.

A `.gitignore` prevents accidental new additions; it does not remove something already committed. If a secret is ever committed, stop sharing and arrange rotation—deleting the visible line is insufficient.
