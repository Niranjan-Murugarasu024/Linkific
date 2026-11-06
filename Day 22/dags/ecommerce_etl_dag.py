"""Production-style daily orchestration for the e-commerce warehouse ETL."""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup

PROJECT_HOME = Path(os.getenv("PROJECT_HOME", Path(__file__).resolve().parents[1]))
if str(PROJECT_HOME) not in sys.path:
    sys.path.insert(0, str(PROJECT_HOME))

from src.pipeline import (
    extract_batch,
    load_dimension_batch,
    load_fact_batch,
    run_warehouse_quality_checks,
    transform_batch,
)

DAG_DOC = """
## E-commerce daily warehouse pipeline

Processes synthetic or source CSV files into the PostgreSQL star schema.

### Stages
1. Extract five source files and persist the latest raw snapshot.
2. Validate source domains, uniqueness, and dimension relationships; write
   normalized dimensions and fact CSVs to the processed folder.
3. Upsert date, product, customer, and region dimensions.
4. Upsert sales-line and inventory-snapshot facts.
5. Run post-load warehouse quality checks.

Raw and processed artifacts are written as flat, latest-only CSVs beneath the
shared project `data/` directory. Each file carries its batch identifier;
Airflow tasks verify they are reading files from the expected run. The Airflow
tasks share the same project volume and are limited to one active DAG run.
Database writes are idempotent, so retries reuse the batch identifier and can
safely replay loads.
"""

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=15),
    "email_on_failure": False,
    "email_on_retry": False,
}


def _extract_run(run_id: str, dag_id: str) -> dict:
    batch_id = str(uuid5(NAMESPACE_URL, f"{dag_id}:{run_id}"))
    return extract_batch(batch_id=batch_id)


with DAG(
    dag_id="ecommerce_data_platform",
    description="Daily validated CSV-to-PostgreSQL e-commerce warehouse ETL",
    doc_md=DAG_DOC,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    max_active_tasks=2,
    dagrun_timeout=timedelta(hours=2),
    default_args=default_args,
    tags=["ecommerce", "etl", "postgres", "daily"],
) as dag:
    with TaskGroup(
        group_id="ingestion",
        tooltip="Extract, validate, and transform source CSVs",
    ) as ingestion:
        extract_sources = PythonOperator(
            task_id="extract_sources",
            python_callable=_extract_run,
            multiple_outputs=True,
            op_kwargs={
                "run_id": "{{ run_id }}",
                "dag_id": "{{ dag.dag_id }}",
            },
            execution_timeout=timedelta(minutes=30),
            doc_md="Extract all configured source CSVs into the flat latest raw folder.",
        )

        validate_and_transform = PythonOperator(
            task_id="validate_and_transform",
            python_callable=transform_batch,
            multiple_outputs=True,
            op_kwargs={"batch_id": extract_sources.output["batch_id"]},
            execution_timeout=timedelta(minutes=45),
            doc_md=(
                "Validate required fields and relationships, then write normalized "
                "dimension and fact CSVs to the flat processed folder."
            ),
        )

    with TaskGroup(
        group_id="warehouse",
        tooltip="Load dimensions and facts, then verify warehouse quality",
    ) as warehouse:
        load_dimensions = PythonOperator(
            task_id="load_dimensions",
            python_callable=load_dimension_batch,
            op_kwargs={"batch_id": validate_and_transform.output["batch_id"]},
            execution_timeout=timedelta(minutes=30),
            doc_md="Upsert date, product, customer, and region dimensions.",
        )

        load_facts = PythonOperator(
            task_id="load_facts",
            python_callable=load_fact_batch,
            op_kwargs={"batch_id": validate_and_transform.output["batch_id"]},
            execution_timeout=timedelta(minutes=45),
            doc_md="Upsert sales-line and inventory-snapshot facts.",
        )

        quality_checks = PythonOperator(
            task_id="quality_checks",
            python_callable=run_warehouse_quality_checks,
            execution_timeout=timedelta(minutes=15),
            doc_md="Fail the run if post-load warehouse checks report violations.",
        )

        load_dimensions >> load_facts >> quality_checks

    ingestion >> warehouse
