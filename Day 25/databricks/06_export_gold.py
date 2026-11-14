# Databricks notebook source
# MAGIC %md
# MAGIC # 06 — Export Gold tables for PostgreSQL
# MAGIC Export one CSV file per table. Download/copy these files to `data/gold_export` on Windows.

# COMMAND ----------
CATALOG = spark.conf.get("day24.catalog", "main")
EXPORT_PATH = spark.conf.get("day24.export_path", "/Volumes/main/default/day24/gold_export")

for table_name in ["dim_region", "dim_customer", "dim_product", "dim_date", "fact_sales"]:
    source = spark.table(f"{CATALOG}.gold.{table_name}")
    destination = f"{EXPORT_PATH}/{table_name}"
    (source.coalesce(1).write.mode("overwrite")
     .option("header", True).option("dateFormat", "yyyy-MM-dd")
     .option("timestampFormat", "yyyy-MM-dd HH:mm:ss")
     .csv(destination))
    print(f"Exported {table_name} to {destination}")

# Note: Spark writes a directory containing part-*.csv. Download the part file
# from each directory and rename it to <table_name>.csv in data/gold_export.
