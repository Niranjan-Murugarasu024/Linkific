# Databricks notebook source
from pyspark.sql import functions as F
# MAGIC %md
# MAGIC # 01 — Bronze ingestion
# MAGIC Read source snapshots as strings first, preserving raw values for audit and replay.

# COMMAND ----------
# If running this notebook independently, define these values to match 00_environment_setup.
CATALOG = spark.conf.get("day24.catalog", "main")
SOURCE_PATH = spark.conf.get("day24.source_path", "/Volumes/main/default/day24")

# COMMAND ----------
source_files = ["customers", "products", "regions", "orders"]
for name in source_files:
    df = (spark.read
          .option("header", True)
          .option("inferSchema", False)
          .csv(f"{SOURCE_PATH}/{name}.csv"))
    (df.withColumn("_ingested_at", F.current_timestamp())
       .withColumn("_source_file", F.lit(f"{name}.csv"))
       .write.format("delta").mode("overwrite")
       .option("overwriteSchema", "true")
       .saveAsTable(f"{CATALOG}.bronze.{name}"))

display(spark.table(f"{CATALOG}.bronze.orders").limit(10))
