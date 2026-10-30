# Data model design

## Table grain

- **FactSales**: one row per order line (not one row per order). `SalesID` is the row identifier. `OrderID` can repeat because an order may contain multiple product lines.
- **FactSalesTargets**: one row per month and region (`month_start`, `region_id`). This is a separate periodic snapshot/target fact table.
- **DimProduct**: one row per product.
- **DimCustomer**: one row per customer.
- **DimRegion**: one row per sales region.
- **DimDate**: one row per calendar date, created in DAX.

## Relationships to create

| One-side table/column | Many-side table/column | Cardinality | Cross-filter |
|---|---|---|---|
| DimDate[Date] | FactSales[OrderDate] | 1:* | Single |
| DimProduct[ProductID] | FactSales[ProductID] | 1:* | Single |
| DimCustomer[CustomerID] | FactSales[CustomerID] | 1:* | Single |
| DimRegion[RegionID] | FactSales[RegionID] | 1:* | Single |
| DimDate[Date] | FactSalesTargets[month_start] | 1:* | Single |
| DimRegion[RegionID] | FactSalesTargets[region_id] | 1:* | Single |

Use active relationships. Keep the normal dimension-to-fact filter direction (Single) unless a specific requirement proves otherwise. Do not create a direct relationship between FactSales and FactSalesTargets.

## Star-schema sketch

```text
                    DimProduct
                         |
DimCustomer ---- FactSales ---- DimDate
                         |
                     DimRegion
                         |
                 FactSalesTargets
                         |
                       DimDate
```

`DimDate` and `DimRegion` are shared dimensions used by both fact tables. `FactSales` and `FactSalesTargets` must not be joined directly.
