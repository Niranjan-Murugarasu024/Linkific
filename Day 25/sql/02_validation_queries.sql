-- Row counts
SELECT 'fact_sales' AS table_name, COUNT(*) AS row_count FROM analytics.fact_sales
UNION ALL SELECT 'dim_customer', COUNT(*) FROM analytics.dim_customer
UNION ALL SELECT 'dim_product', COUNT(*) FROM analytics.dim_product
UNION ALL SELECT 'dim_region', COUNT(*) FROM analytics.dim_region;

-- Revenue by month
SELECT d.year, d.month, d.month_name,
       SUM(f.net_amount) AS net_revenue,
       COUNT(DISTINCT f.order_id) AS orders
FROM analytics.fact_sales f
JOIN analytics.dim_date d ON d.date_key = f.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- Referential integrity check (should return zero)
SELECT COUNT(*) AS orphaned_fact_rows
FROM analytics.fact_sales f
LEFT JOIN analytics.dim_customer c ON c.customer_key = f.customer_key
LEFT JOIN analytics.dim_product p ON p.product_key = f.product_key
LEFT JOIN analytics.dim_region r ON r.region_key = f.region_key
LEFT JOIN analytics.dim_date d ON d.date_key = f.date_key
WHERE c.customer_key IS NULL OR p.product_key IS NULL
   OR r.region_key IS NULL OR d.date_key IS NULL;

-- Pipeline history
SELECT * FROM analytics.pipeline_audit ORDER BY created_at DESC LIMIT 20;
