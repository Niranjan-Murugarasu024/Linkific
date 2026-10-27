from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.etl import extract, transform, load, quality_check

with DAG('day13_ecommerce_etl', start_date=datetime(2026, 1, 1), schedule='@daily', catchup=False,
         max_active_runs=1, default_args={'retries': 2, 'retry_delay': timedelta(minutes=2)},
         tags=['day13', 'etl', 'postgres']) as dag:
    t1 = PythonOperator(task_id='extract', python_callable=extract)
    t2 = PythonOperator(task_id='transform', python_callable=transform)
    t3 = PythonOperator(task_id='load', python_callable=load)
    t4 = PythonOperator(task_id='quality_check', python_callable=quality_check)
    t1 >> t2 >> t3 >> t4
