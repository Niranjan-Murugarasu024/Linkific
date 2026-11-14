# Databricks notebook source
# MAGIC %md
# MAGIC # 03 — Data quality framework
# MAGIC Validate required fields, numeric ranges, formats, duplicate keys and referential integrity.
# MAGIC Invalid order rows are quarantined rather than silently discarded.

# COMMAND ----------
from pyspark.sql import functions as F

CATALOG = spark.conf.get("day24.catalog", "main")
orders = spark.table(f"{CATALOG}.silver.orders_enriched")
customers = spark.table(f"{CATALOG}.silver.customers").select("customer_id").distinct()
products = spark.table(f"{CATALOG}.silver.products").select("product_id").distinct()
regions = spark.table(f"{CATALOG}.silver.regions").select("region_id").distinct()

checks = [
    ("required_fields", F.col("order_id").isNotNull() & F.col("line_id").isNotNull()
     & F.col("customer_id").isNotNull() & F.col("product_id").isNotNull()
     & F.col("region_id").isNotNull() & F.col("order_date").isNotNull()),
    ("positive_quantity", F.col("quantity") > 0),
    ("nonnegative_price", F.col("unit_price") >= 0),
    ("discount_range", F.col("discount_pct").between(0, 1)),
    ("valid_status", F.col("status").isin("PENDING", "SHIPPED", "COMPLETED", "CANCELLED")),
    ("valid_email", F.col("email").rlike(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")),
]
validated = orders
for rule_name, condition in checks:
    validated = validated.withColumn(f"fail_{rule_name}", ~F.coalesce(condition, F.lit(False)))

# Duplicate detection on order-line natural key.
duplicate_keys = (orders.groupBy("order_id", "line_id").count()
                  .filter(F.col("count") > 1)
                  .select("order_id", "line_id")
                  .withColumn("fail_duplicate_key", F.lit(True)))
validated = validated.join(duplicate_keys, ["order_id", "line_id"], "left")
validated = validated.withColumn("fail_duplicate_key", F.coalesce("fail_duplicate_key", F.lit(False)))

# Referential integrity checks.
validated = (validated
    .join(customers.withColumn("customer_exists", F.lit(True)), "customer_id", "left")
    .join(products.withColumn("product_exists", F.lit(True)), "product_id", "left")
    .join(regions.withColumn("region_exists", F.lit(True)), "region_id", "left")
    .withColumn("fail_customer_fk", ~F.coalesce("customer_exists", F.lit(False)))
    .withColumn("fail_product_fk", ~F.coalesce("product_exists", F.lit(False)))
    .withColumn("fail_region_fk", ~F.coalesce("region_exists", F.lit(False)))
)

failure_columns = [c for c in validated.columns if c.startswith("fail_")]
failure_expr = None
for c in failure_columns:
    expr = F.col(c)
    failure_expr = expr if failure_expr is None else (failure_expr | expr)

result = validated.withColumn(
    "quality_status",
    F.when(failure_expr, F.lit("REJECTED")).otherwise(F.lit("VALID"))
).withColumn(
    "quality_failure_reasons",
    F.concat_ws(",", *[F.when(F.col(c), F.lit(c.replace("fail_", ""))) for c in failure_columns])
)

(result.filter("quality_status = 'VALID'").drop(*failure_columns, "quality_status", "quality_failure_reasons")
 .write.format("delta").mode("overwrite").option("overwriteSchema", "true")
 .saveAsTable(f"{CATALOG}.silver.orders_valid"))

(result.filter("quality_status = 'REJECTED'")
 .write.format("delta").mode("overwrite").option("overwriteSchema", "true")
 .saveAsTable(f"{CATALOG}.silver.quarantine_orders"))

metrics = []
for rule in failure_columns:
    failed = result.filter(F.col(rule)).count()
    metrics.append(("orders_enriched", rule.replace("fail_", ""), failed == 0, failed))

metrics_df = spark.createDataFrame(metrics, ["dataset_name", "rule_name", "passed", "failed_records"])
(metrics_df.withColumn("run_id", F.date_format(F.current_timestamp(), "yyyyMMddHHmmss"))
 .withColumn("checked_at", F.current_timestamp())
 .write.format("delta").mode("append").saveAsTable(f"{CATALOG}.ops.data_quality_results"))

display(metrics_df)
