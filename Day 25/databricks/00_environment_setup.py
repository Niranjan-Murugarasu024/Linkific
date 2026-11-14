# Databricks notebook source
# MAGIC %md
# MAGIC # 00 — Environment setup
# MAGIC Configure the catalog, schema and uploaded source-data directory before running other notebooks.

# COMMAND ----------
dbutils.widgets.text("catalog", "main", "Unity Catalog")
dbutils.widgets.text("project_schema", "day24_ecommerce", "Project schema")
dbutils.widgets.text("source_path", "/Volumes/main/default/day24", "Source CSV directory")
dbutils.widgets.text("export_path", "/Volumes/main/default/day24/gold_export", "Gold export directory")

CATALOG = dbutils.widgets.get("catalog")
PROJECT_SCHEMA = dbutils.widgets.get("project_schema")
SOURCE_PATH = dbutils.widgets.get("source_path").rstrip("/")
EXPORT_PATH = dbutils.widgets.get("export_path").rstrip("/")

# Share configuration with subsequent notebooks on the same cluster session.
spark.conf.set("day24.catalog", CATALOG)
spark.conf.set("day24.source_path", SOURCE_PATH)
spark.conf.set("day24.export_path", EXPORT_PATH)

spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{CATALOG}`.`bronze`")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{CATALOG}`.`silver`")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{CATALOG}`.`gold`")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{CATALOG}`.`ops`")

spark.sql(f"USE CATALOG `{CATALOG}`")
print(f"Catalog={CATALOG}; source={SOURCE_PATH}; export={EXPORT_PATH}")
