# Quick Glossary

| Term | Meaning |
|---|---|
| OLTP | Operational transactions and writes. |
| OLAP | Analytical queries and aggregations. |
| Fact grain | What one fact row represents. |
| Fact table | Events/measures joined to dimensions. |
| Dimension | Descriptive context for slicing facts. |
| Star schema | Fact links directly to dimensions. |
| Snowflake schema | Normalized dimension sub-tables. |
| Galaxy schema | Multiple facts share conformed dimensions. |
| Natural key | Source/business identifier. |
| Surrogate key | Warehouse-generated identifier. |
| SCD1 | Overwrite attribute, discard previous value. |
| SCD2 | Insert a version with effective dates. |
| SCD3 | Keep limited prior value in extra columns. |
| Conformed dimension | Shared definition/key policy across facts. |
| Late-arriving fact | Event arrives after its expected reporting time. |
| Late-arriving dimension | Dimension context arrives after the referencing event. |
