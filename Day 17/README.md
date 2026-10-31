# Advanced Power BI & DAX Day Task

## Project
Extend the existing `Ecommerce_Sales_Dashboard.pbix` with advanced DAX, time intelligence, rankings, drill-through, bookmarks, buttons, navigation, and conditional formatting.

This guide assumes the existing model contains:

- `FactSales`
- `DimProducts`
- `DimCustomer`
- `DimRegion`
- `FactSalesTargets`
- `DimDate`

Existing measures include `[Total Sales]`, `[Total Profit]`, `[Total Orders]`, `[Total Units]`, `[Sales Target]`, `[Target Achievement %]`, `[Profit Margin %]`, `[Average Order Value]`, `[Target Variance]`, `[Active Customers]`, `[Distinct Products Sold]`, `[Target Variance %]`, `[Target Status]`, and `[Target Status Color]`.

Check the exact names in your Fields pane before pasting formulas. DAX formulas in `DAX_Library.dax` are reference snippets; create each measure or calculated column separately in Power BI Desktop.

## 1. Save a working copy

Use **File → Save As** and save a copy named `Ecommerce_Sales_Advanced_DAX.pbix`. Keep the previous version as a checkpoint.

## 2. Calculated column versus measure

Create the calculated column `FactSales[Line Net Sales]`:

```dax
Line Net Sales =
    FactSales[Quantity]
        * FactSales[UnitPrice]
        * ( 1 - FactSales[DiscountPct] )
```

This is a row-level amount calculated and stored at model refresh. Then create `[Total Sales (Column Check)]` as `SUM(FactSales[Line Net Sales])` and `[Sales Reconciliation Difference]` as `[Total Sales] - [Total Sales (Column Check)]`. The difference should be zero (or a negligible rounding difference) when the calculation matches the existing `[Total Sales]` measure.

A measure is evaluated at query time under the current filter context. A calculated column is evaluated row by row at refresh and stored in the model. Use measures for report KPIs and most aggregations; use calculated columns when a row-level attribute is genuinely needed for grouping, filtering, or relationships.

## 3. Advanced DAX practice

Create the formulas in `DAX_Library.dax` one at a time:

- Iterators: `SUMX`, `AVERAGEX`
- Context modification: `CALCULATE`
- Table filtering: `FILTER`
- Filter removal: `ALL`
- Preserve one grouping: `ALLEXCEPT`
- Time intelligence: `SAMEPERIODLASTYEAR`, `TOTALYTD`, `TOTALQTD`, `TOTALMTD`
- Cumulative analysis: running total
- Trend smoothing: three-month moving average
- Ranking: `RANKX`

### Required model conditions for time intelligence

1. `DimDate[Date]` must contain a continuous calendar with no gaps.
2. `DimDate[Date]` must be marked as the model's date table.
3. The active relationship must be `DimDate[Date]` (one) to `FactSales[OrderDate]` (many).
4. Use `DimDate[Year Month]` on monthly chart axes and sort it by `DimDate[YearMonthSort]`.
5. The source data covers 2025–2026. Prior-year measures for 2025 will be blank because 2024 data is not present.

## 4. Add advanced visuals to the existing report

### Page 1 – Executive Overview

Add:
- `[Sales Previous Year]`
- `[YoY Growth %]`
- `[Sales YTD]`
- `[Running Total Sales]`

Suggested visuals:
- KPI card: YoY Growth %
- Line chart: `DimDate[Year Month]` with `[Total Sales]` and `[Sales 3M Moving Average]`
- Line chart or area chart: `[Running Total Sales]`

### Page 2 – Product & Regional Analysis

Add:
- `[Product Revenue Rank]`
- `[Region Sales Rank]`
- `[Product Sales Contribution %]`
- `[Category Sales – Keep Category]`

Use Product Revenue Rank in a visual-level filter (`is less than or equal to 10`) as an alternative to the Top N filter. Add the rank as a displayed column in the product matrix if useful.

### Page 3 – Sales Target Tracking

Retain the existing target calculations. Use `[Sales Target]`, `[Target Variance]`, `[Target Variance %]`, `[Target Achievement %]`, and `[Target Status]`. Compare targets only at the month/region grain because the PostgreSQL target table has no product or customer-segment allocation.

## 5. Drill-through page – Product Details

1. Add a new page and name it `Product Details`.
2. In the Visualizations/Build pane, locate the **Drill-through** field well.
3. Drag `DimProducts[ProductName]` into the drill-through field well.
4. Keep **Keep all filters** enabled if you want Year, Region, Category, and other applicable source filters passed to the detail page.
5. Add four cards: `[Total Sales]`, `[Total Profit]`, `[Total Units]`, `[Profit Margin %]`.
6. Add a line chart with `DimDate[Year Month]` and `[Total Sales]`.
7. Add a table with `FactSales[OrderDate]`, `FactSales[OrderID]`, `FactSales[Quantity]`, `FactSales[UnitPrice]`, and `FactSales[DiscountPct]`.
8. Power BI normally adds a Back button when a drill-through field is added. If not, insert **Buttons → Back** and set its action to Back.
9. Test from Page 2: right-click a product bar or product row → Drill through → Product Details.
10. Optionally hide the Product Details page tab after testing; hidden drill-through pages remain accessible through the drill-through action.

If ProductName is not unique in the source, use ProductID (or ProductID plus ProductName) as the drill-through key and ensure the same key is present in the source visual.

## 6. Bookmarks – Chart/Table toggle

A useful practice is to toggle between a Top Products bar chart and a detailed product table in the same location on Page 2.

1. Add the table visual and position it exactly over the Top 10 product bar chart.
2. Open **View → Selection** and **View → Bookmarks**.
3. Hide the table and show the chart in the Selection pane.
4. Add a bookmark named `Top Products – Chart`.
5. In the bookmark options, turn **Data Off**, **Display On**, and **Current page On**. Use **Selected visuals** when managing only the two overlapping visuals.
6. Hide the chart and show the table. Add a second bookmark named `Top Products – Table` with the same bookmark options.
7. Add two buttons labelled `Chart View` and `Table View`.
8. For each button, set **Action On → Type Bookmark** and select the corresponding bookmark.
9. Test that changing slicers does not reset their selections when switching views. If slicers reset, verify the bookmark's Data option is Off.

## 7. Buttons and page navigation

1. On a main report page, choose **Insert → Buttons → Navigator → Page navigator** (menu wording may vary by Power BI version).
2. Format the navigator to match the Navy/Teal report theme.
3. Ensure the Product Details drill-through page is hidden if you do not want it in the main navigation.
4. Add the same page navigator to Pages 1–3, or copy/paste it between pages.
5. Use the Back button on the drill-through page to return to the source page.

## 8. Conditional formatting

- Product matrix: apply data bars to `[Total Sales]`.
- Product matrix: apply a colour scale to `[Profit Margin %]`.
- Target matrix: apply rule-based background formatting to `[Target Variance]` (negative = muted red, non-negative = teal).
- Target Status: apply **Conditional formatting → Background color → Format style: Field value** and choose `[Target Status Color]`. Do not add the colour measure as a visible business-value column.

## 9. Validation checklist

- `[Sales Reconciliation Difference]` equals zero or a negligible rounding difference.
- 2026 YoY measures compare 2026 with 2025; 2025 prior-year measures are blank because 2024 is not in the source.
- YTD resets at the start of each year.
- Running total accumulates in chronological order and responds to selected date ranges.
- The three-month moving average uses monthly totals, not daily averages.
- Product rank changes appropriately with Year, Region, and Category selections.
- Drill-through opens the correct product and retains intended filter context.
- Bookmark switching does not reset slicer values.
- Page navigation buttons open the correct pages.
- Target comparisons remain at month/region grain.

## 10. Final deliverables

- `Ecommerce_Sales_Advanced_DAX.pbix`
- `DAX_Library.dax`
- `README.md`
- Screenshots of Pages 1–3 and the Product Details drill-through page

**Important:** This starter documentation does not contain your PBIX file. The report visuals, bookmarks, buttons, and drill-through page must be created and saved in Power BI Desktop.
