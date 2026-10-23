import pandas as pd
from sqlalchemy import create_engine
from src.config import sqlalchemy_url

EXPECTED = {"event_id", "event_date", "region", "orders_count", "sales_amount"}

def transform_csv(input_path: str) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    missing = EXPECTED - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {sorted(missing)}")
    df = df[list(sorted(EXPECTED))].copy()
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df["orders_count"] = pd.to_numeric(df["orders_count"], errors="coerce")
    df["sales_amount"] = pd.to_numeric(df["sales_amount"], errors="coerce")
    df["region"] = df["region"].astype("string").str.strip()
    df = df.dropna(subset=["event_id", "event_date", "region", "orders_count", "sales_amount"])
    df = df[(df.orders_count >= 0) & (df.sales_amount >= 0)]
    df["orders_count"] = df["orders_count"].astype("int64")
    return df.drop_duplicates(subset=["event_id"], keep="last")

def load_dataframe(df: pd.DataFrame) -> int:
    engine = create_engine(sqlalchemy_url(), pool_pre_ping=True)
    with engine.begin() as conn:
        df.to_sql("daily_sales_staging", conn, if_exists="append", index=False, chunksize=500, method="multi")
    engine.dispose()
    return len(df)

def run(input_path: str = "data/sales_events.csv") -> int:
    df = transform_csv(input_path)
    if df.empty:
        print("No valid records to load.")
        return 0
    count = load_dataframe(df)
    print(f"Loaded {count} cleaned records.")
    return count

if __name__ == "__main__":
    run()
