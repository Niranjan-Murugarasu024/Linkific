# Data Dictionary

## Source schema (`source`)

| Table | Grain / key | Purpose |
|---|---|---|
| `regions` | One row per `region_code` | Region reference data |
| `customers` | One row per `customer_id` | Customer master; `updated_at` is the SCD2 effective date |
| `products` | One row per `product_id` | Product master and current cost / price |
| `orders` | One row per `order_id` | Order header and order date |
| `order_items` | One row per `order_item_id` | Order-line quantity, price, and discount |
| `holidays` | One row per holiday date and country | Calendar holiday input |

## Warehouse dimensions (`dw`)

| Table | Key | Important attributes |
|---|---|---|
| `dim_date` | `date_key` (`YYYYMMDD`) | Calendar labels, ISO weekday, week, month, quarter, year, fiscal year / quarter, weekend and holiday flags |
| `dim_customer` | `customer_key` surrogate; `customer_id` natural | Name, email, location, segment, `valid_from`, inclusive `valid_to`, `is_current`, attribute hash |
| `dim_product` | `product_key` surrogate; `product_id` natural | SKU, name, category, brand, unit cost, list price, active flag |
| `dim_region` | `region_key` surrogate; `region_code` natural | Region name, country, active flag |

## Warehouse fact (`dw.fact_sales`)

| Column | Meaning |
|---|---|
| `sales_key` | Warehouse-generated row identifier |
| `source_order_item_id` | Unique source order-line identifier; ETL idempotency key |
| `order_id` | Degenerate order identifier |
| `date_key`, `customer_key`, `product_key`, `region_key` | Foreign keys to dimensions |
| `order_status` | Status captured from the source order header |
| `quantity`, `unit_price`, `discount_pct` | Source transaction inputs |
| `gross_sales` | Quantity multiplied by unit price |
| `discount_amount` | Gross sales multiplied by discount fraction |
| `net_sales` | Gross sales less discount amount |
| `unit_cost`, `total_cost` | Unit cost lookup and extended cost |
| `profit` | Net sales less total cost; not a full accounting margin |
| `loaded_at` | Warehouse load timestamp |

## Keys and constraints

- Every dimension has a surrogate primary key, except that source identifiers remain as natural-key attributes.
- The customer dimension allows multiple historical versions but has a partial unique index permitting only one `is_current = TRUE` version per natural customer ID.
- The fact table's foreign keys enforce referential integrity; `source_order_item_id` is unique to make repeated ETL runs idempotent.
- Non-negative prices / costs, positive quantities, and discount fractions from 0 through 1 are enforced where applicable.
