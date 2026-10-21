-- Advanced practice: CTE, window functions, CASE, date operations
WITH order_totals AS (
  SELECT o.order_id, o.customer_id, o.order_date, o.status,
         COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total
  FROM orders o LEFT JOIN order_items oi USING (order_id)
  GROUP BY o.order_id
)
SELECT *, CASE WHEN total >= 10000 THEN 'high value'
               WHEN total >= 3000 THEN 'medium value'
               ELSE 'standard value' END AS order_segment
FROM order_totals ORDER BY total DESC;

WITH monthly AS (
  SELECT DATE_TRUNC('month', o.order_date)::date AS month,
         SUM(oi.quantity * oi.unit_price) AS gross_sales
  FROM orders o JOIN order_items oi USING (order_id)
  GROUP BY 1
)
SELECT month, gross_sales,
       LAG(gross_sales) OVER (ORDER BY month) AS previous_month_sales
FROM monthly ORDER BY month;

-- Inspect query plans. Compare plans before and after indexes on a larger dataset.
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders
WHERE customer_id = 1
ORDER BY order_date DESC;
