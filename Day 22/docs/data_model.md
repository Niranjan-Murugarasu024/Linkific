# Data Model

```mermaid
erDiagram
    DIM_DATE ||--o{ FACT_SALES : date_key
    DIM_PRODUCT ||--o{ FACT_SALES : product_key
    DIM_CUSTOMER ||--o{ FACT_SALES : customer_key
    DIM_REGION ||--o{ FACT_SALES : region_key
    DIM_DATE ||--o{ FACT_INVENTORY : date_key
    DIM_PRODUCT ||--o{ FACT_INVENTORY : product_key
    DIM_REGION ||--o{ FACT_INVENTORY : region_key
```

## Fact grains
- `warehouse.fact_sales`: one row per unique source sales line.
- `warehouse.fact_inventory`: one row per product, region, and snapshot date.

## Dimensions
- `dim_date`: integer `YYYYMMDD` key and calendar attributes.
- `dim_product`: warehouse surrogate key plus unique source `product_id`.
- `dim_customer`: warehouse surrogate key plus unique source `customer_id`.
- `dim_region`: warehouse surrogate key plus unique source `region_id`.

The fact tables reference warehouse surrogate keys; source IDs remain in the
dimension tables for traceability. The current model updates dimension
attributes in place. It does not implement slowly changing dimension history.

## Measures
- `sales_amount = quantity * unit_price - discount_amount`. The discount is a
  line-level value, not a per-unit value.
- `stock_value = available_quantity * unit_cost`.

Run `sql/schema.sql` to create the schemas, tables, constraints, and indexes.
