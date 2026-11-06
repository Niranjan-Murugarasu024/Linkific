# Task Breakdown

| Phase | Work | Deliverable | Status |
|---|---|---|---|
| Requirements | Domain, sources, personas, metrics, cadence | Requirements and proposal | Documented |
| Design | Architecture, ERD, dictionary, ETL flow | Design documentation | Documented |
| Infrastructure | Python environment, PostgreSQL, local Airflow | Compose and setup guide | Implemented for local learning |
| Synthetic scale | Generate connected, repeatable development data | 10k+ sales and dimension/fact CSVs | Implemented |
| Ingestion | Read sales, product, customer, region, inventory CSVs | Source readers | Implemented |
| Validation | Required fields, data domains, unique keys, relationships | Validation helpers | Implemented |
| Modeling | PostgreSQL staging and star schema | SQL schema and model docs | Implemented |
| ETL | Transform and idempotently load dimensions and facts | Python pipeline and SQL upserts | Implemented |
| Orchestration | Schedule and retry discrete pipeline stages | Airflow DAG with task groups | Implemented |
| BI | Report page and metric specifications | Dashboard mockups and Power BI report | Design documented; build a PBIX for a complete analytics demo |
| Extensions | Live source APIs, quarantine, batch history, streaming inventory | Production pipeline | Future work |

## Roles
For an individual project, one learner can take the data engineer, warehouse
designer, ETL developer, QA, documentation, and BI developer roles. In a team,
those responsibilities can be separated across data engineering, analytics,
and platform/operations.

## Suggested timeline
1. Requirements and source contracts: half day.
2. Architecture, model, and metrics: one day.
3. Local PostgreSQL/Python/Airflow setup: one day.
4. Ingestion, transformations, and validation: two to three days.
5. Warehouse loads, idempotency, and tests: two days.
6. Airflow and BI validation: one to two days.
7. Documentation, demo, and review: one day.

Times are estimates for planning, not guarantees.
