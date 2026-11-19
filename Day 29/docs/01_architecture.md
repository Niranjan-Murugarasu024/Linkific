# 1. System Architecture

## 1.1 Purpose
Describe the end-to-end e-commerce analytics platform: source files → orchestration → ETL → PostgreSQL
warehouse → Power BI semantic model and dashboards.

## 1.2 Architecture diagram
Insert `images/architecture.png` here.

![End-to-end architecture](images/architecture.png)

## 1.3 Components

| Component | Responsibility | Actual implementation / location |
|---|---|---|
| Source data | Orders, customers, products, targets, and other inputs | [FILL IN: paths / systems] |
| Apache Airflow | Schedules and orchestrates pipeline tasks | [FILL IN: DAG ID, schedule, tasks] |
| Python ETL | Extracts, cleans, validates, transforms, and loads data | [FILL IN: script paths] |
| PostgreSQL | Stores analytical fact and dimension tables | Database: `ecommerce_practice`; schema: [VERIFY] |
| Power BI | Semantic model, DAX measures, reports | [FILL IN: PBIX/report name] |

## 1.4 Data flow
1. Source data is made available to the pipeline.
2. Airflow triggers tasks in dependency order.
3. Python processing performs the implemented extraction and transformations.
4. Validated records are loaded into PostgreSQL.
5. Power BI connects to PostgreSQL and consumes the modeled tables.
6. Report pages present sales, regional, product, and target analysis as implemented.

## 1.5 Data model
Insert `images/data_model.png` here.

![Data model](images/data_model.png)

Known model elements from the project work include `FactSales`, `FactSalesTargets`, `DimProducts`,
`DimCustomer`, `DimRegion`, and `DimDate`. Verify exact names, keys, cardinalities, and relationships
against the live database and Power BI model.

## 1.6 Operational considerations
Document actual configuration for retries, logging, failure handling, credentials, scheduling,
incremental/full refresh behavior, and recovery. Mark unsupported capabilities as future work.
