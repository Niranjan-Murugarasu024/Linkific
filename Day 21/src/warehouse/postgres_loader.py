import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

def load_dataframe(df, table="integrated_sales", url=None):
    if df is None or df.empty: return "No rows to load"
    url=url or os.getenv("WAREHOUSE_URL")
    if not url:
        Path("data/warehouse").mkdir(parents=True,exist_ok=True)
        path="data/warehouse/integrated_sales.csv"
        df.to_csv(path,index=False)
        return f"Saved CSV warehouse fallback: {path}"
    engine=create_engine(url)
    try:
        df.to_sql(table,engine,if_exists="replace",index=False)
        return f"Loaded {len(df)} rows into {table}"
    finally:
        engine.dispose()
