-- Day 9 Advanced SQL: 45 queries
-- Prerequisite: Day 8 ecommerce_practice schema and sample data.

-- 01. INNER JOIN: orders and customers
SELECT o.order_id, o.order_date, o.status, c.first_name, c.last_name FROM orders o INNER JOIN customers c ON c.customer_id = o.customer_id ORDER BY o.order_id;

-- 02. LEFT JOIN: all customers, including those with no orders
SELECT c.customer_id, c.first_name, c.last_name, o.order_id FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id ORDER BY c.customer_id, o.order_id;

-- 03. RIGHT JOIN: keep all customers via reversed table order
SELECT o.order_id, c.customer_id, c.first_name FROM orders o RIGHT JOIN customers c ON c.customer_id = o.customer_id ORDER BY c.customer_id;

-- 04. FULL OUTER JOIN demonstration
WITH a AS (SELECT customer_id, COUNT(*) AS order_count FROM orders GROUP BY customer_id), b AS (SELECT o.customer_id, SUM(p.amount) AS paid FROM orders o JOIN payments p USING(order_id) WHERE p.payment_status='successful' GROUP BY o.customer_id) SELECT COALESCE(a.customer_id,b.customer_id) customer_id,a.order_count,b.paid FROM a FULL OUTER JOIN b USING(customer_id);

-- 05. CROSS JOIN: category and status combinations
SELECT c.category_name,s.status FROM categories c CROSS JOIN (VALUES ('pending'),('paid'),('shipped'),('delivered')) s(status) ORDER BY 1,2;

-- 06. Self join: customers in same city
SELECT a.first_name customer_a,b.first_name customer_b,a.city FROM customers a JOIN customers b ON a.city=b.city AND a.customer_id<b.customer_id ORDER BY a.city;

-- 07. Three-table join: items, products, categories
SELECT oi.order_id,p.product_name,c.category_name,oi.quantity,oi.unit_price,oi.quantity*oi.unit_price line_total FROM order_items oi JOIN products p USING(product_id) JOIN categories c USING(category_id) ORDER BY oi.order_id;

-- 08. Multi-table order details
SELECT o.order_id,o.order_date,c.first_name,p.product_name,oi.quantity,oi.unit_price FROM orders o JOIN customers c USING(customer_id) JOIN order_items oi USING(order_id) JOIN products p USING(product_id) ORDER BY o.order_id;

-- 09. Order count per customer
SELECT c.customer_id,c.first_name,COUNT(o.order_id) order_count FROM customers c LEFT JOIN orders o USING(customer_id) GROUP BY c.customer_id,c.first_name ORDER BY order_count DESC;

-- 10. Categories with average price above 1000
SELECT c.category_name,ROUND(AVG(p.unit_price),2) avg_price FROM categories c JOIN products p USING(category_id) GROUP BY c.category_name HAVING AVG(p.unit_price)>1000;

-- 11. Distinct buyers per product
SELECT p.product_name,COUNT(DISTINCT o.customer_id) distinct_buyers FROM products p LEFT JOIN order_items oi USING(product_id) LEFT JOIN orders o USING(order_id) GROUP BY p.product_id,p.product_name ORDER BY distinct_buyers DESC;

-- 12. Multiple aggregates per category
SELECT c.category_name,COUNT(p.product_id) product_count,MIN(p.unit_price) min_price,MAX(p.unit_price) max_price,ROUND(AVG(p.unit_price),2) avg_price,SUM(p.stock_quantity) stock_units FROM categories c LEFT JOIN products p USING(category_id) GROUP BY c.category_name;

-- 13. ROLLUP subtotals and grand total
SELECT CASE WHEN GROUPING(c.category_name)=1 THEN 'GRAND TOTAL' ELSE c.category_name END category,SUM(p.unit_price) sum_list_prices FROM categories c JOIN products p USING(category_id) GROUP BY ROLLUP(c.category_name);

-- 14. CUBE category and active status
SELECT CASE WHEN GROUPING(c.category_name)=1 THEN 'ALL CATEGORIES' ELSE c.category_name END category,CASE WHEN GROUPING(p.is_active)=1 THEN 'ALL STATUS' WHEN p.is_active THEN 'active' ELSE 'inactive' END product_status,COUNT(*) product_count FROM products p JOIN categories c USING(category_id) GROUP BY CUBE(c.category_name,p.is_active);

-- 15. ROW_NUMBER: order sequence per customer
SELECT customer_id,order_id,order_date,ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY order_date) customer_order_number FROM orders;

-- 16. RANK vs DENSE_RANK for product prices
SELECT product_name,unit_price,RANK() OVER(ORDER BY unit_price DESC) price_rank,DENSE_RANK() OVER(ORDER BY unit_price DESC) dense_price_rank FROM products ORDER BY unit_price DESC;

-- 17. Rank products within category
SELECT c.category_name,p.product_name,p.unit_price,DENSE_RANK() OVER(PARTITION BY c.category_id ORDER BY p.unit_price DESC) category_rank FROM products p JOIN categories c USING(category_id);

-- 18. Running total of monthly sales
WITH monthly AS (SELECT DATE_TRUNC('month',o.order_date)::date AS month,SUM(oi.quantity*oi.unit_price) sales FROM orders o JOIN order_items oi USING(order_id) WHERE o.status<>'cancelled' GROUP BY 1) SELECT month,sales,SUM(sales) OVER(ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) running_sales FROM monthly;

-- 19. LAG: month-over-month sales
WITH m AS (SELECT DATE_TRUNC('month',o.order_date)::date AS month,SUM(oi.quantity*oi.unit_price) sales FROM orders o JOIN order_items oi USING(order_id) GROUP BY 1) SELECT month,sales,LAG(sales) OVER(ORDER BY month) previous_sales,sales-LAG(sales) OVER(ORDER BY month) sales_change FROM m;

-- 20. LEAD: next order date
SELECT customer_id,order_id,order_date,LEAD(order_date) OVER(PARTITION BY customer_id ORDER BY order_date) next_order_date FROM orders;

-- 21. Three-month moving average
WITH m AS (SELECT DATE_TRUNC('month',o.order_date)::date AS month,SUM(oi.quantity*oi.unit_price) sales FROM orders o JOIN order_items oi USING(order_id) GROUP BY 1) SELECT month,sales,ROUND(AVG(sales) OVER(ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),2) moving_avg FROM m;

-- 22. Subquery in WHERE: above-average priced products
SELECT product_name,unit_price FROM products WHERE unit_price>(SELECT AVG(unit_price) FROM products);

-- 23. Subquery in SELECT: category average
SELECT p.product_name,p.unit_price,(SELECT ROUND(AVG(p2.unit_price),2) FROM products p2 WHERE p2.category_id=p.category_id) category_average FROM products p;

-- 24. Subquery in FROM: high-value orders
SELECT order_id,total FROM (SELECT order_id,SUM(quantity*unit_price) total FROM order_items GROUP BY order_id) t WHERE total>3000 ORDER BY total DESC;

-- 25. Correlated subquery: customers with an order over 5000
SELECT c.customer_id,c.first_name FROM customers c WHERE EXISTS(SELECT 1 FROM orders o JOIN order_items oi USING(order_id) WHERE o.customer_id=c.customer_id GROUP BY o.order_id HAVING SUM(oi.quantity*oi.unit_price)>5000);

-- 26. NOT EXISTS: products never ordered
SELECT p.product_id,p.product_name FROM products p WHERE NOT EXISTS(SELECT 1 FROM order_items oi WHERE oi.product_id=p.product_id);

-- 27. CTE: customer lifetime item value
WITH cv AS (SELECT o.customer_id,SUM(oi.quantity*oi.unit_price) value FROM orders o JOIN order_items oi USING(order_id) GROUP BY o.customer_id) SELECT c.customer_id,c.first_name,COALESCE(cv.value,0) lifetime_value FROM customers c LEFT JOIN cv USING(customer_id) ORDER BY lifetime_value DESC;

-- 28. Multiple CTEs: order totals vs successful payments
WITH item_totals AS (SELECT order_id,SUM(quantity*unit_price) total FROM order_items GROUP BY order_id), paid AS (SELECT order_id,SUM(amount) amount FROM payments WHERE payment_status='successful' GROUP BY order_id) SELECT o.order_id,it.total,COALESCE(p.amount,0) successful_paid FROM orders o LEFT JOIN item_totals it USING(order_id) LEFT JOIN paid p USING(order_id);

-- 29. Recursive CTE: monthly calendar
WITH RECURSIVE months(m) AS (SELECT DATE '2026-01-01' UNION ALL SELECT (m+INTERVAL '1 month')::date FROM months WHERE m<DATE '2026-12-01') SELECT m FROM months;

-- 30. Recursive CTE: integers 1 to 10
WITH RECURSIVE nums(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM nums WHERE n<10) SELECT n FROM nums;

-- 31. Daily order totals
SELECT o.order_date::date as day,COUNT(DISTINCT o.order_id) orders_count,SUM(oi.quantity*oi.unit_price) gross_sales FROM orders o JOIN order_items oi USING(order_id) GROUP BY o.order_date::date ORDER BY day;

-- 32. Sales by state and month
SELECT o.shipping_state,DATE_TRUNC('month',o.order_date)::date AS month,SUM(oi.quantity*oi.unit_price) sales FROM orders o JOIN order_items oi USING(order_id) GROUP BY 1,2 ORDER BY 1,2;

-- 33. Top two products per category by units sold
WITH u AS (SELECT p.product_id,p.product_name,p.category_id,COALESCE(SUM(oi.quantity),0) units FROM products p LEFT JOIN order_items oi USING(product_id) GROUP BY p.product_id),r AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY category_id ORDER BY units DESC,product_id) rn FROM u) SELECT c.category_name,r.product_name,r.units FROM r JOIN categories c USING(category_id) WHERE rn<=2;

-- 34. Product percentage of gross sales
WITH ps AS (SELECT p.product_id,p.product_name,SUM(oi.quantity*oi.unit_price) sales FROM products p JOIN order_items oi USING(product_id) GROUP BY p.product_id), t AS (SELECT SUM(sales) all_sales FROM ps) SELECT ps.product_name,ps.sales,ROUND(100.0*ps.sales/NULLIF(t.all_sales,0),2) pct_sales FROM ps CROSS JOIN t ORDER BY ps.sales DESC;

-- 35. EXPLAIN ANALYZE for customer order lookup
EXPLAIN (ANALYZE,BUFFERS) SELECT order_id,order_date,status FROM orders WHERE customer_id=1 ORDER BY order_date DESC;

-- 36. Latest order per customer if not delivered
WITH r AS (SELECT o.*,ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY order_date DESC) rn FROM orders o) SELECT c.first_name,c.last_name,r.order_id,r.status FROM r JOIN customers c USING(customer_id) WHERE rn=1 AND status<>'delivered';

-- 37. Conditional aggregation with FILTER
SELECT c.customer_id,c.first_name,COUNT(o.order_id) total_orders,COUNT(*) FILTER(WHERE o.status='delivered') delivered,COUNT(*) FILTER(WHERE o.status='cancelled') cancelled FROM customers c LEFT JOIN orders o USING(customer_id) GROUP BY c.customer_id,c.first_name;

-- 38. Historical order price vs current product price
SELECT oi.order_id,p.product_name,oi.unit_price historical_price,p.unit_price current_price FROM order_items oi JOIN products p USING(product_id) WHERE oi.unit_price<p.unit_price;

-- 39. Compare order to customer's average order value
WITH t AS (SELECT o.order_id,o.customer_id,o.order_date,SUM(oi.quantity*oi.unit_price) total FROM orders o JOIN order_items oi USING(order_id) GROUP BY o.order_id) SELECT *,ROUND(AVG(total) OVER(PARTITION BY customer_id),2) customer_avg,total-AVG(total) OVER(PARTITION BY customer_id) delta FROM t;

-- 40. Calendar left join to show zero-sales months
WITH RECURSIVE m(month_start) AS (SELECT DATE '2026-01-01' UNION ALL SELECT (month_start+INTERVAL '1 month')::date FROM m WHERE month_start<DATE '2026-12-01'),s AS (SELECT DATE_TRUNC('month',o.order_date)::date month_start,SUM(oi.quantity*oi.unit_price) sales FROM orders o JOIN order_items oi USING(order_id) GROUP BY 1) SELECT m.month_start,COALESCE(s.sales,0) sales FROM m LEFT JOIN s USING(month_start) ORDER BY m.month_start;

-- 41. Payment outcomes by method using FILTER
SELECT payment_method,COUNT(*) FILTER(WHERE payment_status='successful') successful,COUNT(*) FILTER(WHERE payment_status='failed') failed,COUNT(*) FILTER(WHERE payment_status='pending') pending FROM payments GROUP BY payment_method;

-- 42. Detect payment/order total mismatches
WITH ot AS (SELECT order_id,SUM(quantity*unit_price) total FROM order_items GROUP BY order_id),p AS (SELECT order_id,SUM(amount) FILTER(WHERE payment_status='successful') paid FROM payments GROUP BY order_id) SELECT o.order_id,ot.total,COALESCE(p.paid,0) paid FROM orders o LEFT JOIN ot USING(order_id) LEFT JOIN p USING(order_id) WHERE ABS(COALESCE(ot.total,0)-COALESCE(p.paid,0))>0.01;

-- 43. DISTINCT ON: latest order per customer
SELECT DISTINCT ON(customer_id) customer_id,order_id,order_date,status FROM orders ORDER BY customer_id,order_date DESC;

-- 44. Segment customers by order count
WITH x AS (SELECT c.customer_id,c.first_name,COUNT(o.order_id) n FROM customers c LEFT JOIN orders o USING(customer_id) GROUP BY c.customer_id,c.first_name) SELECT *,CASE WHEN n>=3 THEN 'frequent' WHEN n=2 THEN 'repeat' WHEN n=1 THEN 'one order' ELSE 'no orders' END segment FROM x;

-- 45. EXPLAIN ANALYZE for order-item product filter
EXPLAIN (ANALYZE,BUFFERS) SELECT * FROM order_items WHERE product_id=1; -- A small table may favor a sequential scan.
