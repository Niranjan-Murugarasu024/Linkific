from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

def show_context(**context):
    print(f"Airflow logical date: {context['ds']}")
    print('First PythonOperator completed')

with DAG('day13_hello_airflow', start_date=datetime(2026, 1, 1), schedule='@daily', catchup=False,
         default_args={'retries': 1, 'retry_delay': timedelta(minutes=1)}, tags=['day13', 'beginner']) as dag:
    greet = BashOperator(task_id='greet', bash_command='echo "Hello from Apache Airflow"')
    python_task = PythonOperator(task_id='show_context', python_callable=show_context)
    done = BashOperator(task_id='done', bash_command='echo "DAG complete"')
    greet >> python_task >> done
