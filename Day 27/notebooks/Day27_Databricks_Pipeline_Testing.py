# Databricks notebook source
# MAGIC %md
# MAGIC # Day 27 — Databricks Large-Volume Pipeline Testing
# MAGIC
# MAGIC **Workload:** 200,000 raw order rows, 25,000 customers, 5,000 products, 20 regions, and four 50K ingestion batches.
# MAGIC
# MAGIC This notebook reads the synthetic CSV files included in the project ZIP, writes Bronze Delta data, validates and deduplicates each batch into Silver, builds Gold aggregates, checks the expected-results manifest, tests replay idempotency and Delta MERGE updates, and records performance metrics.
# MAGIC
# MAGIC **Important:** Set `INPUT_PATH` and `OUTPUT_BASE_PATH` in the configuration cell before running. The folder at `INPUT_PATH` must contain `orders.csv`, `customers.csv`, `products.csv`, `regions.csv`, and `expected_manifest.csv`.

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql import Window
from delta.tables import DeltaTable
from statistics import median
from time import perf_counter
import json

# ---------------------------- CONFIGURATION ----------------------------
# Preferred on Unity Catalog: use paths like
# /Volumes/<catalog>/<schema>/<volume>/day27_input
# /Volumes/<catalog>/<schema>/<volume>/day27_output
# Classic DBFS fallback (only where DBFS root is enabled):
INPUT_PATH = "dbfs:/FileStore/day27/input"
OUTPUT_BASE_PATH = "dbfs:/FileStore/day27/output"

EXPECTED_ORDER_ROWS = 200_000
EXPECTED_BATCH_SIZE = 50_000
EXPECTED_BATCHES = ["BATCH_1", "BATCH_2", "BATCH_3", "BATCH_4"]
RESET_OUTPUT = True  # Set False only when intentionally inspecting existing output.
UPDATE_TEST_ROWS = 100

BRONZE_PATH = f"{OUTPUT_BASE_PATH}/delta/bronze_orders"
CUSTOMERS_PATH = f"{OUTPUT_BASE_PATH}/delta/bronze_customers"
PRODUCTS_PATH = f"{OUTPUT_BASE_PATH}/delta/bronze_products"
REGIONS_PATH = f"{OUTPUT_BASE_PATH}/delta/bronze_regions"
SILVER_PATH = f"{OUTPUT_BASE_PATH}/delta/silver_orders"
QUARANTINE_PATH = f"{OUTPUT_BASE_PATH}/delta/quarantine_orders"
DUPLICATES_PATH = f"{OUTPUT_BASE_PATH}/delta/duplicate_orders"
GOLD_PATH = f"{OUTPUT_BASE_PATH}/delta/gold_daily_region_sales"
REPORT_PATH = f"{OUTPUT_BASE_PATH}/reports"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Validate input files and prepare output locations

# COMMAND ----------

required_files = ["orders.csv", "customers.csv", "products.csv", "regions.csv", "expected_manifest.csv"]
try:
    input_entries = {entry.name.rstrip("/") for entry in dbutils.fs.ls(INPUT_PATH)}
except Exception as exc:
    raise FileNotFoundError(f"Cannot list INPUT_PATH={INPUT_PATH}. Check the path and permissions: {exc}")
missing_files = [file_name for file_name in required_files if file_name not in input_entries]

if missing_files:
    raise FileNotFoundError(
        f"Missing files in {INPUT_PATH}: {missing_files}. "
        "Upload the five CSV files from data/generated/ and check INPUT_PATH."
    )

if RESET_OUTPUT:
    try:
        dbutils.fs.rm(OUTPUT_BASE_PATH, True)
    except Exception as exc:
        print(f"Output cleanup note: {exc}")

dbutils.fs.mkdirs(OUTPUT_BASE_PATH)
dbutils.fs.mkdirs(REPORT_PATH)

# Read all CSV columns as strings first. Explicit casts happen during validation.
read_csv = (
    spark.read.option("header", True)
    .option("mode", "PERMISSIVE")
    .option("escape", '"')
    .csv
)

raw_orders = read_csv(f"{INPUT_PATH}/orders.csv")
customers = read_csv(f"{INPUT_PATH}/customers.csv")
products = read_csv(f"{INPUT_PATH}/products.csv")
regions = read_csv(f"{INPUT_PATH}/regions.csv")
manifest = read_csv(f"{INPUT_PATH}/expected_manifest.csv")

raw_order_count = raw_orders.count()
customer_count = customers.count()
product_count = products.count()
region_count = regions.count()
manifest_count = manifest.count()

print({
    "raw_orders": raw_order_count,
    "customers": customer_count,
    "products": product_count,
    "regions": region_count,
    "manifest_rows": manifest_count,
})

assert raw_order_count == EXPECTED_ORDER_ROWS, f"Expected {EXPECTED_ORDER_ROWS:,} raw orders, found {raw_order_count:,}."
assert manifest_count == raw_order_count, "Manifest row count must match raw order row count."

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Bronze ingestion — immutable raw landing layer

# COMMAND ----------

bronze_start = perf_counter()
(raw_orders.withColumn("bronze_ingested_at", F.current_timestamp())
 .write.format("delta").mode("overwrite").save(BRONZE_PATH))
(customers.write.format("delta").mode("overwrite").save(CUSTOMERS_PATH))
(products.write.format("delta").mode("overwrite").save(PRODUCTS_PATH))
(regions.write.format("delta").mode("overwrite").save(REGIONS_PATH))
bronze_seconds = perf_counter() - bronze_start

bronze_orders = spark.read.format("delta").load(BRONZE_PATH)
customers_bronze = spark.read.format("delta").load(CUSTOMERS_PATH)
products_bronze = spark.read.format("delta").load(PRODUCTS_PATH)
regions_bronze = spark.read.format("delta").load(REGIONS_PATH)

print(f"Bronze ingestion completed in {bronze_seconds:.2f} seconds.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Reusable Delta helpers and Silver validation logic

# COMMAND ----------

def delta_exists(path: str) -> bool:
    return DeltaTable.isDeltaTable(spark, path)


def merge_by_key(source_df, target_path: str, key_column: str, update_matched: bool = True) -> None:
    """Create a Delta target or MERGE a source DataFrame by its business key."""
    if source_df is None or source_df.limit(1).count() == 0:
        return
    if not delta_exists(target_path):
        source_df.write.format("delta").mode("overwrite").save(target_path)
        return
    target = DeltaTable.forPath(spark, target_path).alias("t")
    merge_builder = target.merge(source_df.alias("s"), f"t.`{key_column}` = s.`{key_column}`")
    if update_matched:
        merge_builder = merge_builder.whenMatchedUpdateAll()
    merge_builder.whenNotMatchedInsertAll().execute()


def get_processed_source_ids():
    frames = []
    for path in [SILVER_PATH, QUARANTINE_PATH, DUPLICATES_PATH]:
        if delta_exists(path):
            frames.append(spark.read.format("delta").load(path).select("source_row_id"))
    if not frames:
        return None
    combined = frames[0]
    for frame in frames[1:]:
        combined = combined.unionByName(frame)
    return combined.dropDuplicates(["source_row_id"])


def classify_batch(batch_df):
    """Return valid, rejected and duplicate dataframes for one incoming batch."""
    customer_lookup = (
        customers_bronze.select("customer_id").dropDuplicates()
        .withColumn("_customer_found", F.lit(1))
    )
    product_lookup = (
        products_bronze.select("product_id").dropDuplicates()
        .withColumn("_product_found", F.lit(1))
    )
    region_lookup = (
        regions_bronze.select("region_id").dropDuplicates()
        .withColumn("_region_found", F.lit(1))
    )

    typed = (batch_df
        .withColumn("_quantity", F.col("quantity").cast("int"))
        .withColumn("_unit_price", F.col("unit_price").cast("double"))
        .withColumn("_discount_pct", F.col("discount_pct").cast("double"))
        .withColumn("_order_amount", F.col("order_amount").cast("double"))
        .withColumn("_order_ts", F.to_timestamp("order_ts"))
        .withColumn("_updated_at", F.to_timestamp("updated_at"))
        .withColumn("_received_at", F.to_timestamp("received_at"))
        .join(customer_lookup, "customer_id", "left")
        .join(product_lookup, "product_id", "left")
        .join(region_lookup, "region_id", "left")
    )

    # Expected amount is recalculated from quantity, unit price and discount.
    expected_amount = F.col("_quantity") * F.col("_unit_price") * (F.lit(1.0) - F.col("_discount_pct"))
    reason_parts = [
        F.when(F.col("order_id").isNull() | (F.trim(F.col("order_id")) == ""), "MISSING_ORDER_ID"),
        F.when(F.col("_customer_found").isNull(), "CUSTOMER_NOT_FOUND"),
        F.when(F.col("_product_found").isNull(), "PRODUCT_NOT_FOUND"),
        F.when(F.col("_region_found").isNull(), "REGION_NOT_FOUND"),
        F.when(F.col("_quantity").isNull() | (F.col("_quantity") <= 0), "INVALID_QUANTITY"),
        F.when(F.col("_unit_price").isNull() | (F.col("_unit_price") <= 0), "INVALID_UNIT_PRICE"),
        F.when(F.col("_discount_pct").isNull() | (F.col("_discount_pct") < 0) | (F.col("_discount_pct") > 1), "INVALID_DISCOUNT"),
        F.when(F.col("_order_ts").isNull(), "INVALID_ORDER_TIMESTAMP"),
        F.when(F.col("_updated_at").isNull(), "INVALID_UPDATED_TIMESTAMP"),
        F.when(F.col("_received_at").isNull(), "INVALID_RECEIVED_TIMESTAMP"),
        F.when(F.col("_order_amount").isNull() | (F.abs(F.col("_order_amount") - expected_amount) > F.lit(0.02)), "ORDER_AMOUNT_MISMATCH"),
    ]
    typed = typed.withColumn("rejection_reason", F.concat_ws("|", *reason_parts))

    duplicate_window = Window.partitionBy("order_id").orderBy(F.col("source_row_id").asc())
    typed = typed.withColumn("_row_number", F.row_number().over(duplicate_window))

    if delta_exists(SILVER_PATH):
        existing_orders = (spark.read.format("delta").load(SILVER_PATH)
            .select("order_id").dropDuplicates()
            .withColumn("_already_loaded", F.lit(1)))
        typed = typed.join(existing_orders, "order_id", "left")
    else:
        typed = typed.withColumn("_already_loaded", F.lit(None).cast("int"))

    typed = typed.cache()
    invalid_condition = F.col("rejection_reason") != ""
    duplicate_condition = (F.col("_row_number") > 1) | F.col("_already_loaded").isNotNull()

    valid = (typed.filter((~invalid_condition) & (~duplicate_condition))
        .select(
            "source_row_id", "order_id", "customer_id", "product_id", "region_id",
            F.col("_order_ts").alias("order_ts"),
            F.col("_quantity").alias("quantity"),
            F.col("_unit_price").alias("unit_price"),
            F.col("_discount_pct").alias("discount_pct"),
            F.col("_order_amount").alias("order_amount"),
            "order_status", "payment_method",
            F.col("_updated_at").alias("updated_at"),
            F.col("_received_at").alias("received_at"),
            "batch_id",
            F.to_date(F.col("_order_ts")).alias("order_date"),
        ))

    rejected = (typed.filter(invalid_condition)
        .select("source_row_id", "order_id", "batch_id", "rejection_reason"))

    duplicates = (typed.filter((~invalid_condition) & duplicate_condition)
        .select(
            "source_row_id", "order_id", "batch_id",
            F.when(F.col("_already_loaded").isNotNull(), "ORDER_ID_ALREADY_PROCESSED")
             .otherwise("DUPLICATE_WITHIN_BATCH").alias("duplicate_reason"),
        ))

    return valid, rejected, duplicates, typed

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Incremental pipeline execution — four 50K batches

# COMMAND ----------

batch_metrics = []
pipeline_start = perf_counter()

for batch_id in EXPECTED_BATCHES:
    batch_start = perf_counter()
    batch_df = bronze_orders.filter(F.col("batch_id") == batch_id)
    incoming_count = batch_df.count()

    processed_ids = get_processed_source_ids()
    if processed_ids is not None:
        batch_df = batch_df.join(processed_ids, "source_row_id", "left_anti")

    new_count = batch_df.count()
    if new_count == 0:
        batch_metrics.append({
            "batch_id": batch_id,
            "raw_rows": incoming_count,
            "new_rows": 0,
            "valid_rows": 0,
            "rejected_rows": 0,
            "duplicate_rows": 0,
            "duration_seconds": 0.0,
            "status": "SKIPPED_ALREADY_PROCESSED",
        })
        continue

    valid_df, rejected_df, duplicate_df, classified_df = classify_batch(batch_df)
    valid_count = valid_df.count()
    rejected_count = rejected_df.count()
    duplicate_count = duplicate_df.count()

    merge_by_key(valid_df, SILVER_PATH, "order_id", update_matched=False)
    merge_by_key(rejected_df, QUARANTINE_PATH, "source_row_id", update_matched=False)
    merge_by_key(duplicate_df, DUPLICATES_PATH, "source_row_id", update_matched=False)
    classified_df.unpersist()

    duration = perf_counter() - batch_start
    batch_metrics.append({
        "batch_id": batch_id,
        "raw_rows": incoming_count,
        "new_rows": new_count,
        "valid_rows": valid_count,
        "rejected_rows": rejected_count,
        "duplicate_rows": duplicate_count,
        "duration_seconds": round(duration, 3),
        "status": "PROCESSED",
    })
    print(f"{batch_id}: raw={incoming_count:,}, new={new_count:,}, valid={valid_count:,}, "
          f"rejected={rejected_count:,}, duplicates={duplicate_count:,}, {duration:.2f}s")

pipeline_seconds = perf_counter() - pipeline_start

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Build the Gold analytics layer

# COMMAND ----------

silver_df = spark.read.format("delta").load(SILVER_PATH)
quarantine_df = spark.read.format("delta").load(QUARANTINE_PATH)
duplicates_df = spark.read.format("delta").load(DUPLICATES_PATH)

# Gold grain: one row per order date and region.
gold_df = (silver_df.groupBy("order_date", "region_id")
    .agg(
        F.countDistinct("order_id").alias("order_count"),
        F.countDistinct("customer_id").alias("customer_count"),
        F.round(F.sum("order_amount"), 2).alias("gross_revenue"),
        F.round(F.avg("order_amount"), 2).alias("average_order_value"),
    ))

(gold_df.write.format("delta").mode("overwrite").save(GOLD_PATH))
print(f"Gold aggregate rows: {gold_df.count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Data quality tests and expected-results comparison
# MAGIC
# MAGIC The manifest is the independent test oracle. It is used only after pipeline processing to calculate row-level classification quality.

# COMMAND ----------

actual_valid = silver_df.select("source_row_id").withColumn("actual_status", F.lit("VALID"))
actual_rejected = quarantine_df.select("source_row_id").withColumn("actual_status", F.lit("REJECT"))
actual_duplicates = duplicates_df.select("source_row_id").withColumn("actual_status", F.lit("DUPLICATE"))
actual_all = actual_valid.unionByName(actual_rejected).unionByName(actual_duplicates)

comparison = (manifest.select("source_row_id", "expected_status", "expected_reason")
    .join(actual_all, "source_row_id", "left")
    .fillna({"actual_status": "MISSING"})
    .cache())

comparison_count = comparison.count()
misclassified_count = comparison.filter(F.col("expected_status") != F.col("actual_status")).count()
false_rejection_count = comparison.filter(
    (F.col("expected_status") == "VALID") & (F.col("actual_status") != "VALID")
).count()
false_acceptance_count = comparison.filter(
    (F.col("expected_status") != "VALID") & (F.col("actual_status") == "VALID")
).count()

valid_count = silver_df.count()
rejected_count = quarantine_df.count()
duplicate_count = duplicates_df.count()
reconciled_count = valid_count + rejected_count + duplicate_count
unique_order_count = silver_df.select("order_id").dropDuplicates().count()
null_order_ids = silver_df.filter(F.col("order_id").isNull()).count()
null_customer_ids = silver_df.filter(F.col("customer_id").isNull()).count()
null_product_ids = silver_df.filter(F.col("product_id").isNull()).count()
foreign_key_violations = (
    silver_df.join(customers_bronze.select("customer_id"), "customer_id", "left_anti").count()
    + silver_df.join(products_bronze.select("product_id"), "product_id", "left_anti").count()
    + silver_df.join(regions_bronze.select("region_id"), "region_id", "left_anti").count()
)

# Late-arrival test: valid events received more than 30 days after order_ts.
late_arrival_count = silver_df.filter(F.datediff("received_at", "order_ts") > 30).count()

# Per-rule quarantine breakdown.
rejection_reason_breakdown = [row.asDict() for row in (
    quarantine_df.groupBy("rejection_reason").count().orderBy(F.desc("count")).collect()
)]

quality_tests = {
    "raw_row_count_matches_target": raw_order_count == EXPECTED_ORDER_ROWS,
    "manifest_reconciles_to_raw": comparison_count == raw_order_count,
    "valid_rejected_duplicate_reconciliation": reconciled_count == raw_order_count,
    "all_source_rows_classified_once": actual_all.select("source_row_id").dropDuplicates().count() == raw_order_count,
    "no_duplicate_order_ids_in_silver": unique_order_count == valid_count,
    "no_null_order_ids_in_silver": null_order_ids == 0,
    "no_null_customer_ids_in_silver": null_customer_ids == 0,
    "no_null_product_ids_in_silver": null_product_ids == 0,
    "no_foreign_key_violations_in_silver": foreign_key_violations == 0,
    "zero_false_rejections": false_rejection_count == 0,
    "zero_false_acceptances": false_acceptance_count == 0,
    "zero_manifest_misclassifications": misclassified_count == 0,
}

quality_summary = {
    "raw_rows": int(raw_order_count),
    "valid_rows": int(valid_count),
    "rejected_rows": int(rejected_count),
    "duplicate_rows": int(duplicate_count),
    "reconciled_rows": int(reconciled_count),
    "late_arrival_rows": int(late_arrival_count),
    "false_rejections": int(false_rejection_count),
    "false_acceptances": int(false_acceptance_count),
    "manifest_misclassifications": int(misclassified_count),
    "foreign_key_violations": int(foreign_key_violations),
    "rejection_reason_breakdown": rejection_reason_breakdown,
    "tests": quality_tests,
}

for test_name, passed in quality_tests.items():
    print(f"{'PASS' if passed else 'FAIL'} — {test_name}")

assert all(quality_tests.values()), "One or more data-quality tests failed. Inspect quality_summary and quarantine data."
assert duplicate_count == 2_000, f"Expected 2,000 duplicates, found {duplicate_count:,}."

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Pipeline reliability tests — replay idempotency and MERGE updates

# COMMAND ----------

# Replay all four source batches. Previously processed source_row_id values must be skipped.
pre_replay_counts = {
    "silver": spark.read.format("delta").load(SILVER_PATH).count(),
    "quarantine": spark.read.format("delta").load(QUARANTINE_PATH).count(),
    "duplicates": spark.read.format("delta").load(DUPLICATES_PATH).count(),
}
replay_new_rows = 0
for batch_id in EXPECTED_BATCHES:
    replay_df = bronze_orders.filter(F.col("batch_id") == batch_id)
    processed_ids = get_processed_source_ids()
    replay_df = replay_df.join(processed_ids, "source_row_id", "left_anti")
    replay_new_rows += replay_df.count()

post_replay_counts = {
    "silver": spark.read.format("delta").load(SILVER_PATH).count(),
    "quarantine": spark.read.format("delta").load(QUARANTINE_PATH).count(),
    "duplicates": spark.read.format("delta").load(DUPLICATES_PATH).count(),
}
replay_idempotency_passed = (replay_new_rows == 0 and pre_replay_counts == post_replay_counts)
assert replay_idempotency_passed, "Replay test failed: rerun changed classified record counts."
print(f"PASS — replay idempotency; new rows on replay: {replay_new_rows}")

# Isolated MERGE update test on a temporary copy; production Silver remains unchanged.
UPDATE_TEST_PATH = f"{OUTPUT_BASE_PATH}/delta/update_merge_test"
try:
    dbutils.fs.rm(UPDATE_TEST_PATH, True)
except Exception:
    pass

silver_df.write.format("delta").mode("overwrite").save(UPDATE_TEST_PATH)
temp_target = DeltaTable.forPath(spark, UPDATE_TEST_PATH)
base_before_update = spark.read.format("delta").load(UPDATE_TEST_PATH).count()
updates_df = (spark.read.format("delta").load(UPDATE_TEST_PATH)
    .orderBy("order_id").limit(UPDATE_TEST_ROWS)
    .withColumn("source_row_id", F.concat(F.col("source_row_id"), F.lit("_UPDATE_TEST")))
    .withColumn("order_amount", F.col("order_amount") + F.lit(1.0))
    .withColumn("updated_at", F.current_timestamp() + F.expr("INTERVAL 1 DAY")))

temp_target.alias("t").merge(
    updates_df.alias("s"), "t.order_id = s.order_id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

update_test_result = spark.read.format("delta").load(UPDATE_TEST_PATH)
base_after_update = update_test_result.count()
updated_rows = update_test_result.filter(F.col("source_row_id").endswith("_UPDATE_TEST")).count()
merge_update_passed = base_before_update == base_after_update and updated_rows == min(UPDATE_TEST_ROWS, base_before_update)
assert merge_update_passed, "Delta MERGE update test failed."
print(f"PASS — Delta MERGE updated {updated_rows:,} rows without changing table row count.")

try:
    dbutils.fs.rm(UPDATE_TEST_PATH, True)
except Exception as exc:
    print(f"Temporary update-test cleanup note: {exc}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Performance benchmark and optimization
# MAGIC
# MAGIC The benchmark measures a selective aggregate query before and after Delta compaction / Z-Ordering. The actual result depends on the Databricks compute size, runtime, cache state, and storage. No speedup is assumed in advance.

# COMMAND ----------

def benchmark_region_query(iterations: int = 3) -> dict:
    durations = []
    for _ in range(iterations):
        start = perf_counter()
        (spark.read.format("delta").load(SILVER_PATH)
            .filter(F.col("region_id") == "R01")
            .agg(
                F.countDistinct("order_id").alias("orders"),
                F.round(F.sum("order_amount"), 2).alias("revenue"),
            ).collect())
        durations.append(perf_counter() - start)
    return {"runs_seconds": [round(x, 4) for x in durations], "median_seconds": round(median(durations), 4)}

# One warm-up run is excluded from the timed samples.
benchmark_region_query(iterations=1)
baseline_benchmark = benchmark_region_query(iterations=3)
optimization_action = "not_run"
optimization_error = None
optimization_start = perf_counter()
try:
    spark.sql(f"OPTIMIZE delta.`{SILVER_PATH}` ZORDER BY (region_id, order_date)")
    optimization_action = "OPTIMIZE with ZORDER BY (region_id, order_date)"
except Exception as first_error:
    optimization_error = str(first_error)[:1000]
    try:
        spark.sql(f"OPTIMIZE delta.`{SILVER_PATH}`")
        optimization_action = "OPTIMIZE compaction (Z-ORDER unavailable)"
    except Exception as second_error:
        optimization_action = "OPTIMIZE unavailable on current compute or storage"
        optimization_error = (optimization_error + " | fallback: " + str(second_error))[:1500]
optimization_seconds = perf_counter() - optimization_start

optimized_benchmark = benchmark_region_query(iterations=3)
baseline_median = baseline_benchmark["median_seconds"]
optimized_median = optimized_benchmark["median_seconds"]
improvement_pct = None if baseline_median == 0 else round(
    ((baseline_median - optimized_median) / baseline_median) * 100.0, 2
)

# Show the physical plan for review in the Databricks notebook output.
(spark.read.format("delta").load(SILVER_PATH)
    .filter(F.col("region_id") == "R01")
    .groupBy("region_id")
    .agg(F.sum("order_amount").alias("revenue"))
    .explain("formatted"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Performance and test reports

# COMMAND ----------

batch_df_report = spark.createDataFrame(batch_metrics)
batch_df_report.write.mode("overwrite").option("header", True).csv(f"{REPORT_PATH}/batch_metrics.csv")
comparison.groupBy("expected_status", "actual_status").count().write.mode("overwrite").option("header", True).csv(
    f"{REPORT_PATH}/classification_confusion_matrix.csv"
)
quarantine_df.groupBy("rejection_reason").count().write.mode("overwrite").option("header", True).csv(
    f"{REPORT_PATH}/rejection_reason_breakdown.csv"
)

pipeline_throughput = round(raw_order_count / pipeline_seconds, 2) if pipeline_seconds > 0 else None
try:
    compute_master = spark.sparkContext.master
except Exception:
    compute_master = "not exposed by this compute type"

performance_report = {
    "raw_orders": int(raw_order_count),
    "batch_count": len(EXPECTED_BATCHES),
    "batch_size_target": EXPECTED_BATCH_SIZE,
    "bronze_ingestion_seconds": round(bronze_seconds, 3),
    "incremental_processing_seconds": round(pipeline_seconds, 3),
    "incremental_pipeline_throughput_records_per_second": pipeline_throughput,
    "baseline_region_query": baseline_benchmark,
    "optimization_action": optimization_action,
    "optimization_seconds": round(optimization_seconds, 3),
    "optimized_region_query": optimized_benchmark,
    "query_time_change_percent_positive_means_faster": improvement_pct,
    "optimization_error_if_any": optimization_error,
    "compute_master": compute_master,
    "spark_version": spark.version,
}

final_test_report = {
    "project": "Day 27 - Databricks Large-Volume Pipeline Testing",
    "quality": quality_summary,
    "replay_idempotency": {
        "passed": bool(replay_idempotency_passed),
        "new_rows_on_replay": int(replay_new_rows),
        "before_counts": pre_replay_counts,
        "after_counts": post_replay_counts,
    },
    "delta_merge_update_test": {
        "passed": bool(merge_update_passed),
        "updated_rows": int(updated_rows),
        "row_count_before": int(base_before_update),
        "row_count_after": int(base_after_update),
    },
    "batch_metrics": batch_metrics,
}

dbutils.fs.put(f"{REPORT_PATH}/performance_report.json", json.dumps(performance_report, indent=2), True)
dbutils.fs.put(f"{REPORT_PATH}/test_results.json", json.dumps(final_test_report, indent=2), True)
dbutils.fs.put(f"{REPORT_PATH}/quality_summary.json", json.dumps(quality_summary, indent=2), True)

print("\n================ DAY 27 SUMMARY ================")
print(json.dumps({
    "raw_rows": raw_order_count,
    "valid": valid_count,
    "rejected": rejected_count,
    "duplicates": duplicate_count,
    "pipeline_seconds": round(pipeline_seconds, 3),
    "throughput_rows_per_second": pipeline_throughput,
    "replay_idempotency": replay_idempotency_passed,
    "merge_update_test": merge_update_passed,
    "quality_tests_passed": sum(1 for passed in quality_tests.values() if passed),
    "quality_tests_total": len(quality_tests),
    "baseline_query_seconds": baseline_median,
    "optimized_query_seconds": optimized_median,
    "query_time_change_percent": improvement_pct,
    "reports_location": REPORT_PATH,
}, indent=2))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Useful inspection queries
# MAGIC
# MAGIC Run these after the main notebook cells if you want to inspect the output tables.

# COMMAND ----------

# Uncomment to inspect rows:
# display(spark.read.format("delta").load(SILVER_PATH).limit(20))
# display(spark.read.format("delta").load(QUARANTINE_PATH).groupBy("rejection_reason").count().orderBy(F.desc("count")))
# display(spark.read.format("delta").load(DUPLICATES_PATH).limit(20))
# display(spark.read.format("delta").load(GOLD_PATH).orderBy(F.desc("gross_revenue")).limit(20))
