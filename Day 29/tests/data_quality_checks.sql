-- Adapt identifiers and business rules to the actual schema before execution.
-- Run in a test/read-only context first. These are diagnostic examples, not guaranteed drop-in SQL.

-- 1. Inspect available tables and columns.
SELECT table_schema, table_name, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name, ordinal_position;

-- 2. Example row counts. Verify table names first.
-- SELECT 'FactSales' AS table_name, COUNT(*) AS row_count FROM public."FactSales"
-- UNION ALL
-- SELECT 'FactSalesTargets', COUNT(*) FROM public."FactSalesTargets";

-- 3. Example null checks. Replace the key/column names if needed.
-- SELECT COUNT(*) AS missing_product_ids
-- FROM public."FactSales"
-- WHERE "ProductID" IS NULL;

-- 4. Example duplicate-key check. Replace with the actual business key.
-- SELECT "SalesID", COUNT(*) AS occurrences
-- FROM public."FactSales"
-- GROUP BY "SalesID"
-- HAVING COUNT(*) > 1;

-- 5. Example orphan-reference check. Confirm key names and relationship first.
-- SELECT COUNT(*) AS orphan_product_references
-- FROM public."FactSales" f
-- LEFT JOIN public."DimProducts" p
--   ON f."ProductID" = p."ProductID"
-- WHERE f."ProductID" IS NOT NULL
--   AND p."ProductID" IS NULL;

-- 6. Example reconciliation. Confirm revenue definition and filters match Power BI.
-- SELECT SUM("Revenue") AS total_revenue
-- FROM public."FactSales";
