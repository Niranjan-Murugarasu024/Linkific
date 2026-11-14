# Databricks notebook source
# MAGIC %md
# MAGIC # 04 — Incremental CDC processing
# MAGIC Apply I/U/D events to the current-state Silver order-line table.
# MAGIC Run after the initial Bronze/Silver build and quality checks.

# COMMAND ----------
from pyspark.sql import functions as F
from delta.tables import DeltaTable

CATALOG = spark.conf.get("day24.catalog", "main")
SOURCE_PATH = spark.conf.get("day24.source_path", "/Volumes/main/default/day24")

# Seed current-state table from validated initial snapshot on first run.
target_name = f"{CATALOG}.silver.orders_current"
if not spark.catalog.tableExists(target_name):
    (spark.table(f"{CATALOG}.silver.orders_valid")
     .write.format("delta").mode("overwrite").saveAsTable(target_name))

changes = (spark.read.option("header", True).option("inferSchema", False)
           .csv(f"{SOURCE_PATH}/order_changes.csv"))

typed = (changes
    .withColumn("order_id", F.col("order_id").cast("long"))
    .withColumn("line_id", F.col("line_id").cast("int"))
    .withColumn("customer_id", F.col("customer_id").cast("long"))
    .withColumn("product_id", F.col("product_id").cast("long"))
    .withColumn("region_id", F.col("region_id").cast("long"))
    .withColumn("order_date", F.to_date("order_date"))
    .withColumn("quantity", F.col("quantity").cast("int"))
    .withColumn("unit_price", F.col("unit_price").cast("decimal(14,2)"))
    .withColumn("discount_pct", F.col("discount_pct").cast("decimal(5,4)"))
    .withColumn("status", F.upper(F.trim("status")))
    .withColumn("updated_at", F.to_timestamp("updated_at"))
    .withColumn("op", F.upper(F.trim("op")))
    .withColumn("gross_amount", (F.col("quantity") * F.col("unit_price")).cast("decimal(16,2)"))
    .withColumn("discount_amount", (F.col("gross_amount") * F.col("discount_pct")).cast("decimal(16,2)"))
    .withColumn("net_amount", (F.col("gross_amount") - F.col("discount_amount")).cast("decimal(16,2)"))
)

# Resolve enrichment columns for I/U events.
customers = spark.table(f"{CATALOG}.silver.customers").select("customer_id", "email")
products = spark.table(f"{CATALOG}.silver.products").select("product_id", "product_name", "category", "is_active")
regions = spark.table(f"{CATALOG}.silver.regions").select("region_id", "region_name", "country")
typed = (typed.join(customers, "customer_id", "left")
         .join(products, "product_id", "left")
         .join(regions, "region_id", "left"))

# Keep the latest event per natural key in a batch.
from pyspark.sql.window import Window
w = Window.partitionBy("order_id", "line_id").orderBy(F.col("updated_at").desc())
changes_latest = (typed.withColumn("_rn", F.row_number().over(w))
                  .filter("_rn = 1").drop("_rn"))

# MERGE supports inserts and updates; matched D events delete.
target = DeltaTable.forName(spark, target_name)
(target.alias("t").merge(
    changes_latest.alias("s"),
    "t.order_id = s.order_id AND t.line_id = s.line_id"
)
 .whenMatchedDelete(condition="s.op = 'D'")
 .whenMatchedUpdateAll(condition="s.op IN ('U', 'I')")
 .whenNotMatchedInsertAll(condition="s.op IN ('I', 'U')")
 .execute())

display(spark.table(target_name).orderBy("order_id").limit(20))
