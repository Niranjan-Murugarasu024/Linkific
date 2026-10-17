from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
daily = pd.read_csv(ROOT / "data" / "daily_sales.csv", parse_dates=["date"]).set_index("date").sort_index()
monthly = daily.resample("ME").agg(revenue=("revenue", "sum"), active_days=("orders", "sum"))
daily["rolling_7d_revenue"] = daily["revenue"].rolling(7, min_periods=1).mean()
daily["previous_day_revenue"] = daily["revenue"].shift(1)
daily["daily_change"] = daily["revenue"].diff()
monthly.to_csv(reports / "monthly_sales_summary.csv")
daily.to_csv(reports / "daily_time_series_features.csv")
print("Wrote monthly summary and daily time-series features.")
