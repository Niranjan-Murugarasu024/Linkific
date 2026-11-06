"""Shared CSV ingestion helpers."""

from collections.abc import Mapping
from pathlib import Path

import pandas as pd


def read_source_csv(
    source_config: str | Path | Mapping[str, str],
    source_name: str,
) -> pd.DataFrame:
    """Read a CSV source with clear errors for missing or unreadable files."""
    if isinstance(source_config, Mapping):
        configured_path = source_config.get(f"{source_name}_path")
        if configured_path is None:
            configured_path = source_config.get("path")
        if configured_path is None:
            raise ValueError(
                f"Source configuration must define {source_name}_path or path."
            )
        path = Path(configured_path)
    else:
        path = Path(source_config)

    if path.is_dir():
        path = path / f"{source_name}_sample.csv"
    if not path.is_file():
        raise FileNotFoundError(f"{source_name} source CSV was not found: {path}")

    try:
        return pd.read_csv(path, dtype="string")
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        raise ValueError(f"Could not read {source_name} CSV at {path}: {error}") from error
