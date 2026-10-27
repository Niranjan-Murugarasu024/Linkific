# Day 13 — Apache Airflow Data Engineering Internship Project

A complete learning project with **three DAGs**, a scheduled PostgreSQL ETL workflow, XCom, task groups, branching, retry rules, and data-quality validation.

## Prerequisites

- Windows 10/11 with **Docker Desktop running Linux containers + WSL2** (or Linux)
- Docker Compose v2 (`docker compose version`)
- Recommended: at least 4 GB RAM available to Docker (8 GB preferred)
- Port 8080 available

**Version:** Apache Airflow **2.10.5**, Python 3.11 in Docker. This version is intentionally pinned for reproducible beginner lessons; Airflow 3 has different commands and APIs. Use this project as a local learning environment, not production deployment.

## Quick start (PowerShell)

```powershell
cd "E:\Linkific\Day 13"
Copy-Item .env.example .env
# Start Docker Desktop first
docker compose up airflow-init
docker compose up -d airflow-webserver airflow-scheduler
docker compose ps
```

Open **http://localhost:8080** and sign in with `admin` / `admin` (LOCAL DEVELOPMENT ONLY).

In the DAGs page, enable each DAG and click **Trigger DAG**. View **Graph**, **Grid**, and task **Logs**. The scheduler also creates daily runs once enabled; `catchup=False` avoids processing historical dates.

## DAGs

| DAG | Purpose | Key features |
| --- | --- | --- |
| `day13_hello_airflow` | Hello-world workflow | BashOperator, PythonOperator, dependencies |
| `day13_ecommerce_etl` | CSV → clean CSV → PostgreSQL → checks | XCom, PostgresHook, retries, upsert |
| `day13_branching_taskgroups` | Branching demo | BranchPythonOperator, TaskGroup, trigger rule |

**ETL input:** `data/raw/sales.csv`. Output: `data/processed/sales_clean_YYYYMMDD.csv`. Target: `ecommerce` PostgreSQL database in Docker, `sales` table. The `AIRFLOW_CONN_ECOMMERCE_DB` environment variable configures the Airflow connection.

## Check results

```powershell
docker compose exec airflow-scheduler airflow dags list
docker compose exec airflow-scheduler airflow tasks list day13_ecommerce_etl
docker compose exec postgres psql -U airflow -d ecommerce -c 'SELECT * FROM sales ORDER BY order_id;'
docker compose logs -f airflow-scheduler
```

For the ETL DAG, verify the four tasks run in order: `extract → transform → load → quality_check`. Re-triggering the ETL DAG updates existing orders instead of inserting duplicates (idempotent upsert).

## Core concepts

- **DAG:** Directed Acyclic Graph defining a workflow.
- **Operator:** Template for a task (BashOperator, PythonOperator).
- **Task instance:** A task in a particular DAG run.
- **Scheduler:** Determines which runs/tasks are ready.
- **Logical date:** Identifier for a scheduled interval, not necessarily the wall-clock run time.
- **XCom:** Small metadata exchanged between tasks (here: file paths and counts); do not use it for large datasets.
- **TaskGroup:** Visual and organizational grouping.
- **Trigger rule:** Controls when a downstream task runs, including after a skipped branch.

## Project structure

```text
Day 13/
├── dags/
│   ├── 01_hello_airflow.py
│   ├── 02_ecommerce_etl.py
│   └── 03_branching_taskgroups.py
├── src/
│   ├── __init__.py
│   └── etl.py
├── sql/
│   ├── init.sql
│   └── warehouse.sql
├── data/
│   ├── raw/sales.csv
│   └── processed/
├── logs/
├── plugins/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Troubleshooting

- **Cannot connect to Docker daemon:** Start Docker Desktop; enable WSL2 and Linux containers.
- **Port 8080 already in use:** Change `8080:8080` to `8081:8080`, then visit localhost:8081.
- **DAG not visible:** Wait 30–60 seconds; inspect scheduler logs; check import errors in the UI.
- **`ecommerce` database missing:** `sql/init.sql` runs only when Postgres volume is created. For a fresh throwaway installation only, run `docker compose down -v` and restart; **this deletes local database data**.
- **Memory problems:** Increase Docker Desktop's WSL2 memory allocation.
- **Stop:** `docker compose down` (preserves database volume).

## Internship checklist

- [ ] Airflow installed and UI accessible
- [ ] Three DAGs visible and triggered successfully
- [ ] Daily scheduling configured
- [ ] ETL loaded records into PostgreSQL
- [ ] Data-quality task passed
- [ ] Screenshots of Graph/Grid/logs and SQL output collected
- [ ] README reviewed and explained

## Notes

The ETL input is a small included sample. You can replace it with Day 12's `sales.csv` after mapping its column names to this schema. Credentials and configuration are intentionally simple for **local-only** learning. Do not expose the Airflow UI or database to the public internet.
