# Databricks notebook source
# MAGIC %md
# MAGIC # 02 — Silver transformations
# MAGIC Standardize types, normalize text, join customer/product/region data, derive measures.

# COMMAND ----------
from pyspark.sql import functions as F
from pyspark.sql import types as T

CATALOG = spark.conf.get("day24.catalog", "main")

customers = spark.table(f"{CATALOG}.bronze.customers").select(
    F.col("customer_id").cast("long"),
    F.trim("customer_name").alias("customer_name"),
    F.lower(F.trim("email")).alias("email"),
    F.col("region_id").cast("long"),
    F.to_date("created_at").alias("created_at")
)
products = spark.table(f"{CATALOG}.bronze.products").select(
    F.col("product_id").cast("long"),
    F.trim("product_name").alias("product_name"),
    F.initcap(F.trim("category")).alias("category"),
    F.col("unit_price").cast(T.DecimalType(14, 2)).alias("unit_price"),
    F.col("is_active").cast("boolean").alias("is_active")
)
regions = spark.table(f"{CATALOG}.bronze.regions").select(
    F.col("region_id").cast("long"),
    F.trim("region_name").alias("region_name"),
    F.trim("country").alias("country")
)
orders = spark.table(f"{CATALOG}.bronze.orders").select(
    F.col("order_id").cast("long"),
    F.col("line_id").cast("int"),
    F.col("customer_id").cast("long"),
    F.col("product_id").cast("long"),
    F.col("region_id").cast("long"),
    F.to_date("order_date").alias("order_date"),
    F.col("quantity").cast("int"),
    F.col("unit_price").cast(T.DecimalType(14, 2)).alias("unit_price"),
    F.col("discount_pct").cast(T.DecimalType(5, 4)).alias("discount_pct"),
    F.upper(F.trim("status")).alias("status"),
    F.to_timestamp("updated_at").alias("updated_at")
)

# Business rule: customer is authoritative for region assignment.
joined = (orders.alias("o")
    .join(customers.select("customer_id", F.col("region_id").alias("customer_region_id"), "email"), "customer_id", "left")
    .join(products.select("product_id", "product_name", "category", "is_active"), "product_id", "left")
    .join(regions.select("region_id", "region_name", "country"),
          F.col("customer_region_id") == F.col("region_id"), "left")
    .select("o.*", F.col("customer_region_id").alias("resolved_region_id"), "email",
            "product_name", "category", "is_active", "region_name", "country")
    .withColumn("region_id", F.col("resolved_region_id"))
    .drop("resolved_region_id")
    .withColumn("gross_amount", (F.col("quantity") * F.col("unit_price")).cast("decimal(16,2)"))
    .withColumn("discount_amount", (F.col("gross_amount") * F.col("discount_pct")).cast("decimal(16,2)"))
    .withColumn("net_amount", (F.col("gross_amount") - F.col("discount_amount")).cast("decimal(16,2)"))
)

(joined.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
 .saveAsTable(f"{CATALOG}.silver.orders_enriched"))

(customers.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
 .saveAsTable(f"{CATALOG}.silver.customers"))
(products.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
 .saveAsTable(f"{CATALOG}.silver.products"))
(regions.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
 .saveAsTable(f"{CATALOG}.silver.regions"))

display(spark.table(f"{CATALOG}.silver.orders_enriched").limit(20))
