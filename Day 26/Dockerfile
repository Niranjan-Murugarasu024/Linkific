FROM apache/airflow:3.4.0

# Keep the Airflow core package on the exact image version while adding task dependencies.
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir "apache-airflow==3.4.0" -r /requirements.txt
