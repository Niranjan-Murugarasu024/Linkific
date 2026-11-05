# Day 21 — Multi-Source Data Collection & Integration

A beginner-friendly, runnable Python data engineering project that collects records from REST APIs, databases, local files, a webpage, and optionally SFTP; converts data formats; standardizes schemas; integrates records; records lineage; and loads the result into PostgreSQL or a local CSV fallback.

## Learning objectives
- Collect from 3 REST APIs, SQLite, optional PostgreSQL, CSV, JSON, Excel, webpage scraping, and optional SFTP.
- Handle JSON-to-DataFrame, XML parsing, Parquet and Avro output.
- Apply schema mapping, cleaning, key-based merging, and conflict resolution.
- Orchestrate stages with retries, logs, lineage, and an interval scheduler.
- Load integrated sales into a PostgreSQL warehouse.

## Requirements
- Python 3.10+ recommended
- PostgreSQL 14+ optional; SQLite/CSV fallback works without it
- Internet access for API and webpage collection
- Windows PowerShell examples below

## Setup (Windows PowerShell)
```powershell
Set-Location "E:\day21_multi_source_collection"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```
If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

## Run
```powershell
python -m src.pipeline.orchestrator
```
The pipeline creates sample files, collects APIs, scrapes example.com, reads SQLite, performs format examples, integrates sales/customer data, writes lineage, and loads the warehouse.

## PostgreSQL warehouse (optional)
Create a database named `day21_warehouse`, then update `WAREHOUSE_URL` in `.env`:
```text
WAREHOUSE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/day21_warehouse
```
The pipeline writes table `integrated_sales`. If `WAREHOUSE_URL` is empty, it writes `data/warehouse/integrated_sales.csv`.

For an optional source PostgreSQL database, set `SOURCE_DATABASE_URL`. The collector introspects public tables and attempts to read them. Use a disposable practice database only.

## Sources
| Source | Implementation | Output |
|---|---|---|
| JSONPlaceholder users | REST API | `data/raw/jsonplaceholder_users.json` |
| DummyJSON products | REST API | `data/raw/dummyjson_products.json` |
| REST Countries | REST API | `data/raw/restcountries.json` |
| SQLite | Generated source DB | `data/raw/sqlite_customers.csv` |
| PostgreSQL | Optional source URL | DataFrame |
| CSV | Sample customer file | DataFrame |
| Excel | Sample sales workbook | DataFrame |
| JSON | Sample inventory file | DataFrame |
| Web | Example.com HTML | `data/raw/scraped_page.csv` |
| SFTP | Optional Paramiko download | `data/raw/<remote filename>` |

## Format examples
```powershell
python examples/json_to_dataframe.py
python examples/xml_parser.py
python examples/parquet_conversion.py
python examples/avro_conversion.py
```
Parquet requires PyArrow; Avro uses fastavro. The sample XML parser uses lxml.

## Pipeline stages
1. Collect APIs and local/remote source data.
2. Save raw API payloads and source files.
3. Standardize customer columns and normalize emails.
4. Deduplicate by `customer_id`.
5. Left-join sales to customer records.
6. Write processed datasets and `data/processed/lineage.json`.
7. Load to PostgreSQL or CSV fallback.

## Scheduling
Run a simple interval scheduler (default hourly):
```powershell
python -m src.pipeline.scheduler
```
Stop with Ctrl+C. For production, use Airflow, Prefect, or Windows Task Scheduler; this interval loop is for learning and does not persist job state.

## Logs and error handling
- Logs are printed to console and `logs/pipeline.log`.
- API requests retry up to three times with increasing delay.
- SFTP and source PostgreSQL are optional and skip when not configured.
- The pipeline raises errors after retries are exhausted; review logs before rerunning.

## Tests
```powershell
pip install pytest
pytest
```

## Data quality and limitations
- Public APIs can change, rate-limit, or be unavailable; the pipeline logs and raises on API failure.
- Example.com is used for a safe HTML parsing demonstration, not large-scale scraping.
- SFTP requires a server and credentials supplied by you.
- Source PostgreSQL introspection is a generic demo; adapt table allowlists and credentials before real use.
- The customer merge demonstrates a stable-key strategy. Production pipelines should define source priority, null policy, duplicate policy, schema contracts, and PII access controls explicitly.

## Suggested meeting explanation
“This project demonstrates a multi-source ingestion pipeline. I collected data from three REST APIs, generated CSV/Excel/JSON files, read a SQLite database, and included optional PostgreSQL and SFTP connectors. I normalized schemas, cleaned and deduplicated customer records, joined sales to customers using customer_id, converted sample data to Parquet and Avro, parsed XML, logged each stage, generated lineage metadata, and loaded the integrated output into PostgreSQL or a CSV fallback.”


## Apache Airflow integration (added)
The project now includes `dags/day21_multi_source_pipeline.py`, an Airflow DAG with four tasks: `collect_sources` → `transform_and_integrate` → `write_data_lineage` → `load_warehouse`. It runs daily (`@daily`), retries failed tasks twice, and exposes task-level logs and state in the Airflow UI. The existing `src/pipeline/orchestrator.py` remains the standalone Python entry point; Airflow is an additional orchestration layer.

### Run Airflow with Docker Compose (Windows PowerShell)
From the project root, ensure Docker Desktop is running, then:
```powershell
docker compose -f docker-compose.airflow.yaml up -d
docker compose -f docker-compose.airflow.yaml logs -f airflow
```
Open `http://localhost:8080`. Airflow standalone prints a generated login/password in its container logs. Sign in, find `day21_multi_source_data_pipeline`, toggle it on, and trigger it. Stop it with:
```powershell
docker compose -f docker-compose.airflow.yaml down
```
The compose file is a learning/local setup. For a real deployment, use the official Airflow Compose stack with PostgreSQL metadata DB, a supported executor, secrets management, and separate workers.

### Airflow task graph
```text
collect_sources
      ↓
transform_and_integrate
      ↓
write_data_lineage
      ↓
load_warehouse
```

### Important fixes in this revision
- Fixed the malformed `os.getenv` expression in the optional PostgreSQL source collector.
- Standardized the warehouse table and CSV fallback names to `integrated_sales`.
- Added an Airflow DAG, Docker Compose learning setup, and Airflow dependency notes.
