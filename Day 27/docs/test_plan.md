# Day 27 Test Plan

## Scope

Validate a reproducible 200,000-row e-commerce workload through Databricks Bronze, Silver and Gold Delta layers. Test functional correctness, incremental processing, failure handling, data quality, replay safety and performance.

## Workload profile

- 200,000 raw order rows, four batches of 50,000.
- 25,000 customers, 5,000 products and 20 regions.
- 2,000 repeated order events.
- Controlled defects: missing customer references, unknown products, negative quantities, invalid unit prices, malformed timestamps, invalid discount values and amount mismatches.
- Late-arriving events are identified where `received_at` is more than 30 days after `order_ts`.

## Test matrix

| ID | Test | Execution | Pass condition |
|---|---|---|---|
| GEN-01 | Raw volume | Count source CSV rows | Exactly 200,000 |
| GEN-02 | Batch allocation | Group by `batch_id` | Four batches of 50,000 |
| E2E-01 | Bronze ingestion | Write and reread Delta | Source row count preserved |
| E2E-02 | Silver load | Run validation and classification | Valid records only in Silver |
| E2E-03 | Gold aggregation | Group by order date and region | Aggregates built from Silver |
| INC-01 | Incremental batch processing | Run BATCH_1 through BATCH_4 | Every source row classified once |
| INC-02 | Duplicate handling | Detect repeated `order_id` | Duplicate source events excluded from Silver |
| INC-03 | Replay idempotency | Replay all four batches | No new rows and no count changes |
| INC-04 | Existing-order update | Temporary Delta MERGE test | 100 matches updated; total row count unchanged |
| ERR-01 | Invalid customer | Remove or blank customer key | Row quarantined |
| ERR-02 | Invalid product | Use unknown product key | Row quarantined |
| ERR-03 | Invalid numeric field | Use nonpositive or unparsable quantity/price | Row quarantined |
| ERR-04 | Invalid event time | Malformed timestamp | Row quarantined |
| DQ-01 | Completeness | Check mandatory Silver columns | No null mandatory keys |
| DQ-02 | Uniqueness | Count distinct Silver `order_id` | No duplicate business keys |
| DQ-03 | Referential integrity | Anti-join to dimensions | Zero missing dimension keys |
| DQ-04 | Financial consistency | Recalculate amount | Differences within 0.02 tolerance |
| DQ-05 | False rejection / acceptance | Compare with manifest | Both counts equal zero |
| PERF-01 | Throughput | Raw count / measured pipeline time | Record actual measured rate |
| PERF-02 | Query benchmark | Repeated selective aggregation | Record median before/after |
| PERF-03 | Data layout | OPTIMIZE / Z-Ordering attempt | Record action and any unsupported-operation reason |

## Definitions used in the report

- **False rejection:** expected `VALID`, actual status is not `VALID`.
- **False acceptance:** expected `REJECT` or `DUPLICATE`, actual status is `VALID`.
- **Manifest misclassification:** expected and actual statuses differ, including missing classifications.
- **Throughput:** raw source records divided by measured incremental processing seconds. This is a workload-level rate, not a claim about cluster-independent Spark throughput.
- **Replay idempotency:** the second processing attempt adds zero newly classified source rows and does not change Silver, quarantine or duplicate counts.

## Evidence to retain

1. Notebook output showing batch metrics.
2. `test_results.json`.
3. `quality_summary.json`.
4. `performance_report.json`.
5. `batch_metrics.csv` and the classification breakdown outputs.
6. Databricks Spark UI screenshots or query profile details for the performance discussion, if available.

## Acceptance criteria

All row-count, reconciliation, manifest, referential-integrity, Silver uniqueness and replay checks must pass. Performance results are descriptive measurements; a speedup is not a functional acceptance requirement.
