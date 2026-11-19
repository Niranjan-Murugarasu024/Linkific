# 2. Data Dictionary

Complete this document from the actual PostgreSQL schema. Use `information_schema.columns` or
pgAdmin to verify data types and nullability.

## 2.1 Table inventory

| Table | Type (fact/dimension) | Grain | Primary key | Description |
|---|---|---|---|---|
| FactSales | Fact | [FILL IN] | [FILL IN] | Sales transactions |
| FactSalesTargets | Fact | [FILL IN] | [FILL IN] | Sales targets |
| DimProducts | Dimension | One row per [FILL IN] | [FILL IN] | Product attributes |
| DimCustomer | Dimension | One row per [FILL IN] | [FILL IN] | Customer attributes |
| DimRegion | Dimension | One row per [FILL IN] | [FILL IN] | Regional attributes |
| DimDate | Dimension | One row per date | [FILL IN] | Calendar attributes |

## 2.2 Column-level dictionary

| Table | Column | Data type | Key / constraint | Nullable? | Business meaning |
|---|---|---|---|---|---|
| FactSales | SalesID | [VERIFY] | [VERIFY] | [VERIFY] | Unique sales identifier |
| FactSales | ProductID | [VERIFY] | FK? [VERIFY] | [VERIFY] | Product reference |
| FactSales | CustomerID | [VERIFY] | FK? [VERIFY] | [VERIFY] | Customer reference |
| FactSales | Quantity | [VERIFY] | — | [VERIFY] | Units sold |
| FactSales | Revenue | [VERIFY] | — | [VERIFY] | Sales revenue |
| DimProducts | ProductID | [VERIFY] | PK? [VERIFY] | [VERIFY] | Product identifier |
| DimRegion | RegionID | [VERIFY] | PK? [VERIFY] | [VERIFY] | Region identifier |
| DimDate | DateKey | [VERIFY] | PK? [VERIFY] | [VERIFY] | Date dimension key |

Add every remaining column from the actual schema. Do not assume the example fields are exact.

## 2.3 Relationship inventory

| One-side table/key | Many-side table/key | Cardinality | Active? |
|---|---|---|---|
| DimProducts / [key] | FactSales / [key] | [VERIFY] | [VERIFY] |
| DimCustomer / [key] | FactSales / [key] | [VERIFY] | [VERIFY] |
| DimRegion / [key] | FactSales / [key] | [VERIFY] | [VERIFY] |
| DimRegion / [key] | FactSalesTargets / [key] | [VERIFY] | [VERIFY] |
| DimDate / [key] | FactSales / [key] | [VERIFY] | [VERIFY] |
| DimDate / [key] | FactSalesTargets / [key] | [VERIFY] | [VERIFY] |

## 2.4 Data conventions
- Currency and timezone: [FILL IN]
- Date format and calendar assumptions: [FILL IN]
- Null handling: [FILL IN]
- Duplicate definition: [FILL IN]
- Units and rounding: [FILL IN]
