-- Day 29 read-only checks for Day 24's day24_gold star schema.
-- Run against the database containing day24_gold. Zero-valued counters and
-- zero-row violation queries indicate passing checks. Exact counts scan tables.

-- 1. Confirm the actual gold-layer columns.
SELECT table_name, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'day24_gold'
ORDER BY table_name, ordinal_position;

-- 2. Exact row counts for the five gold tables.
SELECT 'dim_customer' AS table_name, COUNT(*) AS row_count FROM day24_gold.dim_customer
UNION ALL SELECT 'dim_date', COUNT(*) FROM day24_gold.dim_date
UNION ALL SELECT 'dim_product', COUNT(*) FROM day24_gold.dim_product
UNION ALL SELECT 'dim_region', COUNT(*) FROM day24_gold.dim_region
UNION ALL SELECT 'fact_sales', COUNT(*) FROM day24_gold.fact_sales
ORDER BY table_name;

-- 3. Verify the fact grain and dimension relationships from declared keys.
-- This reads PostgreSQL metadata; it avoids rescanning fact rows to re-prove
-- the primary key and foreign keys already enforced by the database.
SELECT
    table_namespace.nspname || '.' || table_rel.relname AS table_name,
    constraint_info.conname AS constraint_name,
    CASE constraint_info.contype
        WHEN 'p' THEN 'PRIMARY KEY'
        WHEN 'f' THEN 'FOREIGN KEY'
        WHEN 'u' THEN 'UNIQUE'
        ELSE constraint_info.contype::text
    END AS constraint_type,
    pg_get_constraintdef(constraint_info.oid) AS definition
FROM pg_constraint constraint_info
JOIN pg_class table_rel
    ON table_rel.oid = constraint_info.conrelid
JOIN pg_namespace table_namespace
    ON table_namespace.oid = table_rel.relnamespace
WHERE table_namespace.nspname = 'day24_gold'
ORDER BY table_rel.relname, constraint_info.conname;

-- 4. Check fact measures, arithmetic, foreign-key lookups, and report totals
-- in one fact-table pass. Dimension primary-key indexes support the joins.
SELECT
    COUNT(*) AS fact_rows,
    COALESCE(SUM(f.gross_amount), 0) AS total_gross_amount,
    COALESCE(SUM(f.discount_amount), 0) AS total_discount_amount,
    COALESCE(SUM(f.net_amount), 0) AS total_net_amount,
    COUNT(*) FILTER (
        WHERE f.quantity <= 0
           OR f.unit_price < 0
           OR f.discount_pct NOT BETWEEN 0 AND 1
           OR f.gross_amount < 0
           OR f.discount_amount < 0
           OR f.net_amount < 0
    ) AS rows_with_invalid_measures,
    COUNT(*) FILTER (
        WHERE ABS(f.gross_amount - (f.quantity * f.unit_price)) > 0.01
           OR ABS(f.discount_amount - (f.gross_amount * f.discount_pct)) > 0.01
           OR ABS(f.net_amount - (f.gross_amount - f.discount_amount)) > 0.01
    ) AS rows_with_inconsistent_amounts,
    COUNT(*) FILTER (WHERE d.date_key IS NULL) AS missing_date_dimension_rows,
    COUNT(*) FILTER (WHERE c.customer_key IS NULL) AS missing_customer_dimension_rows,
    COUNT(*) FILTER (WHERE p.product_key IS NULL) AS missing_product_dimension_rows,
    COUNT(*) FILTER (WHERE r.region_key IS NULL) AS missing_region_dimension_rows
FROM day24_gold.fact_sales f
LEFT JOIN day24_gold.dim_date d ON d.date_key = f.date_key
LEFT JOIN day24_gold.dim_customer c ON c.customer_key = f.customer_key
LEFT JOIN day24_gold.dim_product p ON p.product_key = f.product_key
LEFT JOIN day24_gold.dim_region r ON r.region_key = f.region_key;

-- 5. Check the customer-to-region relationship.
SELECT COUNT(*) AS customers_without_region
FROM day24_gold.dim_customer c
LEFT JOIN day24_gold.dim_region r ON r.region_key = c.region_key
WHERE r.region_key IS NULL;

-- 6. Check natural-key uniqueness; these columns do not have unique
-- constraints in the inspected schema.
SELECT 'dim_customer.customer_id' AS natural_key, COUNT(*) AS duplicate_groups
FROM (
    SELECT customer_id
    FROM day24_gold.dim_customer
    GROUP BY customer_id
    HAVING COUNT(*) > 1
) duplicates
UNION ALL
SELECT 'dim_product.product_id', COUNT(*)
FROM (
    SELECT product_id
    FROM day24_gold.dim_product
    GROUP BY product_id
    HAVING COUNT(*) > 1
) duplicates
UNION ALL
SELECT 'dim_region.region_id', COUNT(*)
FROM (
    SELECT region_id
    FROM day24_gold.dim_region
    GROUP BY region_id
    HAVING COUNT(*) > 1
) duplicates
UNION ALL
SELECT 'dim_date.full_date', COUNT(*)
FROM (
    SELECT full_date
    FROM day24_gold.dim_date
    GROUP BY full_date
    HAVING COUNT(*) > 1
) duplicates
ORDER BY natural_key;

-- 7. Check that the date key and calendar attributes match full_date.
SELECT COUNT(*) AS inconsistent_date_rows
FROM day24_gold.dim_date
WHERE date_key <> TO_CHAR(full_date, 'YYYYMMDD')::INTEGER
   OR year <> EXTRACT(YEAR FROM full_date)::INTEGER
   OR quarter <> EXTRACT(QUARTER FROM full_date)::INTEGER
   OR month <> EXTRACT(MONTH FROM full_date)::INTEGER
   OR day <> EXTRACT(DAY FROM full_date)::INTEGER;
