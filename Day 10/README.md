# Day 10 — Python, PostgreSQL, SQLAlchemy and ETL

## Deliverables
- psycopg2 connection, parameterized query, fetch, update and transaction examples.
- Pandas query, chunk reading, CSV export and `to_sql` examples.
- SQLAlchemy 2.x ORM models and query/create examples.
- CSV → validate/transform → PostgreSQL pipeline.
- Public API → transform → idempotent PostgreSQL upsert pipeline.
- Incremental extraction example with a watermark.
- Sample CSV, transformation test, and integration guide.

## Prerequisites
Python 3.11+ recommended, PostgreSQL running, and the `ecommerce_practice` database/tables from Day 8.

## Windows PowerShell setup
```powershell
Set-Location "E:\Day-10-Python-PostgreSQL-Pipeline"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```
Update `.env` with local PostgreSQL credentials. Never commit `.env`.

## Run examples
Run these from the project root:
```powershell
python -m src.psycopg2_basics
python -m src.pandas_sql
python -m src.sqlalchemy_orm
python -m src.etl_csv_to_postgres
python -m src.etl_api_to_postgres
python -m src.incremental_load
```

Before CSV loading, execute `sql/01_pipeline_tables.sql` in pgAdmin to create the target table and its check constraint/index. The API ETL creates `api_posts` automatically and calls `https://jsonplaceholder.typicode.com/posts`; it requires internet access but no API key.

## Run transformation tests
```powershell
python -m pytest -q
```

## Learning checklist
Understand parameterized queries, transactions, engine pooling, ORM relationships, DataFrame chunks, validation, idempotent upserts, and incremental watermarks.

## Limitations
The sample watermark cannot detect updates to old orders. Production pipelines should use `updated_at`, CDC, or another robust change tracking mechanism. Sample data is fictional.
