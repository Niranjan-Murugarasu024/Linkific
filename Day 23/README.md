# Day 23 – Multi-Source Automated Data Ingestion Framework

## Objective
Collect data from APIs, a practice website, local files, and a database. Preserve raw payloads, load a staging database, isolate source failures, and record ingestion metadata.

## Architecture
REST APIs / scraper / files / source DB → source collectors → orchestrator → raw JSON + staging DB → logs, quarantine and run metadata.

## Windows PowerShell setup
```powershell
cd E:\Linkific\day23_ingestion_framework
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python -m src.main
```
If activation is blocked:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```
Run tests with `pytest -v`.

## Sources
- JSONPlaceholder posts: page/limit pagination.
- DummyJSON products: skip/limit pagination.
- REST Countries: country metadata.
- Books to Scrape: static HTML product scraping (practice site).
- Files: CSV, Excel, JSON and Parquet; batch reading.
- Database: SQLAlchemy source extraction. A sample SQLite source DB is initialized automatically.

Public demo APIs do not require credentials. The API client supports an optional bearer token through `DEMO_API_TOKEN`; do not invent credentials for public APIs. The example scraper uses a practice website. Check robots.txt, terms and request limits before scraping other sites.

## Outputs
- `data/raw/<source>/<run_id>.json`: preserved source payload, timestamp and count.
- `data/staging/ingestion.db`: `ingestion_records` and `ingestion_runs`.
- `data/quarantine/`: metadata for failed sources.
- `logs/ingestion.log`: execution log.

## Incremental database extraction
The extractor accepts `watermark_column` and `last_watermark`:
```python
rows = extract_table(engine, "source_orders",
                     watermark_column="updated_at",
                     last_watermark="2026-11-11T00:00:00")
```
Persist the last successfully committed watermark in a durable metadata table in a production version. Update it only after the corresponding staging load commits. For equal timestamps, use a compound watermark (timestamp + primary key) to avoid skipped records.

## Reliability notes
- HTTP retries cover transient connection errors and status codes 429, 500, 502, 503 and 504. `Retry-After` is respected when supplied.
- Pagination is source-specific; the examples show page/limit and skip/limit.
- The pipeline continues independent sources after one source fails.
- The staging uniqueness key prevents duplicate writes for the same run/source/record number. Cross-run business deduplication is a later data-quality concern.
- The included rate limiter is process-local, not distributed.
- Default staging uses SQLite. The included DDL/loader use SQLite-specific `AUTOINCREMENT` and `INSERT OR IGNORE`; adapt them to PostgreSQL (`IDENTITY` and `ON CONFLICT DO NOTHING`) before changing `STAGING_DATABASE_URL`.
- This is an educational baseline, not a certified production or HIPAA-compliant system.

## Airflow
Airflow is optional. Native Windows execution is unsupported; use Docker Desktop or WSL2. To run it with Docker Desktop, start Docker Desktop, then from the repository root run:

```powershell
docker compose up --build -d
docker compose logs -f airflow
```

Wait for the standalone Airflow service to start. Its initial login credentials are printed in the logs. Open `http://localhost:8080`, unpause `day23_multi_source_ingestion_detailed`, and trigger it manually. The Compose setup mounts this repository's `airflow/` directory as the DAG folder and keeps Airflow's metadata database in a Docker volume. Ingestion data and logs are written to the project folders.

Stop Airflow with `docker compose down`; use `docker compose down -v` only if you also intend to delete the persistent Airflow metadata volume. The standalone DAG file is also suitable for an existing Airflow environment, provided the project root is on `PYTHONPATH` and is the task working directory.

## Deliverables
[x] 3 API collectors [x] pagination [x] timeout/retry/rate-limit response handling
[x] scraper [x] CSV/Excel/JSON/Parquet batches [x] SQLAlchemy extraction and watermark parameters
[x] orchestrator [x] raw data [x] staging DB [x] quarantine [x] logs [x] tests [x] optional Airflow DAG
