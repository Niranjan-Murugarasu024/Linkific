# Performance Report — Day 27

> Replace every placeholder with the values measured by your Databricks run. Do not estimate or invent benchmark results.

## Execution environment

| Property | Measured value |
|---|---|
| Databricks Runtime | `[fill in]` |
| Compute type / size | `[fill in]` |
| Worker count | `[fill in]` |
| Spark version | `[from performance_report.json]` |
| Storage path type | `[Unity Catalog Volume / DBFS / other]` |
| Input volume | 200,000 order rows |

## Pipeline results

| Metric | Measured result |
|---|---:|
| Bronze ingestion time | `[fill in]` seconds |
| Four-batch processing time | `[fill in]` seconds |
| End-to-end throughput (as defined in notebook) | `[fill in]` records/second |
| Valid records | 196,586 expected |
| Rejected records | 1,414 expected |
| Duplicate source events | 2,000 expected |
| Reconciliation | 200,000 expected |

## Query benchmark

| Benchmark | Baseline | After optimization |
|---|---:|---:|
| Selective region query median | `[fill in]` seconds | `[fill in]` seconds |
| Optimization operation | — | `[fill in]` |
| Relative query-time change | — | `[fill in]` % |

Positive relative change means the query became faster. A negative value means it became slower. Explain cache effects, small-file layout, compute sizing and the small workload size before drawing conclusions.

## Bottlenecks observed

- `[Describe Spark stages, shuffles, skew, file counts, scan volume or task imbalance supported by evidence.]`

## Optimizations attempted

- `[Describe only operations actually run.]`
- `[Record whether Z-Ordering / OPTIMIZE was supported.]`

## Conclusion

`[State what the measurements demonstrate and what remains untested at larger volumes.]`
