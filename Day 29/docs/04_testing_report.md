# 4. Final Testing Report

> Fill this report with actual run evidence. Use `PASS`, `FAIL`, or `NOT RUN`; include date, environment,
> expected result, actual result, and evidence path. Never mark a test as passed without running it.

## 4.1 Test environment
- OS: [FILL IN]
- Python version: [FILL IN]
- Airflow version: [FILL IN]
- PostgreSQL version: [FILL IN]
- Power BI Desktop version: [FILL IN]
- Test date: [FILL IN]
- Git commit / project version: [FILL IN]

## 4.2 Test cases

| ID | Category | Test | Expected result | Actual result | Status | Evidence |
|---|---|---|---|---|---|---|
| E2E-01 | End-to-end | Execute full pipeline | All required stages complete | [FILL IN] | NOT RUN | [FILL IN] |
| E2E-02 | End-to-end | Compare source and target counts | Counts reconcile under documented rules | [FILL IN] | NOT RUN | [FILL IN] |
| E2E-03 | End-to-end | Validate Power BI refresh | Report refresh completes | [FILL IN] | NOT RUN | [FILL IN] |
| EDGE-01 | Edge case | Null required fields | Handled per defined rule | [FILL IN] | NOT RUN | [FILL IN] |
| EDGE-02 | Edge case | Duplicate business keys | Detected/handled as designed | [FILL IN] | NOT RUN | [FILL IN] |
| EDGE-03 | Edge case | Invalid date / numeric value | Rejected or handled as designed | [FILL IN] | NOT RUN | [FILL IN] |
| EDGE-04 | Edge case | Orphan foreign key | Detected or quarantined as designed | [FILL IN] | NOT RUN | [FILL IN] |
| PERF-01 | Performance | Measure ETL duration | Baseline recorded | [FILL IN] | NOT RUN | [FILL IN] |
| PERF-02 | Performance | Measure analytical query duration | Baseline recorded | [FILL IN] | NOT RUN | [FILL IN] |
| PERF-03 | Performance | Measure report load / refresh | Baseline recorded | [FILL IN] | NOT RUN | [FILL IN] |
| DQ-01 | Data quality | Validate revenue totals | SQL and report reconcile within tolerance | [FILL IN] | NOT RUN | [FILL IN] |
| DQ-02 | Data quality | Validate referential integrity | No unexpected orphan references | [FILL IN] | NOT RUN | [FILL IN] |
| DQ-03 | Data quality | Validate DAX against SQL | Measures reconcile for same filters | [FILL IN] | NOT RUN | [FILL IN] |

## 4.3 Reconciliation summary

| Metric | Source | Target | Difference | Explanation |
|---|---:|---:|---:|---|
| Input rows | [FILL IN] | — | — | |
| Valid rows | — | [FILL IN] | — | |
| Rejected rows | — | [FILL IN] | — | |
| Duplicate rows | [FILL IN] | [FILL IN] | [FILL IN] | |
| Revenue total | [FILL IN] | [FILL IN] | [FILL IN] | |

## 4.4 Defects and resolutions

| Defect ID | Description | Severity | Resolution | Retest result |
|---|---|---|---|---|
| [FILL IN] | [FILL IN] | [FILL IN] | [FILL IN] | [FILL IN] |

## 4.5 Sign-off
- Outstanding issues: [FILL IN]
- Known limitations: [FILL IN]
- Final status: [FILL IN]
