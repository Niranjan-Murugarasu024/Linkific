# Optional: copy into the DAG folder of your existing Airflow environment.
from __future__ import annotations

from datetime import datetime, timedelta
import os
from pathlib import Path

import yaml
from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
    "email_on_retry": False,
}


def enter_project_directory():
    project_dir = Path(os.environ.get("DAY23_PROJECT_DIR", Path(__file__).resolve().parents[1]))
    os.chdir(project_dir)


def prepare_runtime():
    from dotenv import load_dotenv

    enter_project_directory()
    load_dotenv()
    for folder in ["data/sample", "data/raw", "data/staging", "data/quarantine", "logs"]:
        Path(folder).mkdir(parents=True, exist_ok=True)


def initialize_ingestion_runtime():
    from src.extractors.database_extractor import initialize_sample_source, source_engine
    from src.ingestion.staging_loader import initialize_staging, staging_engine

    enter_project_directory()
    source_db = source_engine()
    initialize_sample_source(source_db)
    stage_db = staging_engine()
    initialize_staging(stage_db)
    return {"source_db": str(source_db.url), "staging_db": str(stage_db.url)}


def build_source_map():
    enter_project_directory()
    cfg = yaml.safe_load(Path("config/config.yaml").read_text(encoding="utf-8"))

    from src.collectors.countries import collect as collect_countries
    from src.collectors.dummyjson import collect as collect_dummyjson
    from src.collectors.jsonplaceholder import collect as collect_jsonplaceholder
    from src.extractors.database_extractor import extract_table, source_engine
    from src.processors.file_processor import collect_files
    from src.scrapers.product_scraper import scrape_books

    return {
        "jsonplaceholder": lambda: collect_jsonplaceholder(cfg["apis"]["jsonplaceholder"]),
        "dummyjson": lambda: collect_dummyjson(cfg["apis"]["dummyjson"]),
        "countries": lambda: collect_countries(cfg["apis"]["countries"]),
        "books_scrape": lambda: scrape_books(cfg["scraping"]["url"], cfg["scraping"]["max_pages"]),
        "file_batches": lambda: collect_files("data/sample"),
        "source_database": lambda: extract_table(source_engine(), "source_orders"),
    }


def run_single_source(source_name):
    from src.ingestion.orchestrator import run_pipeline
    from src.ingestion.staging_loader import staging_engine

    enter_project_directory()
    stage_db = staging_engine()
    selected_sources = {source_name: build_source_map()[source_name]}
    result = run_pipeline(selected_sources, stage_db)
    return result


def summarize_ingestion_results(**context):
    ti = context["ti"]
    source_tasks = [
        "api_ingestion_group.ingest_jsonplaceholder",
        "api_ingestion_group.ingest_dummyjson",
        "api_ingestion_group.ingest_countries",
        "web_and_file_group.ingest_books_scrape",
        "web_and_file_group.ingest_file_batches",
        "database_group.ingest_source_database",
    ]
    results = {}
    failures = []
    for task_id in source_tasks:
        result = ti.xcom_pull(task_ids=task_id)
        task_instance = context["dag_run"].get_task_instance(task_id)
        task_status = task_instance.state if task_instance else "missing"
        if result:
            results[task_id] = {**result, "task_status": task_status}
            if result.get("status") != "success":
                failures.append(task_id)
        else:
            results[task_id] = {"status": task_status, "task_status": task_status}
            if task_status != "success":
                failures.append(task_id)

    summary = {
        "task_count": len(results),
        "sources": {k: v.get("status", "unknown") for k, v in results.items()},
        "full_results": results,
    }
    if failures:
        raise AirflowException(f"Ingestion sources failed or did not complete: {failures}")
    return summary


with DAG(
    dag_id="day23_multi_source_ingestion_detailed",
    start_date=datetime(2026, 1, 1),
    default_args=DEFAULT_ARGS,
    schedule=None,
    catchup=False,
    tags=["data-engineering", "ingestion", "etl", "sources"],
    description=(
        "Multi-source ingestion pipeline with separate tasks for API, scraper, file, and database inputs. "
        "Each source runs independently and preserves raw payloads and a detailed run history."
    ),
) as dag:
    start = EmptyOperator(task_id="start")
    prepare = PythonOperator(task_id="prepare_runtime", python_callable=prepare_runtime)
    initialize = PythonOperator(task_id="initialize_ingestion_runtime", python_callable=initialize_ingestion_runtime)

    with TaskGroup("api_ingestion_group", tooltip="REST API ingestion sources") as api_group:
        ingest_jsonplaceholder = PythonOperator(
            task_id="ingest_jsonplaceholder",
            python_callable=run_single_source,
            op_kwargs={"source_name": "jsonplaceholder"},
        )
        ingest_dummyjson = PythonOperator(
            task_id="ingest_dummyjson",
            python_callable=run_single_source,
            op_kwargs={"source_name": "dummyjson"},
        )
        ingest_countries = PythonOperator(
            task_id="ingest_countries",
            python_callable=run_single_source,
            op_kwargs={"source_name": "countries"},
        )

    with TaskGroup("web_and_file_group", tooltip="Scraping and file-batch ingestion sources") as web_file_group:
        ingest_books_scrape = PythonOperator(
            task_id="ingest_books_scrape",
            python_callable=run_single_source,
            op_kwargs={"source_name": "books_scrape"},
        )
        ingest_file_batches = PythonOperator(
            task_id="ingest_file_batches",
            python_callable=run_single_source,
            op_kwargs={"source_name": "file_batches"},
        )

    with TaskGroup("database_group", tooltip="Source database extraction tasks") as database_group:
        ingest_source_database = PythonOperator(
            task_id="ingest_source_database",
            python_callable=run_single_source,
            op_kwargs={"source_name": "source_database"},
        )

    summarize = PythonOperator(
        task_id="summarize_ingestion_results",
        python_callable=summarize_ingestion_results,
        trigger_rule=TriggerRule.ALL_DONE,
    )
    finish = EmptyOperator(task_id="finish")

    start >> prepare >> initialize
    initialize >> [ingest_jsonplaceholder, ingest_dummyjson, ingest_countries]
    initialize >> [ingest_books_scrape, ingest_file_batches]
    initialize >> ingest_source_database

    [ingest_jsonplaceholder, ingest_dummyjson, ingest_countries, ingest_books_scrape, ingest_file_batches, ingest_source_database] >> summarize >> finish
