# E-Commerce Business Intelligence & Advanced Analytics

A starter project for building an interactive Power BI dashboard and supporting SQL/Python analysis on the existing PostgreSQL `ecommerce_practice` database.

## Important: what is and is not included

This ZIP contains the complete project source pack: SQL scripts, Python notebooks, DAX measure definitions, a Power BI theme, dashboard build specification, and an insights template.

**It does not contain a `.pbix` file.** A genuine Power BI report file must be created and saved from Power BI Desktop after connecting to your PostgreSQL database. Generating a fake or empty `.pbix` would be misleading. Follow `powerbi/POWERBI_BUILD_GUIDE.md` to create the report.

## Expected source

The project is intended to use the existing Gold-layer model:

- PostgreSQL database: `ecommerce_practice`
- Schema: `day24_gold`
- Fact table: `fact_sales`
- Dimensions: `dim_customer`, `dim_product`, `dim_region`, `dim_date`
- Optional target table: use it only if it already exists in your database.

The exact column names have not been inspected in this package. Start with `sql/00_schema_inspection.sql`. Then update the clearly marked column-name assumptions in the SQL, DAX and notebook files to match your actual schema.

## Suggested Power BI model

Use a star schema with one-to-many relationships:

- `dim_customer[customer_key]` -> `fact_sales[customer_key]`
- `dim_product[product_key]` -> `fact_sales[product_key]`
- `dim_region[region_key]` -> `fact_sales[region_key]`
- `dim_date[date_key]` -> `fact_sales[date_key]`

These are **illustrative key names**, not verified column names. Use the corresponding primary/foreign keys in your database. Set dimensions on the 1 side, `fact_sales` on the * side, and single-direction filtering from dimensions to fact.

Mark `dim_date` as the Date table using its actual date column.

## Setup

### 1. Inspect PostgreSQL schema

Open `sql/00_schema_inspection.sql` in pgAdmin or DBeaver. Run it against `ecommerce_practice`. Record the actual columns and keys.

### 2. Run analytical SQL

Open `sql/01_analytical_queries.sql`. Replace the placeholder/assumed column names in the configuration comments before executing. Run each query separately and validate its results.

### 3. Configure Python

From the project root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with your PostgreSQL connection details. Do not commit `.env`.

```powershell
jupyter lab
```

Open the notebooks in `python/` and run them in order.

### 4. Build Power BI report

1. Open Power BI Desktop.
2. Get Data -> PostgreSQL database.
3. Server: your PostgreSQL host and port (commonly `localhost:5432`).
4. Database: `ecommerce_practice`.
5. Select Import mode for this learning project unless you specifically need DirectQuery.
6. Select the four `day24_gold` tables.
7. Build and validate relationships using your actual keys.
8. Create measures from `powerbi/DAX_MEASURES.md`.
9. Apply `powerbi/theme.json` using View -> Themes -> Browse for themes.
10. Follow `powerbi/POWERBI_BUILD_GUIDE.md`.
11. Save as `powerbi/ecommerce_analytics.pbix`.

### 5. Complete business insights

Use actual values from your dashboard and notebooks. Fill in `insights/INSIGHTS_TEMPLATE.md`. Never invent business findings or claim a metric that has not been calculated.

## Dashboard pages

1. **Executive Overview** — revenue, orders, AOV, customers, monthly trend, regional and category performance.
2. **Product & Customer Analytics** — top products/customers, customer contribution, category mix, customer segments.
3. **Regional & Time Intelligence** — regional comparisons, monthly/quarterly trend, YoY/MoM metrics if the date range supports them.
4. **Customer Drill-through** — optional detail page for an individual customer.

## Data integrity notes

- Confirm whether `revenue` is net revenue or gross revenue before naming a KPI.
- Confirm whether `order_id` is unique per order or repeated per line item.
- Do not sum order-level totals if they are duplicated across line items.
- Check whether cancelled/returned orders should be excluded.
- Time-intelligence measures require a continuous, correctly typed date table.
- Targets are not included unless an actual target table exists.

## Repository layout

```text
ecommerce-business-intelligence/
├── sql/
│   ├── 00_schema_inspection.sql
│   └── 01_analytical_queries.sql
├── python/
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 02_statistical_analysis.ipynb
│   └── 03_advanced_visualizations.ipynb
├── powerbi/
│   ├── DAX_MEASURES.md
│   ├── POWERBI_BUILD_GUIDE.md
│   └── theme.json
├── insights/
│   └── INSIGHTS_TEMPLATE.md
├── requirements.txt
├── .env.example
└── .gitignore
```
