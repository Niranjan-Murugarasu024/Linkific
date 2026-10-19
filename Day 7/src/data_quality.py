import pandas as pd
import numpy as np

def quality_summary(df):
    """Return one row per column with missingness, uniqueness and dtype."""
    return pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "missing_count": df.isna().sum(),
        "missing_pct": (df.isna().mean() * 100).round(2),
        "unique_count": df.nunique(dropna=True),
        "duplicate_rows_total": [int(df.duplicated().sum())] * len(df.columns),
    }).rename_axis("column").reset_index()

def numeric_outlier_summary(df, columns=None):
    """IQR-based potential outlier counts; investigate, don't auto-delete."""
    cols = columns or df.select_dtypes(include=np.number).columns.tolist()
    rows = []
    for col in cols:
        s = df[col].dropna()
        if s.empty:
            continue
        q1, q3 = s.quantile([.25, .75])
        iqr = q3 - q1
        low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        rows.append({"column": col, "q1": q1, "q3": q3, "iqr": iqr,
                     "lower_fence": low, "upper_fence": high,
                     "potential_outliers": int(((s < low) | (s > high)).sum())})
    return pd.DataFrame(rows)
