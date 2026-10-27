from datetime import datetime
from airflow import DAG
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule

def decide(**context):
    # Deterministic branch based on the logical date; no external dependencies.
    day = context['logical_date'].day
    return 'processing.weekday' if day % 2 else 'processing.weekend'

def print_branch(name):
    print(f'Executed {name} processing branch')

with DAG('day13_branching_taskgroups', start_date=datetime(2026, 1, 1), schedule='@daily',
         catchup=False, tags=['day13', 'advanced']) as dag:
    start = EmptyOperator(task_id='start')
    choose = BranchPythonOperator(task_id='choose_branch', python_callable=decide)
    with TaskGroup('processing'):
        weekday = PythonOperator(task_id='weekday', python_callable=print_branch, op_kwargs={'name': 'odd-day'})
        weekend = PythonOperator(task_id='weekend', python_callable=print_branch, op_kwargs={'name': 'even-day'})
    finish = EmptyOperator(task_id='finish', trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
    start >> choose >> [weekday, weekend] >> finish
