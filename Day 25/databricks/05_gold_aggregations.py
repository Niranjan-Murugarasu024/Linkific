# Databricks notebook source
# MAGIC %md
# MAGIC # 05 — Gold dimensional model and business aggregates
# MAGIC Build dimensions and a fact table at one row per order line.

# COMMAND ----------
from pyspark.sql import functions as F

CATALOG = spark.conf.get("day24.catalog", "main")
orders = spark.table(f"{CATALOG}.silver.orders_current")
customers = spark.table(f"{CATALOG}.silver.customers")
products = spark.table(f"{CATALOG}.silver.products")
regions = spark.table(f"{CATALOG}.silver.regions")

dim_region = regions.select(
    F.col("region_id").alias("region_key"), "region_id", "region_name", "country"
).dropDuplicates(["region_id"])

dim_customer = (customers
    .join(dim_region.select("region_key", "region_id"), "region_id", "left")
    .select(F.col("customer_id").alias("customer_key"), "customer_id",
            "customer_name", "email", F.col("region_key"))
    .dropDuplicates(["customer_id"]))

dim_product = products.select(
    F.col("product_id").alias("product_key"), "product_id",
    "product_name", "category", "unit_price"
).dropDuplicates(["product_id"])

dim_date = (orders.select(F.col("order_date").alias("full_date")).distinct()
    .withColumn("date_key", F.date_format("full_date", "yyyyMMdd").cast("int"))
    .withColumn("year", F.year("full_date"))
    .withColumn("quarter", F.quarter("full_date"))
    .withColumn("month", F.month("full_date"))
    .withColumn("month_name", F.date_format("full_date", "MMMM"))
    .withColumn("day", F.dayofmonth("full_date"))
    .select("date_key", "full_date", "year", "quarter", "month", "month_name", "day"))

fact_sales = (orders
    .select("order_id", "line_id", "customer_id", "product_id", "region_id",
            "order_date", "quantity", "unit_price", "discount_pct",
            "gross_amount", "discount_amount", "net_amount", "status", "updated_at")
    .withColumn("customer_key", F.col("customer_id"))
    .withColumn("product_key", F.col("product_id"))
    .withColumn("region_key", F.col("region_id"))
    .withColumn("date_key", F.date_format("order_date", "yyyyMMdd").cast("int"))
    .select("order_id", "line_id", "customer_key", "product_key", "region_key",
            "date_key", "quantity", "unit_price", "discount_pct", "gross_amount",
            "discount_amount", "net_amount", "status", "updated_at"))

tables = {
    "dim_region": dim_region,
    "dim_customer": dim_customer,
    "dim_product": dim_product,
    "dim_date": dim_date,
    "fact_sales": fact_sales,
}
for table_name, dataframe in tables.items():
    (dataframe.write.format("delta").mode("overwrite")
     .option("overwriteSchema", "true")
     .saveAsTable(f"{CATALOG}.gold.{table_name}"))

sales_summary = (fact_sales.join(dim_date.select("date_key", "year", "month", "month_name"), "date_key")
    .groupBy("year", "month", "month_name", "region_key")
    .agg(F.sum("net_amount").alias("net_revenue"),
         F.countDistinct("order_id").alias("order_count"),
         F.sum("quantity").alias("units_sold"))
)
(sales_summary.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
 .saveAsTable(f"{CATALOG}.gold.sales_summary"))

display(sales_summary.orderBy("year", "month", "region_key"))
