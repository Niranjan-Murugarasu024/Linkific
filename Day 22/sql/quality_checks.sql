SELECT
    'invalid_sales_measures' AS check_name,
    COUNT(*)::BIGINT AS violations
FROM warehouse.fact_sales
WHERE quantity <= 0
    OR unit_price < 0
    OR discount_amount < 0
    OR sales_amount < 0
UNION ALL
SELECT
    'invalid_inventory_measures' AS check_name,
    COUNT(*)::BIGINT AS violations
FROM warehouse.fact_inventory
WHERE available_quantity < 0
    OR reorder_level < 0
    OR stock_value < 0
UNION ALL
SELECT
    'duplicate_sales_source_ids' AS check_name,
    COUNT(*)::BIGINT AS violations
FROM (
    SELECT source_sales_id
    FROM warehouse.fact_sales
    GROUP BY source_sales_id
    HAVING COUNT(*) > 1
) AS duplicate_sales;
