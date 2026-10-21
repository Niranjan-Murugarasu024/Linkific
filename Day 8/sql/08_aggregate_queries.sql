-- Aggregation and GROUP BY practice
SELECT category_id, COUNT(*) AS product_count, ROUND(AVG(unit_price),2) AS average_price
FROM products GROUP BY category_id ORDER BY category_id;

SELECT status, COUNT(*) AS order_count
FROM orders GROUP BY status HAVING COUNT(*) >= 2 ORDER BY order_count DESC;

SELECT customer_id, COUNT(*) AS order_count
FROM orders GROUP BY customer_id ORDER BY order_count DESC;

SELECT p.product_name, SUM(oi.quantity) AS total_units
FROM order_items oi JOIN products p USING (product_id)
GROUP BY p.product_id, p.product_name
ORDER BY total_units DESC;
