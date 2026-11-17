# Day 27 — Databricks Large-Volume Pipeline Testing

A reproducible e-commerce pipeline-testing project built around **200,000 synthetic order rows**. It is designed for Databricks, Apache Spark, PySpark and Delta Lake.

The ZIP includes the generated CSV datasets, an independent expected-results manifest, a Databricks notebook, a deterministic local data generator, automated local tests, and technical documentation.

## 1. Workload included

| Dataset | Records | Purpose |
|---|---:|---|
| Orders | **200,000** | Main pipeline workload; exactly four batches of 50,000 |
| Customers | 25,000 | Customer lookup and referential-integrity checks |
| Products | 5,000 | Product lookup and referential-integrity checks |
| Regions | 20 | Regional validation and analytical grouping |
| Expected-results manifest | 200,000 | Independent row-level testing oracle |

The 200,000 raw order rows contain:

- 196,586 expected-valid source records.
- 1,414 expected-rejected source records with controlled data-quality defects.
- 2,000 duplicate source records that reuse an existing `order_id` but have distinct `source_row_id` values.

These are the expected counts for the included seed-27 dataset. The manifest records the expected classification of every source row. The pipeline must not use the manifest to decide whether a record is valid; it is used only after processing to calculate classification accuracy.

## 2. Project structure

```text
day27-databricks-pipeline-testing/
│
├── config/
│   └── project_config.json
│
├── data/
│   └── generated/
│       ├── orders.csv
│       ├── customers.csv
│       ├── products.csv
│       ├── regions.csv
│       ├── expected_manifest.csv
│       └── generation_summary.json
│
├── notebooks/
│   └── Day27_Databricks_Pipeline_Testing.py
│
├── scripts/
│   ├── generate_synthetic_data.py
│   └── validate_generated_data.py
│
├── src/day27/
│   ├── __init__.py
│   └── data_generator.py
│
├── tests/
│   ├── test_data_generator.py
│   └── test_included_dataset.py
│
├── docs/
│   ├── architecture.md
│   ├── test_plan.md
│   ├── performance_report_template.md
│   └── known_issues.md
│
├── requirements.txt
└── README.md
```

## 3. Local setup — Windows PowerShell

The data generator and local tests use Python's standard library. `pytest` is the only optional local dependency.

```powershell
# Move into the extracted project folder
Set-Location "E:\Day27\day27-databricks-pipeline-testing"

# Install the local test dependency
py -3.13 -m pip install -r .\requirements.txt

# Validate the included data files
py -3.13 .\scripts\validate_generated_data.py

# Run local unit and data-contract tests
py -3.13 -m pytest .\tests -v
```

To regenerate the dataset with the same deterministic values:

```powershell
py -3.13 .\scripts\generate_synthetic_data.py
```

To change the volume or seed:

```powershell
py -3.13 .\scripts\generate_synthetic_data.py --orders 200000 --customers 25000 --products 5000 --regions 20 --duplicates 2000 --seed 27
```

The current generator requires the order count to divide evenly into four batches. Duplicate records are included inside the requested raw order count, not added on top.

## 4. Run the Databricks notebook

### Step A — Upload the project data

Extract the ZIP locally. Upload these five CSV files from `data/generated/` to one Databricks-accessible folder:

```text
orders.csv
customers.csv
products.csv
regions.csv
expected_manifest.csv
```

The `generation_summary.json` file is useful for local verification but is not required by the notebook.

**Recommended:** Upload the files to a Unity Catalog Volume. The notebook path should look like:

```text
/Volumes/<catalog>/<schema>/<volume>/day27_input
```

If your workspace still permits classic DBFS FileStore uploads, you can instead use:

```text
dbfs:/FileStore/day27/input
```

### Step B — Import the notebook

Import `notebooks/Day27_Databricks_Pipeline_Testing.py` into your Databricks Workspace as a Python notebook. Attach an available Databricks compute resource with Spark and Delta Lake support.

### Step C — Set the paths

In the notebook's first configuration cell, update:

```python
INPUT_PATH = "/Volumes/<catalog>/<schema>/<volume>/day27_input"
OUTPUT_BASE_PATH = "/Volumes/<catalog>/<schema>/<volume>/day27_output"
```

Replace the placeholders with your actual catalog, schema and volume names. Keep the input and output folders separate. If using classic DBFS, the supplied defaults are already configured.

`RESET_OUTPUT = True` clears only the configured output folder at the start of a clean run. It does not remove the input data. Set it to `False` only when you intentionally want to inspect prior output; for a fresh full test, leave it as `True`.

### Step D — Run all notebook cells

The notebook performs the following workflow:

1. Reads and checks the five input CSV files.
2. Writes raw orders and dimensions to the Bronze Delta layer.
3. Processes four incremental batches of 50,000 rows.
4. Validates customer, product and region references; numeric fields; timestamps; discounts; and calculated order amounts.
5. Writes valid orders to Silver, invalid records to quarantine, and duplicate order events to a separate Delta path.
6. Builds a Gold daily-by-region sales aggregate.
7. Compares actual classifications with the independent expected-results manifest.
8. Tests replay idempotency and performs an isolated Delta `MERGE` update test.
9. Benchmarks a selective region query before and after an `OPTIMIZE` / Z-Ordering attempt.
10. Writes JSON and CSV reports to the configured report folder.

## 5. Expected acceptance criteria

For the included seed-27 input data, the notebook should report:

| Check | Expected result |
|---|---:|
| Raw order rows | 200,000 |
| Batch 1–4 | 50,000 each |
| Valid source records | 196,586 |
| Rejected source records | 1,414 |
| Duplicate source records | 2,000 |
| Reconciled source rows | 200,000 |
| Manifest misclassifications | 0 |
| False rejections | 0 |
| False acceptances | 0 |
| Silver duplicate `order_id` values | 0 |
| Replay new rows | 0 |
| Delta MERGE update test | 100 rows updated in an isolated test copy |

Do not hardcode performance claims. Runtime, throughput and query-time changes depend on the compute configuration, Databricks Runtime, storage, cache state and data layout. Use the notebook's measured values in your report.

## 6. Output locations

Under `OUTPUT_BASE_PATH`, the notebook creates:

```text
output/
├── delta/
│   ├── bronze_orders/
│   ├── bronze_customers/
│   ├── bronze_products/
│   ├── bronze_regions/
│   ├── silver_orders/
│   ├── quarantine_orders/
│   ├── duplicate_orders/
│   └── gold_daily_region_sales/
│
└── reports/
    ├── batch_metrics.csv/
    ├── classification_confusion_matrix.csv/
    ├── rejection_reason_breakdown.csv/
    ├── test_results.json
    ├── quality_summary.json
    └── performance_report.json
```

Spark writes CSV output as a folder containing part files. Download or inspect the folder contents rather than expecting one single CSV file.

## 7. Technology stack

- Python 3.10+ for local data generation and tests.
- Databricks notebook and Spark SQL.
- PySpark DataFrames and window functions.
- Delta Lake `MERGE`, `OPTIMIZE` and Z-Ordering where supported.
- CSV for portable raw test input; Delta for Bronze, Silver and Gold processing.
- Pytest for local generator and data-contract tests.

## 8. Important engineering notes

- 200K rows is a useful repeatable pipeline-testing workload, but it is not by itself evidence of production-scale big-data capability.
- Do not claim a performance improvement unless the benchmark report shows one.
- Traditional PostgreSQL-style B-tree indexes are not the primary optimization model for Delta tables. The notebook tests Delta compaction and data layout with `OPTIMIZE` and Z-Ordering where available.
- Small datasets can show noisy benchmark results. Run on a consistent compute configuration and compare multiple runs.
- The notebook's update test uses a temporary Delta copy so the original 200K-record classification and manifest comparison remain unchanged.

See `docs/test_plan.md` for the detailed test matrix and `docs/architecture.md` for the pipeline design.
