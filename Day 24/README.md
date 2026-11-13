# Day 24 — E-commerce Data Warehouse (PostgreSQL)

A complete, runnable Day 24 data-engineering project covering warehouse schema design, a date dimension, dimension loading, SCD Type 2, fact loading, and validation. The project uses PostgreSQL 17 and includes a deterministic sample e-commerce source dataset.

## What you will build

- A `source` schema containing the source-system tables and sample CSV-loaded records.
- A `dw` star schema with `dim_date`, `dim_customer`, `dim_product`, `dim_region`, and `fact_sales`.
- A date hierarchy with calendar and April–March fiscal attributes, weekend flags, and configurable holiday flags.
- Customer SCD Type 2 history; product and region dimensions use Type 1 upserts.
- An idempotent fact load at one row per order line, with dimension surrogate-key lookups and sales / cost / profit calculations.
- Automated row-count, referential-integrity, dimensional, date-coverage, and measure-reconciliation checks. Reports are written to `reports/` in JSON and TXT formats.

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the data-flow diagram, star-schema ERD, fact grain, SCD strategy, and measure definitions. See [`docs/data_dictionary.md`](docs/data_dictionary.md) for table and column meanings.

## Requirements

- Python 3.10 or later (Python 3.11 / 3.13 recommended).
- PostgreSQL 17, either already installed locally or started using Docker Compose.
- Windows PowerShell commands below are used in the walkthrough; the Python scripts are cross-platform.

## 1. Extract the ZIP and open PowerShell

Change directory to the extracted project folder:

```powershell
Set-Location "E:\DataEngineering\day24_ecommerce_data_warehouse"
```

Use your actual extraction path if it differs.

## 2. Create and activate a virtual environment

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run this for the current terminal only and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. Configure PostgreSQL

### Option A — Docker (standalone database)

Copy the environment template and start PostgreSQL 17:

```powershell
Copy-Item .env.example .env
docker compose up -d
```

The default database is `day24_warehouse`, user is `postgres`, and password is `postgres`. These are local learning defaults; change the password before exposing the database beyond your machine.

### Option B — Existing local PostgreSQL 17

Create a database named `day24_warehouse` in pgAdmin (or with `CREATE DATABASE day24_warehouse;`). Copy `.env.example` to `.env` and edit `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD` to match your local server. Do not run Docker Compose if you are using your existing server on the same port.

## 4. Generate or inspect the supplied source data

The CSV files are already included in `data/source/`. They contain regions, customers, products, orders, order lines, and a small sample holiday calendar. To regenerate the same deterministic dataset:

```powershell
python scripts/generate_sample_data.py
```

## 5. Create schemas and load source tables

```powershell
python scripts/setup_database.py
```

This creates the `source` and `dw` schemas, tables, keys, constraints and indexes, then loads the CSV files into the `source` schema. Re-running setup reloads the source tables; it does not truncate the warehouse dimensions or fact table.

## 6. Run the warehouse ETL

```powershell
python scripts/run_pipeline.py
```

Expected sequence:

1. Upsert region dimension.
2. Upsert product dimension (SCD Type 1).
3. Load customer dimension (SCD Type 2).
4. Generate / refresh the date dimension.
5. Resolve dimension surrogate keys and load `dw.fact_sales`.
6. Execute validation checks and save a report in `reports/`.

The fact load uses `source_order_item_id` as a unique key. Re-running the pipeline should not duplicate fact rows.

## 7. Demonstrate SCD Type 2

Run the following commands after the initial successful ETL:

```powershell
python scripts/show_customer_history.py
python scripts/demo_scd2_change.py
python scripts/run_pipeline.py
python scripts/show_customer_history.py
```

The demo modifies one source customer (city and segment), advances its effective date, expires the prior dimension version, and inserts a new current version. Previously loaded sales continue pointing to the customer version valid on the order date.

## 8. Run unit tests

```powershell
python -m unittest discover -s tests -v
```

These tests validate financial measure calculations, rounding, and customer attribute hashing. Database integration checks are performed by the ETL validation stage.

## 9. Inspect the warehouse in pgAdmin

Connect pgAdmin to the configured server and database, then inspect:

- `source.customers`, `source.orders`, `source.order_items`
- `dw.dim_date`, `dw.dim_customer`, `dw.dim_product`, `dw.dim_region`
- `dw.fact_sales`

Useful SQL:

```sql
-- Warehouse row counts
SELECT 'dim_date' AS table_name, COUNT(*) FROM dw.dim_date
UNION ALL SELECT 'dim_customer', COUNT(*) FROM dw.dim_customer
UNION ALL SELECT 'dim_product', COUNT(*) FROM dw.dim_product
UNION ALL SELECT 'dim_region', COUNT(*) FROM dw.dim_region
UNION ALL SELECT 'fact_sales', COUNT(*) FROM dw.fact_sales;

-- Customer SCD2 versions
SELECT customer_id, full_name, city, segment, valid_from, valid_to, is_current
FROM dw.dim_customer
ORDER BY customer_id, valid_from;

-- Monthly net sales and profit
SELECT d.year_number, d.month_number, d.month_name,
       SUM(f.net_sales) AS net_sales,
       SUM(f.profit) AS profit
FROM dw.fact_sales f
JOIN dw.dim_date d ON d.date_key = f.date_key
GROUP BY d.year_number, d.month_number, d.month_name
ORDER BY d.year_number, d.month_number;

-- Sales by category and region
SELECT p.category, r.region_name,
       SUM(f.net_sales) AS net_sales,
       SUM(f.profit) AS profit
FROM dw.fact_sales f
JOIN dw.dim_product p ON p.product_key = f.product_key
JOIN dw.dim_region r ON r.region_key = f.region_key
GROUP BY p.category, r.region_name
ORDER BY net_sales DESC;
```

## Troubleshooting

- **Connection refused:** verify PostgreSQL is running and `PGHOST` / `PGPORT` are correct. For Docker, use `docker compose ps` and `docker compose logs postgres`.
- **Password authentication failed:** update `.env` to match the database user and password.
- **Database does not exist:** create `day24_warehouse` in pgAdmin, or use `docker compose up -d` with the default `.env` values.
- **Port 5432 already allocated:** stop one PostgreSQL instance or change `PGPORT` in `.env`; ensure the Docker port mapping and client port agree.
- **SCD2 effective date error:** `source.customers.updated_at` must be later than the current version's `valid_from` when tracked attributes change. Correct the source effective date before rerunning.
- **A validation check fails:** open the newest `reports/validation_report_*.txt` and inspect the failed check before proceeding.

## Deliverables checklist

- [x] Warehouse schema, fact and dimension tables, relationships, constraints, and indexes.
- [x] Date dimension with date hierarchy, fiscal attributes, weekend and holiday flags.
- [x] Dimension extraction and loading; customer SCD Type 2, product / region Type 1.
- [x] Fact extraction, surrogate-key lookup, measures, and idempotent loading.
- [x] Automated data validation with saved results.
- [x] Architecture diagram, ERD, data dictionary, setup guide, SQL examples, and unit tests.

## Important scope note

This is an educational warehouse using synthetic e-commerce data. The holiday CSV is a limited India-focused example; it is not a comprehensive state-wise or exchange holiday calendar. Product dimension attributes are Type 1, while the fact stores the unit cost and price applied to each transaction to preserve loaded measure values.
