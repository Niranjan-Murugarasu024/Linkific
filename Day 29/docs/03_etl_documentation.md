# 3. ETL Documentation

## 3.1 Pipeline summary
Document the actual pipeline that ingests e-commerce source data, applies transformations and
validation, and loads analytical tables into PostgreSQL.

## 3.2 Source-to-target mapping

| Source | Source field | Transformation / rule | Target table.field |
|---|---|---|---|
| [FILL IN] | [FILL IN] | [FILL IN] | [FILL IN] |

Add one row per important mapping. Include type casting, joins, derived columns, deduplication,
invalid-record handling, and business rules.

## 3.3 Airflow orchestration

| DAG ID | Task ID | Purpose | Upstream dependency | Retry / timeout |
|---|---|---|---|---|
| [FILL IN] | [FILL IN] | [FILL IN] | [FILL IN] | [FILL IN] |

Insert `images/airflow_dag.png` here.

![Airflow DAG](images/airflow_dag.png)

## 3.4 Transformation and load logic
For each script/function, document:
- Input and output
- Transformation logic
- Validation rules
- Error handling and logging
- Idempotency / rerun behavior
- Transaction or batch strategy

## 3.5 Scheduling and recovery
- Schedule / trigger: [FILL IN]
- Retry policy: [FILL IN]
- Failure alerting: [FILL IN]
- Backfill / rerun procedure: [FILL IN]
- Incremental load strategy, if implemented: [FILL IN]
