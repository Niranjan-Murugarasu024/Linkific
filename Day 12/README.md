\# Day 12 — E-Commerce ETL Pipeline



\## Overview



This project implements a multi-source ETL pipeline using Python, Pandas, SQLAlchemy, REST APIs, and PostgreSQL.



It demonstrates batch data engineering, data cleaning, enrichment, incremental loading, upserts, logging, retry logic, and optional failure email alerts.



\## Architecture



\*\*Sources:\*\* DummyJSON Products API, PostgreSQL customers, CSV sales transactions.



\*\*Extract:\*\* Retrieve paginated API records, database rows, and CSV transactions.



\*\*Transform:\*\* Validate data types, remove invalid and duplicate records, enrich sales with customer and product information, and calculate total revenue.



\*\*Load:\*\* Upsert products and sales into PostgreSQL warehouse tables. Maintain incremental-load watermarks.



\*\*Monitoring:\*\* Record pipeline executions in `etl\_runs`, write logs to `logs/pipeline.log`, and optionally send email failure notifications.



\## Technology Stack



\- Python 3.11

\- Pandas

\- SQLAlchemy

\- PostgreSQL

\- Psycopg 3

\- Requests

\- python-dotenv



\## Setup



1\. Create a PostgreSQL database named `etl\_demo`.

2\. Create a Python virtual environment.

3\. Install packages with `pip install -r requirements.txt`.

4\. Copy `.env.example` to `.env`.

5\. Configure `DATABASE\_URL`.



\## Run



Full refresh:



`python -m src.pipeline --full`



Incremental run:



`python -m src.pipeline`



\## Verification



Run these queries in pgAdmin4:



```sql

SELECT \* FROM fact\_sales;

SELECT \* FROM product\_catalog;

SELECT \* FROM etl\_watermarks;

SELECT \* FROM etl\_runs ORDER BY run\_id DESC;

```



\## Incremental Loading



The pipeline stores the maximum successfully processed sales timestamp in `etl\_watermarks`.



Subsequent incremental runs select transactions with timestamps greater than or equal to the previous watermark. PostgreSQL upserts prevent duplicate order IDs.



The full-load mode replaces the sales table contents and resets the watermark to the latest timestamp in the refreshed dataset.



\## Error Handling



\- HTTP retry logic with exponential backoff

\- API request timeouts

\- Input schema and data validation

\- PostgreSQL transactions

\- Pipeline execution logging

\- Optional SMTP failure notifications



\## Limitations



\- Incremental extraction uses a timestamp watermark, not database-log CDC.

\- Hard deletes from source systems are not propagated automatically.

\- The CSV is read in full before incremental filtering.

\- API extraction has a configured maximum page count.

\- Transformations use in-memory Pandas DataFrames.

\- The project does not include automated unit tests or a workflow scheduler.

\- Monetary calculations should use a decimal-safe approach for financial production workloads.



\## Learning Outcomes



\- Design an ETL architecture

\- Extract from multiple source types

\- Apply data cleaning and enrichment

\- Implement PostgreSQL upserts

\- Maintain incremental-load checkpoints

\- Handle failures and record execution status

\- Query analytics-ready warehouse tables



