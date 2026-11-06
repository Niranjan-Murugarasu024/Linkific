# Data Dictionary

## `warehouse.fact_sales`
| Field | Type | Meaning |
|---|---|---|
| `sales_key` | BIGSERIAL | Warehouse row key |
| `source_sales_id` | VARCHAR(150) | Unique source sales-line key |
| `date_key` | INTEGER | Order date dimension key |
| `product_key` | BIGINT | Product dimension foreign key |
| `customer_key` | BIGINT | Customer dimension foreign key |
| `region_key` | BIGINT | Region dimension foreign key |
| `quantity` | INTEGER | Units on the sales line; greater than zero |
| `unit_price` | NUMERIC(12,2) | Unit selling price |
| `discount_amount` | NUMERIC(12,2) | Line-level discount |
| `sales_amount` | NUMERIC(14,2) | Quantity times price less line discount |
| `loaded_at` | TIMESTAMPTZ | Warehouse insert time |

## `warehouse.fact_inventory`
| Field | Type | Meaning |
|---|---|---|
| `inventory_key` | BIGSERIAL | Warehouse row key |
| `snapshot_id` | VARCHAR(200) | Unique date-product-region business key |
| `date_key` | INTEGER | Snapshot date dimension key |
| `product_key` | BIGINT | Product dimension foreign key |
| `region_key` | BIGINT | Region dimension foreign key |
| `available_quantity` | INTEGER | Units available; zero or greater |
| `reorder_level` | INTEGER | Reorder threshold; zero or greater |
| `stock_value` | NUMERIC(14,2) | Available quantity multiplied by unit cost |
| `loaded_at` | TIMESTAMPTZ | Warehouse insert time |

## Dimensions
- `dim_date`: `date_key`, `full_date`, day, month, month name, quarter, year.
- `dim_product`: surrogate key, source product ID, name, category, brand,
  unit cost, current-row flag.
- `dim_customer`: surrogate key, source customer ID, name, city, segment,
  current-row flag.
- `dim_region`: surrogate key, source region ID, region name, state, country.

Exact SQL types and constraints are defined in `sql/schema.sql`.
