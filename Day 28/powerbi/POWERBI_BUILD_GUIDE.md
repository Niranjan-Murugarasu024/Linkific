# Power BI Report Build Guide

## Connection

1. Open Power BI Desktop.
2. Home -> Get data -> PostgreSQL database.
3. Enter your PostgreSQL server (for example `localhost:5432`) and database `ecommerce_practice`.
4. Select Import mode for the assignment.
5. Select `day24_gold.fact_sales`, `dim_customer`, `dim_product`, `dim_region`, and `dim_date`.
6. Load the tables.

If Power BI cannot connect, verify PostgreSQL is running, the port is correct, and the database user has SELECT permission.

## Model

Use Model view. Create relationships using the actual keys discovered in `00_schema_inspection.sql`.

Expected pattern:

- dim_customer (1) -> (*) fact_sales
- dim_product (1) -> (*) fact_sales
- dim_region (1) -> (*) fact_sales
- dim_date (1) -> (*) fact_sales

Use single-direction cross-filtering from dimensions to fact. Avoid many-to-many unless the data model genuinely requires it. Mark the date dimension as the Date table.

## Page 1 — Executive Overview

Canvas: 16:9. Suggested layout:
- Header: report title and last refresh date.
- First row: Total Revenue, Total Orders, Average Order Value, Unique Customers.
- Left/middle: monthly revenue line chart.
- Right: revenue by region bar chart.
- Bottom: category revenue bar/donut and top products table.
- Slicers: Year, Region, Category.

## Page 2 — Product & Customer Analytics

- Top 10 products by revenue (bar chart).
- Top 10 customers by revenue (bar chart).
- Revenue by category (column chart).
- Customer segment distribution (bar/donut).
- Customer table with customer, orders, revenue, AOV and rank.
- Slicers: Year, Region, Category.

For a customer segment visual, use a calculated grouping or a SQL-derived customer summary. Clearly label the segmentation rule.

## Page 3 — Regional & Time Intelligence

- Revenue by region (clustered bar).
- Monthly revenue trend (line).
- Quarterly revenue (column).
- YoY/MoM growth cards (only if valid date coverage exists).
- Matrix: Region x Year/Quarter with revenue.
- Slicers: Year, Quarter, Region.

## Page 4 — Customer Drill-through (optional but recommended)

1. Add a new page named `Customer Details`.
2. Add `dim_customer[customer_name]` to the Drill-through filters well.
3. Add cards for revenue, orders, AOV and units.
4. Add a monthly revenue trend and transaction detail table.
5. Add a Back button (Insert -> Buttons -> Back).
6. From Page 2, right-click a customer data point -> Drill through -> Customer Details.

## Navigation, bookmarks and tooltips

- Insert page navigator for page navigation.
- Add a bookmark for an alternate view only when it changes meaningful visual state.
- Create a report-page tooltip for product/customer details if useful.
- Test every slicer and drill-through interaction.

## Visual design

- Use a consistent 16:9 canvas.
- Use 4 KPI cards maximum across the first row.
- Use concise chart titles and descriptive axis labels.
- Avoid 3D charts and excessive donut charts.
- Keep consistent number formats and currency units.
- Add a small footer with data source and refresh date.
- Check readability at 100% zoom.

## Final QA

- Reconcile dashboard KPIs against SQL.
- Test slicers across all pages.
- Test drill-through and Back navigation.
- Confirm there are no broken visuals or blank categories.
- Save as `ecommerce_analytics.pbix` in this folder.
- Export a PDF or capture screenshots for the project evidence.
