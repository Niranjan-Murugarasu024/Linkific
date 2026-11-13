import os
from sqlalchemy import create_engine, inspect, text
from src.monitoring.logger import get_logger
log = get_logger(__name__)

def source_engine():
    return create_engine(os.getenv("SOURCE_DATABASE_URL", "sqlite:///data/sample/source.db"), future=True)

def initialize_sample_source(engine):
    with engine.begin() as c:
        c.execute(text("CREATE TABLE IF NOT EXISTS source_orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, amount REAL NOT NULL, updated_at TEXT NOT NULL)"))
        if c.execute(text("SELECT COUNT(*) FROM source_orders")).scalar_one() == 0:
            c.execute(text("INSERT INTO source_orders VALUES (1,101,125.50,'2026-11-10T10:00:00'),(2,102,89.99,'2026-11-11T11:30:00'),(3,103,240.00,'2026-11-12T08:15:00')"))

def extract_table(engine, table, watermark_column=None, last_watermark=None, batch_size=1000):
    inspector = inspect(engine)
    if table not in inspector.get_table_names(): raise ValueError(f"Unknown table: {table}")
    columns = [c["name"] for c in inspector.get_columns(table)]
    if watermark_column and watermark_column not in columns: raise ValueError("Invalid watermark column")
    where = f' WHERE "{watermark_column}" > :wm' if watermark_column and last_watermark is not None else ""
    params = {"limit": batch_size, "offset": 0}
    if where: params["wm"] = last_watermark
    query = text(f'SELECT * FROM "{table}"{where} ORDER BY 1 LIMIT :limit OFFSET :offset')
    result = []
    with engine.connect() as conn:
        while True:
            batch = [dict(r._mapping) for r in conn.execute(query, params)]
            if not batch: break
            result.extend(batch); params["offset"] += len(batch)
            if len(batch) < batch_size: break
    log.info("Extracted table=%s rows=%d", table, len(result))
    return result
