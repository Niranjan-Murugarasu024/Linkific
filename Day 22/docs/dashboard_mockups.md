# Dashboard Mockups

The following are report specifications, not a finished Power BI file. Connect
Power BI Desktop to the PostgreSQL `warehouse` schema after loading sample data.

## Should the project include a Power BI dashboard?

**Recommended: yes, for a complete e-commerce analytics demo.** The assignment's
formal deliverables call for dashboard requirements and mockups rather than a
published `.pbix`, so the written design satisfies that documentation item.
However, the suggested e-commerce project explicitly includes a Power BI
dashboard. Build and submit a small `.pbix` if the task is assessed as a
working end-to-end analytics platform; publication to Power BI Service is not
necessary unless specifically requested.

Prioritize the Sales Overview and Inventory Monitoring pages. Use the
PostgreSQL `warehouse` schema as the source, and include the report file plus
screenshots in the demonstration deliverables.

## Page 1 — Sales Overview
- KPI cards: Net Sales, Sales Lines, Units Sold, Average Order Value.
- Monthly net-sales trend.
- Sales by product category and region.
- Slicers: date, region, category.

## Page 2 — Inventory Monitoring
- KPI cards: Available Units, Stock Value, Low-Stock Product/Region Count.
- Inventory by category and region.
- Table of product-region pairs where available quantity is below reorder level.
- Snapshot-date slicer.

## Page 3 — Customer Analytics
- KPI cards: Customers Purchasing, Repeat Customers, Average Spend.
- Sales by customer segment and city.
- Top customers by net sales and repeat purchase trend.

## Page 4 — Regional Performance
- Net sales by region and month.
- Category mix by region.
- Drill-through from a region to its products and customers.

## Metric definitions
- Net sales is the sum of `fact_sales.sales_amount`.
- Sales lines are counted using distinct `source_sales_id`; order count needs a
  separate order identifier if a sales line ID is not an order ID.
- Average order value requires a true order-level key and must not be computed
  by treating each line as an order.
- Low stock means `available_quantity < reorder_level`.
- Inventory value is the stored cost value of each snapshot. Use one snapshot
  date at a time for current stock totals.

The sample data is intentionally small and should only be used to validate
connectivity and report layout.
