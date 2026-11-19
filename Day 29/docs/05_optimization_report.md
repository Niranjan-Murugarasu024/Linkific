# 5. Optimization Report

## 5.1 Measurement method
Record machine / database configuration, dataset size, test conditions, number of runs, and whether
the reported value is a single run or a median. Compare equivalent workloads.

## 5.2 Before-and-after benchmark

| Area | Workload / metric | Before | After | Change | Evidence |
|---|---|---:|---:|---:|---|
| Python ETL | Full pipeline duration | [FILL IN] | [FILL IN] | [CALCULATE] | [FILL IN] |
| PostgreSQL | Query duration | [FILL IN] | [FILL IN] | [CALCULATE] | [FILL IN] |
| Airflow | DAG duration | [FILL IN] | [FILL IN] | [CALCULATE] | [FILL IN] |
| Power BI | Page render / refresh duration | [FILL IN] | [FILL IN] | [CALCULATE] | [FILL IN] |

## 5.3 Changes evaluated
For each change, record the bottleneck, evidence, modification, correctness impact, and benchmark.
Potential areas to investigate:
- Python: vectorization, avoiding repeated reads, batch processing.
- PostgreSQL: `EXPLAIN (ANALYZE, BUFFERS)`, appropriate indexes, query shape.
- Airflow: task granularity, unnecessary dependencies, retries, concurrency.
- Power BI: model size, unused columns, relationship design, DAX complexity, visual count.

## 5.4 Index / query changes

| Object | Change | Reason | Query plan evidence | Outcome |
|---|---|---|---|---|
| [FILL IN] | [FILL IN] | [FILL IN] | [FILL IN] | [FILL IN] |

## 5.5 Conclusion
State which changes produced measurable improvements and which did not. Do not infer causation from
non-equivalent test runs.
