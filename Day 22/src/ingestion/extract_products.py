"""Extract product records from a CSV file."""

from pathlib import Path
from typing import Mapping

import pandas as pd

from src.ingestion.common import read_source_csv


def extract_products(source_config: str | Path | Mapping[str, str]) -> pd.DataFrame:
    """Read product records from a CSV path or source configuration."""
    return read_source_csv(source_config, "products")