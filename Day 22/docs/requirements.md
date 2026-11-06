# Requirements

## Data sources

| Entity | Current source | Key fields |
|---|---|---|
| Sales | CSV: `sales_sample.csv` | Line ID, date, product, customer, region, quantity, price, discount |
| Products | CSV: `products_sample.csv` | Product ID, name, category, brand, unit cost |
| Customers | CSV: `customers_sample.csv` | Customer ID, name, city, segment |
| Regions | CSV: `regions_sample.csv` | Region ID, name, state, country |
| Inventory | CSV: `inventory_sample.csv` | Snapshot date, product, region, quantity, reorder level, unit cost |

The sample files are synthetic. Live APIs, operational databases, and web
scraping are possible future sources, not implemented connectors.

## Functional requirements
- Read CSV inputs and fail with a clear error if an expected file or field is
  missing.
- Validate required values, numeric/date domains, duplicate business keys,
  and fact-to-dimension relationships.
- Derive sales amount as `quantity * unit_price - discount_amount`, with a
  line-level discount.
- Derive inventory value as `available_quantity * unit_cost`.
- Load dimensions before facts and preserve source business IDs.
- Make fact and dimension loads rerunnable using unique source keys and
  PostgreSQL upserts.
- Run warehouse-level checks after loading.
- Expose a PostgreSQL star schema for SQL and Power BI analytics.
- Allow direct Python execution and daily Airflow scheduling.

## Non-functional requirements
- PostgreSQL transaction boundaries prevent partial warehouse loads.
- Invalid inputs fail visibly rather than being silently accepted.
- Configuration and credentials are supplied through environment variables;
  `.env` is not committed.
- Code is modular, testable, and suitable for local development.

## Planning assumptions (not measurements)

| Source | Planning volume | Planned refresh |
|---|---:|---|
| Sales | 10k–100k lines/day | Daily |
| Products | 1k–20k records | Daily or on change |
| Customers | 10k–1M records | Daily or on change |
| Regions | 10–500 records | Weekly or on change |
| Inventory | 1k–100k SKU-location rows | Daily snapshot |

The default deterministic sample generator creates 10,000 sales lines, 250
products, 1,000 customers, 20 regions, and 5,000 product-region inventory
snapshots. These are development-scale synthetic records, not production
measurements.

## Users and analytics
- **Business manager:** net sales, order count, units, average order value,
  category and regional performance.
- **Inventory manager:** available units, stock value, and products below
  reorder level.
- **Marketing analyst:** customer segments, repeat purchasers, and customer
  spend.
- **Data engineer:** batch status, input row counts, validation failures, and
  warehouse health.

The sample implementation reports row counts and checks for a successful
batch in the CLI output. Persistent run-history and quarantine tables are
future work.
