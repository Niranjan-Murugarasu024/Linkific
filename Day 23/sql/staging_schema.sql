-- SQLite DDL equivalent to the tables initialized by the application.
CREATE TABLE ingestion_records (
 id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, source_name TEXT NOT NULL,
 record_number INTEGER NOT NULL, payload TEXT NOT NULL, ingested_at TEXT NOT NULL,
 UNIQUE(run_id, source_name, record_number)
);
CREATE TABLE ingestion_runs (
 run_id TEXT PRIMARY KEY, started_at TEXT, completed_at TEXT, status TEXT, source_summary TEXT
);
