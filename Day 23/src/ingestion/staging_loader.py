from pathlib import Path
from datetime import datetime, timezone
import json, os
from sqlalchemy import create_engine, text

def _default(value):
    return value.isoformat() if hasattr(value, "isoformat") else str(value)

def save_raw(source, records, run_id):
    folder = Path("data/raw") / source; folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{run_id}.json"
    path.write_text(json.dumps({"source":source,"run_id":run_id,"ingested_at":datetime.now(timezone.utc).isoformat(),
                                "record_count":len(records),"data":records}, indent=2, default=_default), encoding="utf-8")
    return str(path)

def staging_engine():
    Path("data/staging").mkdir(parents=True, exist_ok=True)
    return create_engine(os.getenv("STAGING_DATABASE_URL", "sqlite:///data/staging/ingestion.db"), future=True)

def initialize_staging(engine):
    with engine.begin() as c:
        c.execute(text("CREATE TABLE IF NOT EXISTS ingestion_records (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, source_name TEXT NOT NULL, record_number INTEGER NOT NULL, payload TEXT NOT NULL, ingested_at TEXT NOT NULL, UNIQUE(run_id,source_name,record_number))"))
        c.execute(text("CREATE TABLE IF NOT EXISTS ingestion_runs (run_id TEXT PRIMARY KEY, started_at TEXT, completed_at TEXT, status TEXT, source_summary TEXT)"))

def load_records(engine, source, records, run_id):
    now = datetime.now(timezone.utc).isoformat()
    with engine.begin() as c:
        for i, record in enumerate(records, 1):
            c.execute(text("INSERT OR IGNORE INTO ingestion_records (run_id,source_name,record_number,payload,ingested_at) VALUES (:r,:s,:n,:p,:t)"),
                      {"r":run_id,"s":source,"n":i,"p":json.dumps(record,default=_default),"t":now})
