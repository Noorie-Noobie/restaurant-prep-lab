#!/bin/sh
set -eu
cd "$(dirname "$0")"
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
if [ ! -x .venv/bin/python ]; then
  echo "Run the new-computer setup in README.md first."
  exit 1
fi
if [ ! -f data/raw/pizzaplace.csv ]; then
  echo "Download the public demo dataset first: .venv/bin/python scripts/download_data.py"
  exit 1
fi
if [ ! -f data/processed/restaurant.sqlite ]; then
  .venv/bin/python -m restaurant_lab.data
fi
exec .venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false
