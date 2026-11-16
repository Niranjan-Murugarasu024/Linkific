# Day 26 — Airflow Pipeline Orchestration, Monitoring and Recovery

**Project:** E-commerce Daily Data Pipeline
**Platform:** Apache Airflow 3.4.0, Docker Compose, PostgreSQL 17, Python, pandas
**DAG:** `ecommerce_daily_pipeline`

This is a local learning / portfolio project. It demonstrates scheduling, parallel extraction, transformation, data-quality gates, idempotent database loading, reconciliation, observability, retries, callbacks and dead-letter storage. It is not a production-secure deployment.

## 1. Architecture

```text
                    Airflow Scheduler
                  Daily 02:00 UTC / 07:30 IST
                              |
               +--------------+--------------+
               |              |              |
         extract_orders  extract_customers  extract_products
               |              |              |
               +--------------+--------------+
                              |
                    transform_and_enrich
                              |
                      data_quality_check
                        /           \
                pass /                 \ fail
                    |                   +--> Alert + task failure event
             load_to_postgresql        +--> Rejected rows in DLQ CSV
                    |
          reconcile_postgresql_load
                    |
              publish_run_summary
                    |
         PostgreSQL analytics.fact_order_lines
```

The committed input dataset contains 100,000 order lines, 5,000 customers and 40 products. It includes 1,007 deliberately invalid product references (about 1.01%); these are written to the dead-letter CSV, below the default 10% failure threshold.

## 2. Schedule and execution policy

- Cron: `0 2 * * *` in UTC (07:30 in Asia/Kolkata).
- `catchup=False`: do not create historical runs automatically.
- `max_active_runs=1`: prevent overlapping daily runs.
- `max_active_tasks=4`: allow the three extraction tasks to run concurrently while limiting per-DAG concurrency.
- Retries: 2 retries, starting at 2 minutes, exponential backoff, capped at 15 minutes.
- Task timeout: 30 minutes; DAG run timeout: 1 hour.
- PostgreSQL writes use `ON CONFLICT (order_line_id) DO UPDATE`, making task retries safe against duplicate fact rows.

## 3. Project structure

```text
day26_airflow_orchestration/
├── dags/
│   └── ecommerce_daily_pipeline.py
├── data/
│   ├── input/
│   │   ├── orders.csv
│   │   ├── customers.csv
│   │   └── products.csv
│   ├── staging/          # run-specific source snapshots and transformed output
│   ├── dead_letter/      # rejected rows and task-failure JSON events
│   └── reports/          # run summary JSON
├── scripts/
│   └── init-warehouse-db.sql
├── logs/
├── plugins/
├── .env.example
├── Dockerfile
├── docker-compose.yaml
└── requirements.txt
```

## 4. Run it on Windows with PowerShell

Prerequisites: Docker Desktop running with the WSL2 backend, Docker Compose v2, and at least 4 GB allocated to Docker (8 GB is preferable for a smoother local experience).

Open PowerShell:

```powershell
Set-Location "E:\Linkific\Day 26"
Copy-Item .env.example .env

docker compose build
docker compose up -d

docker compose ps
docker compose logs -f airflow
```

The first build pulls the Airflow and PostgreSQL images and installs the pinned Python packages. The first Airflow startup initializes its metadata database and starts the standalone development environment.

Open **http://localhost:8080**. The configured Airflow username is `airflow`. To retrieve the generated local password:

```powershell
docker compose exec airflow bash -lc "cat /opt/airflow/simple_auth_manager_passwords.json.generated"
```

If that file is not present yet, inspect `docker compose logs airflow` and wait for the standalone startup to finish. Do not expose this local setup to a public network.

## 5. Enable and trigger the DAG

Airflow creates DAGs paused by default in this project. Unpause it:

```powershell
docker compose exec airflow airflow dags unpause ecommerce_daily_pipeline
docker compose exec airflow airflow dags list
```

Trigger from the UI (DAG page → Trigger) or from PowerShell:

```powershell
docker compose exec airflow airflow dags trigger ecommerce_daily_pipeline
```

For a deterministic CLI test of a logical date:

```powershell
docker compose exec airflow airflow dags test ecommerce_daily_pipeline 2026-11-15
```

A manual trigger is the best first test. The scheduled run will occur at 07:30 Asia/Kolkata after the DAG is unpaused.

## 6. Verify the database load

PostgreSQL is exposed on host port `5433` so it does not collide with a local PostgreSQL server using port `5432`.

```powershell
docker compose exec postgres psql -U airflow -d ecommerce_dw -c "SELECT COUNT(*) AS rows_loaded, SUM(line_revenue) AS total_revenue FROM analytics.fact_order_lines;"

docker compose exec postgres psql -U airflow -d ecommerce_dw -c "SELECT order_line_id, order_date, customer_name, product_name, quantity, line_revenue, gross_profit FROM analytics.fact_order_lines ORDER BY order_date, order_line_id;"
```

Expected initial load: 98,993 accepted rows in the fact table and 1,007 rejected source rows in `data/dead_letter/rejected_records/<run_id>/rejected_orders.csv`. The fact table is keyed by `order_line_id`.

## 7. Monitoring and alerting

Use the Airflow UI:

- **Grid View:** inspect each task state and identify failures / retries.
- **Graph View:** inspect dependencies and parallel extraction.
- **Task Instance → Logs:** inspect extraction counts, reject counts, runtimes, load counts and reconciliation.
- **DAG Run details:** inspect start/end times and overall status.

The DAG also writes:

- `data/reports/<run_id>/run_summary.json` — records processed, rejects, revenue, quality result, verified load count and task-stage durations.
- `data/dead_letter/rejected_records/<run_id>/rejected_orders.csv` — invalid business records and rejection reasons.
- `data/dead_letter/task_failures/<run_id>/<task_id>.json` — task failure metadata.

### Optional Slack / email notifications

Edit `.env` and set `SLACK_WEBHOOK_URL` to a Slack incoming webhook. For email, set `ALERT_EMAIL_TO`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` and `SMTP_FROM`. Restart the Airflow container after changing environment variables:

```powershell
docker compose up -d --force-recreate airflow
```

Without these optional settings, alerts are still visible in Airflow task / DAG logs and failure-event JSON files.

## 8. Test failure handling and the dead-letter path

The committed dataset includes unknown `product_id` values (`P9999`). These rows should be rejected with reason `UNKNOWN_PRODUCT_ID`, while the overall reject percentage remains below the 10% gate.

To test a quality-gate failure, regenerate the dataset with an invalid rate above 10%, such as `--invalid-rate 0.15`, trigger a new run, and inspect the `data_quality_check` task. The quality task should fail and no rows from that run will be loaded. Restore the committed dataset afterwards with the 100,000-row generation command in section 11.

Do not delete the PostgreSQL volume unless you intentionally want to reset all database state.

## 9. Data-quality rules

| Check | Rule | Failure behaviour |
|---|---|---|
| Required schema | Required columns must exist | Extraction fails and retries |
| Non-empty input | Each input must contain rows | Extraction fails and retries |
| Dimension uniqueness | `customer_id` and `product_id` must be unique | Transformation fails |
| Order-line key | Must not be null, blank or duplicated | Record rejected; duplicate count also fails quality gate |
| Order date | Must parse as a date | Record rejected |
| Quantity | Positive whole number | Record rejected |
| Unit price / cost | Numeric and non-negative | Record rejected |
| Referential integrity | Customer and product IDs must exist | Record rejected to DLQ |
| Rejection threshold | Rejected rows must be at most 10% | Quality task fails above threshold |
| Post-load reconciliation | Warehouse row count and revenue must match accepted output | Reconciliation task fails |

Change `MAX_REJECT_RATE` in `docker-compose.yaml` to adjust the threshold.

## 10. Optimization choices

- Independent source extracts are parallelized.
- XCom carries file paths and compact metrics, not full datasets.
- Run-specific source snapshots keep a run's inputs stable across retries.
- PostgreSQL UPSERT avoids duplicate fact rows on retry or reprocessing.
- Batch inserts use `execute_values` with a page size of 1,000.
- A bounded `max_active_tasks` protects the local environment from uncontrolled concurrency.
- Heavy transformation runs inside a task, not while the scheduler parses the DAG file.

For million-row production workloads, replace local CSV snapshots with object storage / a lakehouse, partition inputs by data interval, use Spark or Databricks for large transformations, and keep Airflow responsible for orchestration rather than processing every record itself.

## 11. Optional scale test with synthetic data

The project includes a deterministic CSV generator that uses only the Python standard library. It overwrites the three files under `data/input`, so keep a copy of the small demo CSVs first if you want to restore them.

From the project root in PowerShell, generate a realistic 100k-order workload:

```powershell
python .\scripts\generate_synthetic_data.py --orders 100000 --customers 5000 --products 40 --invalid-rate 0.01 --seed 42
```

To push the same pipeline toward 500k rows, run:

```powershell
python .\scripts\generate_synthetic_data.py --orders 500000 --customers 15000 --products 80 --invalid-rate 0.005 --seed 42
```

The generator now supports configurable product counts, customer counts, invalid-rate settings and a wider date window. It keeps the same stable CSV schema expected by the ETL pipeline and is suitable for local benchmarking before moving to distributed processing.

Then trigger a new DAG run and compare the task durations, extract counts, transformation time, batch-load logs and reconciliation output. Increase the volume gradually while monitoring Docker memory. The transform step currently uses pandas in memory; for sustained multi-million-row workloads, move transformation to Spark / Databricks and have Airflow orchestrate that compute job.

## 12. Stop and reset

Stop services but retain database state:

```powershell
docker compose down
```

Stop services and delete the PostgreSQL volume (destructive reset):

```powershell
docker compose down -v
```

## 13. Important deployment note

This Compose + `airflow standalone` configuration is intended for local learning and demonstration. It uses Airflow's development-oriented standalone command and SimpleAuthManager. For shared or production deployment, use a supported multi-service deployment, secure authentication, a secret backend, external log storage, monitoring/metrics infrastructure, network restrictions and a managed PostgreSQL service. Never commit `.env` or real credentials.
