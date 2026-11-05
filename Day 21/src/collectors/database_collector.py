import sqlite3
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from src.utils.logger import get_logger
log = get_logger("database")

def collect_sqlite():
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect("data/raw/source.db")
    con.execute("CREATE TABLE IF NOT EXISTS customers(customer_id INTEGER, name TEXT, email TEXT)")
    con.execute("DELETE FROM customers")
    con.executemany("INSERT INTO customers VALUES(?,?,?)", [
        (1,"Asha","asha@example.com"),(2,"Kiran","kiran@example.com"),(3,"Meera","meera@example.com")
    ])
    con.commit()
    df = pd.read_sql_query("SELECT * FROM customers", con)
    df.to_csv("data/raw/sqlite_customers.csv", index=False)
    con.close()
    log.info("Collected %d SQLite customers", len(df))
    return df

def collect_postgres(database_url=None):
    database_url = database_url or os.getenv("SOURCE_DATABASE_URL")
    if not database_url:
        log.warning("SOURCE_DATABASE_URL absent; skipping source PostgreSQL collection")
        return pd.DataFrame()
    engine = create_engine(database_url)
    try:
        with engine.connect() as conn:
            tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")).fetchall()
        frames=[]
        for (table,) in tables:
            try:
                frames.append(pd.read_sql_query(text(f'SELECT * FROM "{table}"'), engine))
            except Exception as e:
                log.warning("Skipping table %s: %s", table, e)
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    finally:
        engine.dispose()
