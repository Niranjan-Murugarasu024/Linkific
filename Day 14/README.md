# Day 14 — PySpark Big Data and Data Quality

## Objective
A complete local Spark learning project featuring select/filter, joins, groupBy, window functions, UDFs, CSV processing, quarantined records, metrics, tests, and validation reports.

## Windows PowerShell setup
Install a compatible **JDK 17 or 21** and set `JAVA_HOME` to the **JDK root**. Avoid relying on Java 24 for this tutorial. Check:

```powershell
java -version
$env:JAVA_HOME
py -3.11 --version
```

Open PowerShell in the unpacked project folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -c "import pyspark; print(pyspark.__version__)"
```

If execution policy blocks activation, use `.\.venv\Scripts\python.exe` instead of `python` and `.\.venv\Scripts\pip.exe` instead of `pip`.

## Run (in order)

```powershell
python -m src.operations
python -m src.pipeline
python -m src.validation_suite
python -m pytest -q
python -m src.generate_large_csv --rows 100000
python -m src.pipeline --input data/raw/large_orders.csv --output data/processed/large_run --report reports/large_quality_report.json
```

Spark output directories contain one or more `part-*` files and `_SUCCESS` metadata; they are **directories**, not a single CSV/Parquet file. Running twice uses overwrite on processed outputs.

## Inputs
- `data/raw/orders.csv`: 176 order records, including intentional invalid rows for quality checks.
- `data/raw/customers.csv`: 110 customer records for joins; the expanded orders reference these customers.
- `generate_large_csv.py`: synthetic larger input generated locally, not downloaded production data.

## Outputs
- `data/processed/valid_orders/`: clean Parquet dataset.
- `data/processed/rejected_orders/`: invalid records in JSON; review them rather than deleting.
- `data/processed/category_summary/`: category counts and revenue in CSV.
- `reports/quality_report.json`: counts and rule metrics. `passed` means **zero rejected rows**; it is expected to be false for the intentionally dirty sample.

## Files
- `src/spark_utils.py`: shared SparkSession creation.
- `src/operations.py`: select/filter/groupBy/join/window/UDF demonstrations.
- `src/quality.py`: reusable typed validation, duplicate detection, quality metrics.
- `src/pipeline.py`: end-to-end ingest, quarantine, outputs and report.
- `src/validation_suite.py`: output assertions.
- `src/generate_large_csv.py`: reproducible large synthetic dataset.
- `tests/test_quality.py`: automated PySpark tests.
- `docs/concepts.md`: conceptual notes and engineering tradeoffs.

## Learning caveats
- Local mode is suitable for understanding Spark APIs, but does not measure cluster scalability.
- The generated dataset is synthetic and deterministic; there is no genuine real-time streaming.
- Validation can catch policy breaches; it cannot establish real-world correctness of all values.
- Great Expectations is documented conceptually and optional, not installed or integrated into the core execution path.

## Official documentation
- https://spark.apache.org/docs/latest/api/python/getting_started/install.html
- https://docs.greatexpectations.io/docs/core/introduction/gx_overview/
