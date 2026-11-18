-- Run this first against ecommerce_practice.
-- It reveals actual columns, types, primary keys and foreign keys.
-- Set the schema below if your Gold schema has a different name.

SELECT table_schema, table_name, ordinal_position, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'day24_gold'
  AND table_name IN ('fact_sales', 'dim_customer', 'dim_product', 'dim_region', 'dim_date')
ORDER BY table_name, ordinal_position;

-- Primary keys
SELECT tc.table_name, kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name
 AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'PRIMARY KEY'
  AND tc.table_schema = 'day24_gold'
ORDER BY tc.table_name, kcu.ordinal_position;

-- Foreign keys
SELECT
    tc.table_name AS source_table,
    kcu.column_name AS source_column,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name
 AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
  ON ccu.constraint_name = tc.constraint_name
 AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'day24_gold'
ORDER BY source_table, source_column;

-- Row counts (edit if your table names differ)
SELECT 'fact_sales' AS table_name, COUNT(*) AS row_count FROM day24_gold.fact_sales
UNION ALL SELECT 'dim_customer', COUNT(*) FROM day24_gold.dim_customer
UNION ALL SELECT 'dim_product', COUNT(*) FROM day24_gold.dim_product
UNION ALL SELECT 'dim_region', COUNT(*) FROM day24_gold.dim_region
UNION ALL SELECT 'dim_date', COUNT(*) FROM day24_gold.dim_date;

-- Preview rows
SELECT * FROM day24_gold.fact_sales LIMIT 10;
SELECT * FROM day24_gold.dim_customer LIMIT 10;
SELECT * FROM day24_gold.dim_product LIMIT 10;
SELECT * FROM day24_gold.dim_region LIMIT 10;
SELECT * FROM day24_gold.dim_date LIMIT 10;
