-- Sample challenge solutions
-- 1. Second-highest distinct product price
SELECT MAX(unit_price) AS second_highest_price
FROM products
WHERE unit_price < (SELECT MAX(unit_price) FROM products);

-- 2. Customers with no successful payment on any order
SELECT c.customer_id, c.first_name, c.last_name
FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM orders o JOIN payments p USING (order_id)
  WHERE o.customer_id = c.customer_id AND p.payment_status = 'successful'
);

-- 3. Top product in each category by units sold
WITH product_sales AS (
  SELECT p.product_id, p.product_name, p.category_id,
         COALESCE(SUM(oi.quantity),0) AS units_sold
  FROM products p LEFT JOIN order_items oi USING (product_id)
  GROUP BY p.product_id
)
SELECT * FROM (
  SELECT ps.*, RANK() OVER (PARTITION BY category_id ORDER BY units_sold DESC) AS rnk
  FROM product_sales ps
) ranked WHERE rnk = 1;
