"""Airflow DAG for the Day 21 multi-source data engineering pipeline."""
from datetime import datetime, timedelta
import os
from pathlib import Path
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator

from src.collectors.api_collector import collect_apis
from src.collectors.database_collector import collect_sqlite, collect_postgres
from src.collectors.file_collector import collect_files
from src.collectors.web_scraper import scrape_example
from src.collectors.ftp_collector import collect_sftp
from src.transformations.format_converter import convert_examples
from src.transformations.schema_mapping import standardize_customer_columns, add_source_metadata
from src.transformations.data_cleaning import clean_customers
from src.integration.data_lineage import write_lineage
from src.warehouse.postgres_loader import load_dataframe

BASE = Path(
    os.environ.get("DAY21_PROJECT_DIR", Path(__file__).resolve().parents[1])
).resolve()


def _use_project_directory():
    os.chdir(BASE)

def collect_sources():
    """Run all source collectors; write a marker with source names."""
    _use_project_directory()
    (BASE / "data/raw").mkdir(parents=True, exist_ok=True)
    api = collect_apis()
    files = collect_files()
    collect_sqlite()
    collect_postgres()
    scrape_example()
    collect_sftp()
    convert_examples()
    # Store collected customer and sales data as task-boundary artifacts.
    files["customers"].to_csv(BASE / "data/raw/airflow_customers.csv", index=False)
    files["sales"].to_csv(BASE / "data/raw/airflow_sales.csv", index=False)
    (BASE / "data/raw/airflow_sources.txt").write_text("\n".join(list(api.keys()) + ["sqlite", "postgres_optional", "csv", "excel", "json", "web", "sftp_optional"]), encoding="utf-8")

def transform_and_integrate():
    _use_project_directory()
    customers = pd.read_csv(BASE / "data/raw/airflow_customers.csv")
    sales = pd.read_csv(BASE / "data/raw/airflow_sales.csv")
    customers = standardize_customer_columns(customers)
    customers = clean_customers(customers)
    customers = add_source_metadata(customers, "sample_csv")
    customers.to_csv(BASE / "data/processed/standardized_customers.csv", index=False)
    customer_join = customers.drop(columns=["source_system", "ingested_at"], errors="ignore")
    integrated = sales.merge(customer_join, on="customer_id", how="left")
    integrated.to_csv(BASE / "data/processed/integrated_sales.csv", index=False)
    return len(integrated)

def create_lineage():
    _use_project_directory()
    output = BASE / "data/processed/integrated_sales.csv"
    df = pd.read_csv(output)
    names = (BASE / "data/raw/airflow_sources.txt").read_text(encoding="utf-8").splitlines()
    write_lineage(names, "data/processed/integrated_sales.csv", len(df))

def load_warehouse():
    _use_project_directory()
    df = pd.read_csv(BASE / "data/processed/integrated_sales.csv")
    return load_dataframe(df, table="integrated_sales")


default_args = {
    "owner": "data-engineering-learning",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="day21_multi_source_data_pipeline",
    description="Collect, convert, integrate, lineage and load Day 21 data",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["learning", "data-engineering", "day21"],
) as dag:
    collect = PythonOperator(task_id="collect_sources", python_callable=collect_sources)
    integrate = PythonOperator(task_id="transform_and_integrate", python_callable=transform_and_integrate)
    lineage = PythonOperator(task_id="write_data_lineage", python_callable=create_lineage)
    load = PythonOperator(task_id="load_warehouse", python_callable=load_warehouse)
    collect >> integrate >> lineage >> load
