# 7. PowerPoint Presentation Outline

Suggested duration: 5–7 minutes. Adapt to the required time limit.

## Slide 1 — Project overview
- Business problem and objective
- Scope and users
- Technology stack: Python, Apache Airflow, PostgreSQL, Power BI

## Slide 2 — Architecture and data flow
- Source files / inputs
- Airflow DAG and task dependencies
- Python ETL and validation
- PostgreSQL warehouse
- Power BI semantic model and reports
- Screenshot: `images/architecture.png`

## Slide 3 — Data model
- Fact and dimension tables
- Grain and keys
- Relationships and referential integrity
- Screenshot: `images/data_model.png`

## Slide 4 — Pipeline demonstration
- Show Airflow DAG
- Open a successful DAG run and task logs
- Explain one important transformation and one validation rule
- Screenshot: `images/airflow_dag.png`

## Slide 5 — BI dashboard demonstration
- Show both report pages
- Explain key KPIs, slicers, visuals, and DAX measures
- Reconcile one KPI to a PostgreSQL query
- Screenshots: `images/dashboard_page_1.png`, `images/dashboard_page_2.png`

## Slide 6 — Testing and performance
- Test coverage and actual pass/fail counts
- Data quality reconciliation
- Before/after benchmarks, if optimization was performed
- Mention limitations honestly

## Slide 7 — Conclusion and future scope
- What was delivered
- Key engineering decisions
- Current limitations
- Future enhancements

## Demo sequence
1. Airflow DAG and task execution.
2. Python ETL logic.
3. PostgreSQL target tables and analytical query.
4. Power BI report pages.
5. Test / benchmark evidence.

## Presenter notes
For each slide, prepare:
- One-sentence purpose
- Two or three technical points
- Screenshot or live application to show
- One likely reviewer question and its answer
