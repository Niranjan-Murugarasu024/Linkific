# Power BI dashboard guide

## Connect
Use **Get data → PostgreSQL database** and connect to the database containing the `analytics` schema.
Select `dim_customer`, `dim_product`, `dim_region`, `dim_date`, `fact_sales`, and `pipeline_audit`.

## Model relationships
Create one-to-many, single-direction relationships from dimensions to fact:
- `dim_customer[customer_key]` → `fact_sales[customer_key]`
- `dim_product[product_key]` → `fact_sales[product_key]`
- `dim_region[region_key]` → `fact_sales[region_key]`
- `dim_date[date_key]` → `fact_sales[date_key]`

Mark `dim_date[full_date]` as the date table.

## Page 1 — Executive Sales Overview
- KPI cards: Total Revenue, Orders, Units Sold, Average Order Value.
- Line chart: Net Revenue by month.
- Bar chart: Net Revenue by region.
- Bar chart: Top 10 products by Net Revenue.
- Slicers: Year, Region, Category, Order Status.

## Page 2 — Customer & Product Analytics
- Matrix: Customer, Orders, Revenue, Average Order Value.
- Bar chart: Revenue by Category.
- Top N products by Net Revenue.
- Customer segment / region slicers.

## Page 3 — Data Operations & Quality
The pipeline audit and quality metrics are persisted in Databricks Delta `ops` tables. If you export them to PostgreSQL,
add matching analytics tables and connect them to this page. For the first iteration, show `pipeline_audit`:
- Latest pipeline status
- Records processed
- Execution history table
- Load timestamp

For a quality score card, define the score as passing checks divided by total checks, multiplied by 100.
Do not interpret missing quality metrics as 100%; show blank / unavailable instead.
