-- INNER JOIN: only matching rows
SELECT c.customer_id,c.first_name,o.order_id FROM customers c INNER JOIN orders o USING(customer_id);
-- LEFT JOIN: keep every customer
SELECT c.customer_id,c.first_name,o.order_id FROM customers c LEFT JOIN orders o USING(customer_id);
-- RIGHT JOIN: keep every row on the right
SELECT o.order_id,c.customer_id,c.first_name FROM orders o RIGHT JOIN customers c USING(customer_id);
-- FULL OUTER JOIN: preserve unmatched rows on both sides
SELECT c.customer_id,c.first_name,o.order_id FROM customers c FULL OUTER JOIN orders o USING(customer_id);
-- CROSS JOIN: Cartesian product
SELECT c.category_name,s.status FROM categories c CROSS JOIN (VALUES ('pending'),('delivered')) s(status);
-- SELF JOIN: pairs of customers living in the same city
SELECT a.first_name,b.first_name,a.city FROM customers a JOIN customers b ON a.city=b.city AND a.customer_id<b.customer_id;
