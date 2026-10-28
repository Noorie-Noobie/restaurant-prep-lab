from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = ROOT / "data/raw/pizzaplace.csv"
DB_PATH = ROOT / "data/processed/restaurant.sqlite"
# Source gives local wall-clock times without a timezone. Do not invent UTC/SF.
SOURCE_TIMEZONE = "unspecified_local"
