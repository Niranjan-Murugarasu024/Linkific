"""Reusable data quality checks for tabular data."""


def validate_required_columns(df, required_columns):
    """Raise when a DataFrame is missing one or more required fields."""
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return True

def validate_no_nulls(df, columns):
    """Raise when any of the specified columns contain null values."""
    bad = [col for col in columns if df[col].isna().any()]
    if bad:
        raise ValueError(f"Nulls in required columns: {bad}")
    return True


def validate_unique(df, columns):
    """Raise when the selected columns do not uniquely identify each row."""
    duplicates = df.duplicated(subset=columns, keep=False)
    if duplicates.any():
        raise ValueError(
            f"Duplicate values for {list(columns)} at rows "
            f"{df.index[duplicates].tolist()}."
        )
    return True


def validate_foreign_keys(df, column, reference_values, reference_name):
    """Raise when values in a source key are absent from its reference set."""
    unknown = sorted(set(df[column].dropna()) - set(reference_values))
    if unknown:
        raise ValueError(
            f"Unknown {column} values not found in {reference_name}: {unknown}"
        )
    return True
