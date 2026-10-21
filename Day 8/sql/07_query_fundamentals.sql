-- 01. List every customer
SELECT * FROM customers ORDER BY customer_id;

-- 02. Show customer names and emails
SELECT first_name, last_name, email FROM customers ORDER BY last_name;

-- 03. Find customers in Tamil Nadu
SELECT * FROM customers WHERE state = 'Tamil Nadu';

-- 04. Find customers not in Tamil Nadu
SELECT * FROM customers WHERE state <> 'Tamil Nadu';

-- 05. Find customers in Chennai or Coimbatore
SELECT * FROM customers WHERE city IN ('Chennai','Coimbatore');

-- 06. Find products priced from 500 to 2500
SELECT product_name, unit_price FROM products WHERE unit_price BETWEEN 500 AND 2500 ORDER BY unit_price;

-- 07. Find product names containing 'book'
SELECT * FROM products WHERE product_name ILIKE '%book%';

-- 08. Find products whose names start with 'B'
SELECT * FROM products WHERE product_name ILIKE 'B%';

-- 09. Find customers whose email ends in example.com
SELECT * FROM customers WHERE email LIKE '%@example.com';

-- 10. List the five most expensive products
SELECT product_name, unit_price FROM products ORDER BY unit_price DESC LIMIT 5;

-- 11. List the cheapest three products
SELECT product_name, unit_price FROM products ORDER BY unit_price ASC LIMIT 3;

-- 12. List unique customer states
SELECT DISTINCT state FROM customers ORDER BY state;

-- 13. Count customers
SELECT COUNT(*) AS customer_count FROM customers;

-- 14. Count products per category
SELECT c.category_name, COUNT(p.product_id) AS product_count FROM categories c LEFT JOIN products p USING (category_id) GROUP BY c.category_name ORDER BY product_count DESC;

-- 15. Calculate average product price
SELECT ROUND(AVG(unit_price),2) AS average_price FROM products;

-- 16. Find minimum and maximum product price
SELECT MIN(unit_price) AS minimum_price, MAX(unit_price) AS maximum_price FROM products;

-- 17. Total inventory units
SELECT SUM(stock_quantity) AS units_in_stock FROM products;

-- 18. Products with low stock (under 30)
SELECT product_name, stock_quantity FROM products WHERE stock_quantity < 30 ORDER BY stock_quantity;

-- 19. Active products only
SELECT * FROM products WHERE is_active = TRUE;

-- 20. Orders placed in March 2026
SELECT * FROM orders WHERE order_date >= '2026-03-01' AND order_date < '2026-04-01' ORDER BY order_date;

-- 21. List orders newest first
SELECT order_id, customer_id, order_date, status FROM orders ORDER BY order_date DESC;

-- 22. Count orders by status
SELECT status, COUNT(*) AS orders_count FROM orders GROUP BY status ORDER BY orders_count DESC;

-- 23. Find orders that are not cancelled
SELECT * FROM orders WHERE status <> 'cancelled';

-- 24. Find pending orders
SELECT * FROM orders WHERE status = 'pending';

-- 25. Get first five orders
SELECT * FROM orders ORDER BY order_id LIMIT 5;

-- 26. Show each order with customer name
SELECT o.order_id, o.order_date, o.status, c.first_name, c.last_name FROM orders o JOIN customers c USING (customer_id) ORDER BY o.order_id;

-- 27. Show order line subtotals
SELECT order_id, product_id, quantity, unit_price, quantity * unit_price AS line_total FROM order_items ORDER BY order_id;

-- 28. Calculate order totals
SELECT order_id, SUM(quantity * unit_price) AS order_total FROM order_items GROUP BY order_id ORDER BY order_total DESC;

-- 29. Orders with total above 5000
SELECT order_id, SUM(quantity * unit_price) AS order_total FROM order_items GROUP BY order_id HAVING SUM(quantity * unit_price) > 5000 ORDER BY order_total DESC;

-- 30. Top five products by units sold
SELECT p.product_name, SUM(oi.quantity) AS units_sold FROM order_items oi JOIN products p USING (product_id) GROUP BY p.product_name ORDER BY units_sold DESC LIMIT 5;

-- 31. Revenue by product
SELECT p.product_name, SUM(oi.quantity * oi.unit_price) AS gross_sales FROM order_items oi JOIN products p USING (product_id) GROUP BY p.product_name ORDER BY gross_sales DESC;

-- 32. Revenue by category
SELECT c.category_name, SUM(oi.quantity * oi.unit_price) AS gross_sales FROM order_items oi JOIN products p USING (product_id) JOIN categories c USING (category_id) GROUP BY c.category_name ORDER BY gross_sales DESC;

-- 33. Customers with at least one order
SELECT DISTINCT c.customer_id, c.first_name, c.last_name FROM customers c JOIN orders o USING (customer_id) ORDER BY c.customer_id;

-- 34. Customers with no orders
SELECT c.* FROM customers c LEFT JOIN orders o USING (customer_id) WHERE o.order_id IS NULL;

-- 35. Number of orders per customer
SELECT c.customer_id, c.first_name, c.last_name, COUNT(o.order_id) AS order_count FROM customers c LEFT JOIN orders o USING (customer_id) GROUP BY c.customer_id ORDER BY order_count DESC;

-- 36. Customers with more than one order
SELECT c.customer_id, c.first_name, c.last_name, COUNT(o.order_id) AS order_count FROM customers c JOIN orders o USING (customer_id) GROUP BY c.customer_id, c.first_name, c.last_name HAVING COUNT(o.order_id) > 1;

-- 37. Successful payments and methods
SELECT payment_method, COUNT(*) AS successful_payments, SUM(amount) AS total_paid FROM payments WHERE payment_status = 'successful' GROUP BY payment_method ORDER BY total_paid DESC;

-- 38. Failed or pending payments
SELECT * FROM payments WHERE payment_status IN ('failed','pending') ORDER BY payment_date;

-- 39. Payments above 3000
SELECT * FROM payments WHERE amount > 3000 ORDER BY amount DESC;

-- 40. Orders without a successful payment
SELECT o.order_id, o.status FROM orders o LEFT JOIN payments p ON p.order_id = o.order_id AND p.payment_status = 'successful' WHERE p.payment_id IS NULL;

-- 41. Monthly order counts
SELECT DATE_TRUNC('month', order_date)::date AS order_month, COUNT(*) AS order_count FROM orders GROUP BY order_month ORDER BY order_month;

-- 42. Monthly gross sales from order items
SELECT DATE_TRUNC('month', o.order_date)::date AS order_month, SUM(oi.quantity * oi.unit_price) AS gross_sales FROM orders o JOIN order_items oi USING (order_id) GROUP BY order_month ORDER BY order_month;

-- 43. Products above the average price
SELECT product_name, unit_price FROM products WHERE unit_price > (SELECT AVG(unit_price) FROM products) ORDER BY unit_price DESC;

-- 44. Most expensive product in each category
SELECT category_name, product_name, unit_price FROM (SELECT c.category_name, p.product_name, p.unit_price, ROW_NUMBER() OVER (PARTITION BY c.category_id ORDER BY p.unit_price DESC) AS rn FROM products p JOIN categories c USING (category_id)) ranked WHERE rn = 1;

-- 45. Rank products by price
SELECT product_name, unit_price, DENSE_RANK() OVER (ORDER BY unit_price DESC) AS price_rank FROM products;

-- 46. Show each customer's latest order
SELECT DISTINCT ON (customer_id) customer_id, order_id, order_date, status FROM orders ORDER BY customer_id, order_date DESC;

-- 47. Find duplicate email values (normally prevented by UNIQUE)
SELECT lower(email), COUNT(*) FROM customers GROUP BY lower(email) HAVING COUNT(*) > 1;

-- 48. Show category and product names, including empty categories
SELECT c.category_name, p.product_name FROM categories c LEFT JOIN products p USING (category_id) ORDER BY c.category_name, p.product_name;

-- 49. Use COALESCE for missing phone numbers
SELECT first_name, last_name, COALESCE(phone, 'Not provided') AS phone FROM customers;

-- 50. Search for products matching multiple conditions
SELECT * FROM products WHERE unit_price BETWEEN 500 AND 5000 AND stock_quantity >= 30 AND is_active;

-- 51. Insert a temporary customer and return generated fields
INSERT INTO customers (first_name,last_name,email,city,state) VALUES ('Test','Customer','test.customer@example.com','Chennai','Tamil Nadu') RETURNING customer_id, first_name, email;

-- 52. Update a product price and return changed row
UPDATE products SET unit_price = unit_price * 1.05 WHERE sku = 'ELEC-001' RETURNING product_id, product_name, unit_price;

-- 53. Delete a test customer safely (run only if no orders reference it)
DELETE FROM customers WHERE email = 'test.customer@example.com' RETURNING customer_id, email;

-- 54. Use a transaction to demonstrate rollback
BEGIN; UPDATE products SET stock_quantity = stock_quantity + 10 WHERE sku = 'ELEC-001'; SELECT product_name, stock_quantity FROM products WHERE sku = 'ELEC-001'; ROLLBACK;

-- 55. Explain query plan for product category lookup
EXPLAIN ANALYZE SELECT * FROM products WHERE category_id = 1;

-- 56. Inventory movement summary by reason
SELECT reason, SUM(quantity_change) AS net_quantity_change, COUNT(*) AS movement_count FROM inventory_movements GROUP BY reason ORDER BY reason;

-- 57. Find orders with at least two distinct products
SELECT order_id, COUNT(DISTINCT product_id) AS distinct_products FROM order_items GROUP BY order_id HAVING COUNT(DISTINCT product_id) >= 2;

-- 58. Find customers whose total order-item spend exceeds 5000
SELECT c.customer_id, c.first_name, c.last_name, SUM(oi.quantity * oi.unit_price) AS lifetime_item_value FROM customers c JOIN orders o USING (customer_id) JOIN order_items oi USING (order_id) GROUP BY c.customer_id, c.first_name, c.last_name HAVING SUM(oi.quantity * oi.unit_price) > 5000 ORDER BY lifetime_item_value DESC;

-- 59. Calculate average order value from item totals
WITH order_totals AS (SELECT order_id, SUM(quantity * unit_price) AS total FROM order_items GROUP BY order_id) SELECT ROUND(AVG(total),2) AS average_order_value FROM order_totals;

-- 60. Compare successful payment totals by month
SELECT DATE_TRUNC('month', payment_date)::date AS payment_month, SUM(amount) AS successful_amount FROM payments WHERE payment_status = 'successful' GROUP BY payment_month ORDER BY payment_month;
