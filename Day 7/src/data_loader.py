from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA = PROJECT_ROOT / "data" / "raw"

def load_csv(filename, date_columns=None):
    """Load a CSV and optionally parse one or more date columns."""
    path = RAW_DATA / filename
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    return pd.read_csv(path, parse_dates=date_columns or [])
