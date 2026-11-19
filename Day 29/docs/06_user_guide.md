# 6. User Guide

## 6.1 Prerequisites
- Python: [VERSION]
- PostgreSQL: [VERSION]
- Apache Airflow: [VERSION / deployment method]
- Power BI Desktop: [VERSION]
- Required source files: [LIST]

## 6.2 Setup
1. Clone or copy the project repository.
2. Create and activate a Python virtual environment.
3. Install dependencies from the project's requirements file.
4. Configure environment variables using a local, untracked `.env` file.
5. Create / verify the PostgreSQL database and required schema.
6. Configure Airflow connections and variables.
7. Place source files in the documented input location.

Never put passwords or tokens in this guide or commit them to source control.

## 6.3 Run the pipeline
Document the exact commands and Airflow UI steps used by this project:
- Start services: [FILL IN]
- Trigger DAG: [FILL IN]
- Monitor task logs: [FILL IN]
- Verify loaded tables: [FILL IN]
- Recover / rerun after failure: [FILL IN]

## 6.4 Power BI
1. Open the project `.pbix` file.
2. Verify the PostgreSQL server and database connection.
3. Authenticate using the approved local credentials.
4. Refresh the model.
5. Navigate the report pages and use slicers / drill-through as implemented.

Insert `images/dashboard_page_1.png` and `images/dashboard_page_2.png`.

## 6.5 Troubleshooting

| Symptom | Checks |
|---|---|
| PostgreSQL connection fails | Host, port, database, service status, credentials |
| Airflow task fails | Task log, connection ID, environment, input path |
| Missing rows | Source filters, validation rejects, load logs |
| Power BI refresh fails | PostgreSQL connectivity, credentials, schema changes |
| Dashboard values differ | Filter context, DAX logic, SQL reconciliation |
