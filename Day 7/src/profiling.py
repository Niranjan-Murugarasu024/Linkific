from html import escape
from pathlib import Path
import warnings

def create_profile(df, title, output_path):
    """Create an HTML profile, using a basic summary if YData Profiling is unavailable."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from ydata_profiling import ProfileReport
    except ModuleNotFoundError as exc:
        if exc.name != "ydata_profiling":
            raise
        warnings.warn(
            "ydata-profiling is not installed in this Python environment; "
            "writing a basic HTML summary instead.",
            RuntimeWarning,
            stacklevel=2,
        )
        summary = df.describe(include="all").transpose()
        missing = df.isna().sum().rename("missing_count").to_frame()
        missing["missing_pct"] = (df.isna().mean() * 100).round(2)
        missing["unique_count"] = df.nunique(dropna=True)
        output_path.write_text(
            "<!doctype html><html><head><meta charset=\"utf-8\">"
            f"<title>{escape(title)}</title>"
            "<style>body{font-family:Arial,sans-serif;margin:2rem}"
            "table{border-collapse:collapse;margin:1rem 0}"
            "th,td{border:1px solid #ccc;padding:.4rem;text-align:left}</style>"
            f"</head><body><h1>{escape(title)}</h1>"
            f"<p>Rows: {len(df)} | Columns: {len(df.columns)}</p>"
            "<h2>Descriptive statistics</h2>"
            f"{summary.to_html(escape=True)}"
            "<h2>Missingness and distinct values</h2>"
            f"{missing.to_html(escape=True)}</body></html>",
            encoding="utf-8",
        )
    else:
        profile = ProfileReport(df, title=title, explorative=True, minimal=False)
        profile.to_file(output_path)

    return output_path
