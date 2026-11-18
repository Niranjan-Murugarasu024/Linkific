# Power BI DAX Measure Library

**Before using:** verify field names in Power BI Model view. These measures assume the fact table is named `fact_sales` and contains `revenue`, `order_id`, `quantity`, and `customer_key`. Rename fields to match the actual Gold schema.

## Core KPIs

```dax
Total Revenue =
SUM ( fact_sales[revenue] )

Total Orders =
DISTINCTCOUNT ( fact_sales[order_id] )

Unique Customers =
DISTINCTCOUNT ( fact_sales[customer_key] )

Units Sold =
SUM ( fact_sales[quantity] )

Average Order Value =
DIVIDE ( [Total Revenue], [Total Orders], 0 )

Revenue per Customer =
DIVIDE ( [Total Revenue], [Unique Customers], 0 )
```

## Customer and product metrics

```dax
Revenue per Order =
DIVIDE ( [Total Revenue], [Total Orders], 0 )

Orders per Customer =
DIVIDE ( [Total Orders], [Unique Customers], 0 )

Customer Rank =
RANKX (
    ALLSELECTED ( dim_customer[customer_name] ),
    [Total Revenue],
    ,
    DESC,
    DENSE
)

Product Rank =
RANKX (
    ALLSELECTED ( dim_product[product_name] ),
    [Total Revenue],
    ,
    DESC,
    DENSE
)
```

## Time intelligence

Assumption: `dim_date[full_date]` is a continuous Date column, marked as the Date table.

```dax
Revenue YTD =
TOTALYTD ( [Total Revenue], dim_date[full_date] )

Revenue Previous Year =
CALCULATE (
    [Total Revenue],
    SAMEPERIODLASTYEAR ( dim_date[full_date] )
)

Revenue YoY Change =
[Total Revenue] - [Revenue Previous Year]

Revenue YoY Growth % =
DIVIDE ( [Revenue YoY Change], [Revenue Previous Year], 0 )

Revenue Previous Month =
CALCULATE (
    [Total Revenue],
    DATEADD ( dim_date[full_date], -1, MONTH )
)

Revenue MoM Growth % =
DIVIDE (
    [Total Revenue] - [Revenue Previous Month],
    [Revenue Previous Month],
    0
)
```

## Optional measures

Only create these if the corresponding source fields/tables exist.

```dax
Total Discount =
SUM ( fact_sales[discount] )

Cancelled Orders =
CALCULATE (
    [Total Orders],
    fact_sales[order_status] = "Cancelled"
)

Target Revenue =
SUM ( fact_sales_targets[target_revenue] )

Target Achievement % =
DIVIDE ( [Total Revenue], [Target Revenue], 0 )
```

## Validation checklist

- Compare Total Revenue with a SQL `SUM(revenue)` under identical filters.
- Compare Total Orders with SQL `COUNT(DISTINCT order_id)`.
- Confirm order IDs are not repeated in a way that changes business meaning.
- Confirm cancelled/returned orders treatment.
- Validate YTD/YoY only when the date table and historical coverage support them.
- Format revenue as currency, percentages as percentage, and order/customer counts as whole numbers.
