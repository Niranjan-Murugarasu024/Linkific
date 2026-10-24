-- Table counts.
SELECT 'dim_customer' table_name,COUNT(*) row_count FROM dim_customer
UNION ALL SELECT 'dim_product',COUNT(*) FROM dim_product
UNION ALL SELECT 'dim_date',COUNT(*) FROM dim_date
UNION ALL SELECT 'dim_channel',COUNT(*) FROM dim_channel
UNION ALL SELECT 'fact_sales',COUNT(*) FROM fact_sales ORDER BY table_name;

-- Expected to return no rows: each customer has exactly one current version.
SELECT customer_id,COUNT(*) current_versions FROM dim_customer WHERE is_current
GROUP BY customer_id HAVING COUNT(*)<>1;

-- Expected to return no rows: historical validity intervals do not overlap.
WITH w AS (
 SELECT customer_id,customer_sk,valid_from,valid_to,
        LAG(valid_to) OVER(PARTITION BY customer_id ORDER BY valid_from,customer_sk) previous_valid_to
 FROM dim_customer
)
SELECT * FROM w WHERE previous_valid_to IS NOT NULL AND previous_valid_to > valid_from;

-- Expected to return no rows: measure arithmetic is consistent.
SELECT * FROM fact_sales
WHERE gross_amount<>ROUND(quantity*unit_price,2)
   OR net_amount<>ROUND(gross_amount-discount_amount,2);

-- Sales staging rows that failed to resolve to a fact row; investigate rather than ignore.
SELECT s.* FROM stg_sales s LEFT JOIN fact_sales f
 ON f.order_id=s.order_id AND f.order_line_id=s.order_line_id WHERE f.sales_sk IS NULL;

-- Expected to return no rows: source order-line key is unique.
SELECT order_id,order_line_id,COUNT(*) FROM stg_sales
GROUP BY order_id,order_line_id HAVING COUNT(*)>1;
