# Power BI E-commerce Sales Dashboard — Starter Project

This project is designed for a beginner Power BI assignment. It gives you local CSV sources, a PostgreSQL target table, a public JSON API practice query, a star-schema design, and starter DAX measures.

> **Important:** This is a starter project, not a finished `.pbix` report. Build and save the final interactive report in Power BI Desktop on Windows. The `.pbix` is a native Power BI file and must be authored in Power BI Desktop.

## 1. Project structure

```text
powerbi_ecommerce_starter/
├── data/
│   ├── sales.csv
│   ├── products.csv
│   ├── customers.csv
│   └── regions.csv
├── sql/
│   └── 01_create_sales_targets.sql
├── dax/
│   └── measures_and_date_table.dax
├── power_query/
│   └── api_products_demo.m
├── docs/
│   └── data_model.md
└── README.md
```

## 2. Install Power BI Desktop

1. On Windows, install the latest **64-bit Power BI Desktop** from the Microsoft Store or Microsoft's Download Center.
2. Open Power BI Desktop and select **Blank report**.
3. Save immediately as `Ecommerce_Sales_Dashboard.pbix` in a separate `output/` folder.
4. Check the version with **Help → About**. Power BI Desktop is updated monthly; use the current supported version.

Official install guide: https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop

## 3. Connect the CSV files

1. Select **Home → Get data → Text/CSV**.
2. Browse to this project's `data/sales.csv` and select **Transform Data**.
3. Repeat for `products.csv`, `customers.csv`, and `regions.csv`.
4. In Power Query, rename the queries exactly:
   - `sales` → `FactSales`
   - `products` → `DimProduct`
   - `customers` → `DimCustomer`
   - `regions` → `DimRegion`
5. Confirm column data types:
   - IDs: Whole Number
   - `OrderDate`, `ShipDate`, `SignupDate`: Date
   - `Quantity`: Whole Number
   - `UnitPrice`, `UnitCost`, `DiscountPct`, `ListPrice`: Decimal Number
   - names/categories: Text
6. For practice, perform these transformations:
   - Select `FactSales`: remove any columns you do not need (keep all fields listed in the data file for the measures below).
   - Filter out rows where `SalesID` is null.
   - Set `OrderDate` and `ShipDate` to Date, not Date/Time or Text.
   - Use **Split Column → By Delimiter** on a temporary copy of `CustomerName` if you want to practise splitting names; do not split the model's only customer-name field.
   - **Split and merge columns:** In `DimCustomer`, select `CustomerName` → **Split Column → By Delimiter** → space → split at the left-most delimiter. Rename the two results `FirstName` and `LastName`. You can then select those fields and use **Transform → Merge Columns** with a space separator to practise rebuilding a display name. Keep `CustomerID` unchanged.
   - **Append Queries practice:** The `data/append_practice/` folder contains two yearly extracts with the same schema. Import `sales_2025.csv` and `sales_2026.csv` as `Sales_2025_Staging` and `Sales_2026_Staging`; apply the same data types to both; then choose **Home → Append Queries → Append Queries as New**, select the two staging queries, and name the result `FactSales_AppendPractice`. Check that the appended row count equals the row count of `sales.csv` (900). For the main model, use either the original `sales.csv` query renamed `FactSales`, or the appended result renamed `FactSales`—not both. Disable load for staging queries if you use the appended result.
   - **Merge Queries practice:** Duplicate `FactSales` as `Sales_Product_Preview`. Select **Home → Merge Queries**, join `ProductID` to `DimProduct[ProductID]` using **Left Outer**; expand `ProductName` and `Category`. This is a learning preview only. Disable its load and keep the final model normalized with separate dimension and fact tables.
7. Select **Home → Close & Apply**.

### Excel source practice

The provided pack uses CSVs so the source is easy to inspect and version. You can also test Excel import with any `.xlsx` workbook: **Get data → Excel workbook → select the workbook and tables/sheets → Transform Data**. Convert the Excel range to a named Excel Table before importing where possible.

## 4. Connect PostgreSQL targets

The SQL file creates `pbi_demo.sales_targets` inside the database you choose. It does not create a database or delete other objects.

1. Open pgAdmin or DBeaver and connect to your local PostgreSQL server.
2. Select the database you intend to use with Power BI (for example, a training database).
3. Open Query Tool and run `sql/01_create_sales_targets.sql`.
4. Run the final `SELECT` in the script and verify that rows appear.
5. In Power BI Desktop choose **Home → Get data → PostgreSQL database**.
6. Server: `localhost:5432` (or the host/port where PostgreSQL is running).
7. Database: enter the exact database where you ran the script.
8. Choose **Import** for this beginner project. Import loads a snapshot into the Power BI model; refresh to retrieve updated rows.
9. Authenticate with **Database** and your PostgreSQL username/password.
10. In Navigator select `pbi_demo.sales_targets`, then select **Transform Data**.
11. Rename the query to `FactSalesTargets`; set `month_start` to Date, `region_id` to Whole Number, and `target_sales` to Fixed Decimal/Currency; then **Close & Apply**.

Power BI Desktop includes the Npgsql provider for the PostgreSQL connector in current supported versions; if a connection fails, update Desktop first and inspect the connector error/credentials. Official connector guide: https://learn.microsoft.com/en-us/power-query/connectors/postgresql

## 5. Connect to a Web API (practice query)

This is a separate API exercise. It returns demo product records and is **not** related to the fictional sales rows, so do not create a relationship to `DimProduct`.

### UI method

1. Select **Home → Get data → Web**.
2. Enter `https://dummyjson.com/products?limit=10`.
3. Choose Anonymous if prompted and connect.
4. In Power Query, expand the `products` list and then expand the record fields such as title, category, price, rating, stock, and brand.
5. Rename the query `API_Practice_Products` and load it as a disconnected practice table, or disable load if you only want to demonstrate query transformation.

### Advanced Editor method

Alternatively, choose **Transform data → New Source → Blank Query → Advanced Editor**, paste the contents of `power_query/api_products_demo.m`, and name the query `API_Practice_Products`.

The API is a public demo endpoint; it may change availability or its response schema. If it fails, use the Web connector with a stable JSON endpoint that your organization permits. Official Web connector guide: https://learn.microsoft.com/en-us/power-query/connectors/web/web

## 6. Build the model

1. Open **Model view** (diagram icon on the left rail).
2. Create the `DimDate` calculated table using the DAX expression in `dax/measures_and_date_table.dax` (copy only the `DimDate = ...` expression into **Modeling → New table**).
3. Select `DimDate`, then **Table tools → Mark as date table → Date**.
4. Create the six relationships documented in `docs/data_model.md`.
5. For each relationship set **Cardinality = One to many (1:*)**, **Cross-filter direction = Single**, and **Make this relationship active**.
6. Hide technical key columns from Report view if that makes field selection clearer. Do not delete them; relationships need them.
7. In `DimDate`, sort `Month` by `Month Number` if you use the month-name field on an axis.

Model view should show dimensions filtering facts. Avoid many-to-many relationships for this starter model and do not link the two fact tables directly.

## 7. Add DAX measures

Choose **Modeling → New measure** and create each measure from `dax/measures_and_date_table.dax` (skip the calculated-table section if you already created `DimDate`). Create measures one at a time. The provided measures cover:

- Total Sales, Total Cost, Total Profit, Profit Margin
- Units, distinct Orders, Average Order Value, Average Discount
- Sales Target, Target Variance, Target Attainment
- Sales YTD, Previous Year Sales, YoY Growth

Format currency measures as INR (₹) and percentage measures as Percentage. Since the data is synthetic, the figures are for learning and are not real company performance.

## 8. Build the report pages

### Page 1 — Executive Overview

- 4 KPI cards: **Total Sales**, **Total Profit**, **Total Orders**, **Profit Margin %**.
- Line chart: `DimDate[Year Month]` on X-axis, `[Total Sales]` on Y-axis.
- Clustered bar chart: `DimProduct[Category]` by `[Total Sales]`.
- Donut chart: `DimCustomer[Segment]` by `[Total Sales]`.
- Slicers: `DimDate[Year]`, `DimRegion[RegionName]`, `DimProduct[Category]`.

### Page 2 — Product & Region Analysis

- Matrix: Category → Subcategory → ProductName; values `[Total Sales]`, `[Total Profit]`, `[Profit Margin %]`.
- Bar chart: Region by `[Total Sales]`.
- Bar chart: Product by `[Total Units]` (Top N 10 filter optional).
- Slicers: Category, Region, Year.

### Page 3 — Target Tracking

- KPI cards: `[Sales Target]`, `[Target Variance]`, `[Target Attainment %]`.
- Clustered column chart: `DimDate[Year Month]` with `[Total Sales]` and `[Sales Target]`.
- Matrix: Region rows; Sales, Target, Variance and Attainment values.
- Slicers: Year and Region.

### Interaction and formatting

- Add slicers and verify that selecting a year/region/category updates all relevant visuals.
- Use **Format → Edit interactions** to control whether a slicer filters or highlights each visual.
- Give each page a descriptive title; use consistent number formats, readable labels, and restrained colors.
- Avoid 3D charts, too many visuals, and decorative elements that obscure the data.

## 9. Validation checklist

- [ ] CSV tables load and row counts are non-zero.
- [ ] PostgreSQL target query loads and contains month/region combinations.
- [ ] API query returns demo JSON records (or is clearly documented as a separate practice query).
- [ ] No duplicate keys in dimension key columns.
- [ ] All six model relationships are active 1:* and single-direction.
- [ ] `Total Sales` and `Total Profit` return values.
- [ ] Slicers filter KPI cards, charts, and matrices correctly.
- [ ] Target analysis has values for the selected year/month/region.
- [ ] Save the `.pbix`, close Power BI Desktop, reopen it, and confirm visuals still render.

## 10. Deliverables to submit

1. `Ecommerce_Sales_Dashboard.pbix` — the Power BI Desktop file you create.
2. This starter project folder (or its ZIP) — CSV sources, SQL setup, DAX measures, and API M query.
3. `README.md` — this guide.
4. Screenshots of Model view and each report page, if your evaluator asks for evidence.

## Learning references

- Power BI Desktop install: https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop
- PostgreSQL connector: https://learn.microsoft.com/en-us/power-query/connectors/postgresql
- Web connector: https://learn.microsoft.com/en-us/power-query/connectors/web/web
- Star schema: https://learn.microsoft.com/en-us/power-bi/guidance/star-schema
- Relationships: https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-relationships-understand
- DAX basics: https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-quickstart-learn-dax-basics
