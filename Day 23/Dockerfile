ARG AIRFLOW_VERSION=2.9.3
FROM apache/airflow:${AIRFLOW_VERSION}-python3.11

ARG AIRFLOW_VERSION
USER airflow

RUN pip install --no-cache-dir \
    "apache-airflow==${AIRFLOW_VERSION}" \
    "requests>=2.32,<3" \
    "beautifulsoup4>=4.12,<5" \
    "pandas>=2.2,<3" \
    "openpyxl>=3.1,<4" \
    "SQLAlchemy>=1.4.36,<2.0" \
    "python-dotenv>=1.0,<2" \
    "PyYAML>=6.0,<7" \
    "pyarrow>=18,<25"
