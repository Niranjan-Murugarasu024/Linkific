# Day 24 Warehouse Architecture

## Data flow

```mermaid
flowchart LR
    A[Source CSV files] --> B[PostgreSQL source schema]
    B --> C[Dimension ETL]
    C --> D[dw.dim_date]
    C --> E[dw.dim_customer - SCD Type 2]
    C --> F[dw.dim_product]
    C --> G[dw.dim_region]
    B --> H[Fact ETL]
    D --> H
    E --> H
    F --> H
    G --> H
    H --> I[dw.fact_sales]
    I --> J[Data quality validation]
    J --> K[JSON and TXT reports]
```

## Star schema and fact grain

`dw.fact_sales` is the central fact table. Its grain is **one source order item / order line**. An order containing three products produces three fact rows. `order_id` is retained as a degenerate dimension for drill-through and transaction-level analysis.

```mermaid
erDiagram
    DIM_DATE ||--o{ FACT_SALES : date_key
    DIM_CUSTOMER ||--o{ FACT_SALES : customer_key
    DIM_PRODUCT ||--o{ FACT_SALES : product_key
    DIM_REGION ||--o{ FACT_SALES : region_key
    DIM_REGION ||--o{ DIM_CUSTOMER : region_code

    DIM_DATE {
        int date_key PK
        date full_date UK
        int year_number
        int month_number
        int fiscal_year
        boolean is_holiday
    }
    DIM_CUSTOMER {
        bigint customer_key PK
        bigint customer_id
        varchar city
        varchar segment
        date valid_from
        date valid_to
        boolean is_current
    }
    DIM_PRODUCT {
        bigint product_key PK
        bigint product_id UK
        varchar category
        numeric unit_cost
    }
    DIM_REGION {
        smallint region_key PK
        varchar region_code UK
    }
    FACT_SALES {
        bigint sales_key PK
        bigint source_order_item_id UK
        int date_key FK
        bigint customer_key FK
        bigint product_key FK
        smallint region_key FK
        numeric net_sales
        numeric total_cost
        numeric profit
    }
```

## Slowly changing dimension strategy

- Customer: **SCD Type 2**. Changes to name, email, location, region, or segment expire the active row and insert a new surrogate-key version. The validity end date is inclusive; a new version begins the next effective date.
- Product: **SCD Type 1**. Product attributes are overwritten on change. Cost and price used by already-loaded sales facts are copied into the fact row, preserving the historical transaction measure.
- Region: Type 1 upsert.
- Date: generated calendar dimension, refreshed for the source order-date range plus one year on both sides.

## Measure definitions

- `gross_sales = quantity × unit_price`
- `discount_amount = gross_sales × discount_pct`
- `net_sales = gross_sales − discount_amount`
- `total_cost = quantity × product unit_cost`
- `profit = net_sales − total_cost`

The pipeline rounds monetary measures to two decimal places. `discount_pct` is stored as a fraction (for example, `0.10` means 10%).

## Date conventions

The fiscal year starts on 1 April. For example, April 2025–March 2026 is FY2026. `is_holiday` is populated from `source.holidays`; the packaged records are a small India national-holiday demonstration calendar, not a complete operational holiday service. Add local / state / country holiday dates to the source table before refreshing the date dimension.
