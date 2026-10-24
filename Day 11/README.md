# Day 11 — Data Warehousing & Dimensional Modeling (PostgreSQL)

A practical project for learning OLTP vs OLAP, warehouse architecture, star/snowflake/galaxy schemas, fact and dimension design, surrogate keys, and SCD Type 1/2/3. The implemented warehouse is a sales star schema with a Type 2 customer dimension.

## Deliverables
- PostgreSQL star schema (`dim_date`, `dim_customer`, `dim_product`, `dim_channel`, `fact_sales`).
- Declared fact grain: **one row per order line**.
- Initial customer snapshot and a later snapshot to demonstrate SCD Type 2 history.
- Product Type 1 overwrite example.
- Synthetic CSV datasets, analytical SQL, validation queries, Mermaid ERDs, healthcare and galaxy-schema design exercises.

## Folder structure
```text
Day-11-Data-Warehouse/
├── data/             # Synthetic CSV source datasets
├── docs/             # Modeling notes, ERDs, healthcare exercise, glossary
├── sql/              # DDL, staging, dimension/fact load, SCD2, analytics
├── scripts/          # Recommended execution order
└── README.md
```

## Requirements
PostgreSQL 14+ recommended; pgAdmin 4 or DBeaver. No Python dependencies are required.

## Windows + pgAdmin setup
1. In pgAdmin, create a database called `sales_warehouse_lab`.
2. Open Query Tool on that database.
3. Execute `sql/01_create_warehouse.sql`, then `sql/02_create_staging.sql`.
4. Import these CSVs into their staging tables (Import/Export Data → Import, Format CSV, Header enabled):

| CSV | Staging table |
|---|---|
| `data/customers_initial.csv` | `stg_customer` |
| `data/customers_changes.csv` | `stg_customer_changes` |
| `data/products.csv` | `stg_product` |
| `data/sales.csv` | `stg_sales` |

Ensure the CSV column order matches each staging table. Alternatively, use `psql` and the `\copy` examples below from the **project root**:

```powershell
psql -U YOUR_USER -d sales_warehouse_lab
```
Then at the `sales_warehouse_lab=>` prompt:
```sql
\copy stg_customer(customer_id, full_name, email, city, state, segment, updated_at) FROM 'data/customers_initial.csv' WITH (FORMAT csv, HEADER true);
\copy stg_customer_changes(customer_id, full_name, email, city, state, segment, updated_at) FROM 'data/customers_changes.csv' WITH (FORMAT csv, HEADER true);
\copy stg_product(product_id, product_name, category, brand, unit_price, updated_at) FROM 'data/products.csv' WITH (FORMAT csv, HEADER true);
\copy stg_sales(order_id, order_line_id, order_date, customer_id, product_id, channel, quantity, unit_price, discount_amount) FROM 'data/sales.csv' WITH (FORMAT csv, HEADER true);
```
Do not import a CSV twice without clearing its staging table.

## Run the warehouse
Execute these in order after importing the CSVs:
1. `sql/03_load_dimensions_and_facts.sql`
2. `sql/05_analytics_queries.sql`
3. `sql/06_validation_checks.sql`
4. `sql/04_scd2_customer_change_demo.sql` to apply customer changes and inspect the version history.
5. Run analytics and validation again. The rows in `fact_sales` keep the customer surrogate key valid at the time the sale occurred.

## SCD Type 2 semantics used here
For `dim_customer`, city/state/segment are Type 2 attributes. When one changes, the current row is closed (`valid_to = incoming.updated_at`, `is_current = false`) and a new version with a new `customer_sk` is inserted. Validity is **start inclusive, end exclusive**: `[valid_from, valid_to)`. `9999-12-31` marks the current row. The demo overwrites name/email across versions as a Type 1 policy; use this mixed policy only if it matches the business requirement.

The scripts are educational. Run the lab from a fresh database for a clean first pass. To repeat from scratch, reset/recreate the database and re-import the CSVs. The dimension/fact load avoids duplicate product/channel/date rows and fact order lines, but staging imports themselves are not deduplicated automatically.

## Important modeling ideas
- **Grain first:** the fact is one row per order line; do not mix order-level and line-level measures in one fact.
- **Facts/measures:** quantity, gross, discount, and net amounts. Quantity and revenue are additive in this dataset; ratios should be recalculated from underlying totals, not summed.
- **Natural key:** source `customer_id`; **surrogate key:** warehouse `customer_sk`, which identifies a specific version.
- **Conformed dimensions:** dimensions shared by fact tables with consistent definitions, especially useful for a galaxy schema.
- **Star vs snowflake:** the star denormalizes dimension descriptors for simpler analytics; snowflaking normalizes dimension sub-entities at the cost of extra joins.

## Troubleshooting
- `relation does not exist`: check the connected database and execution order.
- CSV import fails: enable Header, use UTF-8, and verify column order/types.
- `fact_sales` is empty: inspect staging row counts and customer/product/channel key matches; run the orphan query in `06_validation_checks.sql`.
- Duplicate staging rows: truncate the relevant staging table before re-import.
- SCD validity check returns rows: examine source timestamps and ordering before accepting the load.

## Suggested 10-hour study plan
1. 45m — read `docs/dimensional_modeling_guide.md`.
2. 60m — identify fact grain, measures, dimension attributes, natural keys, and surrogate keys.
3. 75m — create tables and load staging CSVs.
4. 90m — run the dimension/fact load and manually validate joins.
5. 90m — execute SCD2 and explain every changed/current/closed row.
6. 90m — complete analytics and validation queries.
7. 60m — draw a snowflake and a fact constellation version of this model.
8. 60m — complete the synthetic healthcare design exercise.

## Production caveats
A production warehouse typically also needs orchestration, idempotent batch control, data-quality gates, CDC/watermarks, late-arriving facts/dimensions, delete handling, row-level lineage, audit fields, transaction/concurrency strategy, timezone policy, monitoring, and reconciliation to source totals.
