-- 1. Monthly net revenue and units sold.
SELECT d.year_number, d.month_number, d.month_name, SUM(f.net_amount) net_revenue,
       SUM(f.quantity) units_sold
FROM fact_sales f JOIN dim_date d ON d.date_sk=f.date_sk
GROUP BY d.year_number,d.month_number,d.month_name ORDER BY d.year_number,d.month_number;

-- 2. Revenue by product category.
SELECT p.category,SUM(f.net_amount) net_revenue,SUM(f.quantity) units_sold
FROM fact_sales f JOIN dim_product p ON p.product_sk=f.product_sk
GROUP BY p.category ORDER BY net_revenue DESC;

-- 3. Revenue by historical customer segment attached to each fact.
SELECT c.segment,SUM(f.net_amount) net_revenue,COUNT(DISTINCT f.order_id) orders
FROM fact_sales f JOIN dim_customer c ON c.customer_sk=f.customer_sk
GROUP BY c.segment ORDER BY net_revenue DESC;

-- 4. Revenue by channel.
SELECT ch.channel_name,SUM(f.net_amount) net_revenue,COUNT(*) order_lines
FROM fact_sales f JOIN dim_channel ch ON ch.channel_sk=f.channel_sk
GROUP BY ch.channel_name ORDER BY net_revenue DESC;

-- 5. Top five customers by revenue; aggregate all historical customer versions together.
SELECT c.customer_id,MAX(c.full_name) full_name,SUM(f.net_amount) net_revenue
FROM fact_sales f JOIN dim_customer c ON c.customer_sk=f.customer_sk
GROUP BY c.customer_id ORDER BY net_revenue DESC LIMIT 5;

-- 6. Running year-to-date revenue using a window function.
WITH monthly AS (
 SELECT d.year_number,d.month_number,SUM(f.net_amount) net_revenue
 FROM fact_sales f JOIN dim_date d ON d.date_sk=f.date_sk
 GROUP BY d.year_number,d.month_number
)
SELECT year_number,month_number,net_revenue,
       SUM(net_revenue) OVER(PARTITION BY year_number ORDER BY month_number
                             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) ytd_revenue
FROM monthly ORDER BY year_number,month_number;

-- 7. Full history for each customer.
SELECT customer_id,version_number,city,state,segment,valid_from,valid_to,is_current
FROM dim_customer ORDER BY customer_id,version_number;

-- 8. Customer attributes as of a timestamp (edit customer ID and timestamp as needed).
SELECT customer_id,full_name,city,state,segment FROM dim_customer
WHERE customer_id='C001' AND TIMESTAMP '2026-02-01 00:00:00' >= valid_from
  AND TIMESTAMP '2026-02-01 00:00:00' < valid_to;

-- 9. Average order value: calculate order totals first, then average the orders.
WITH order_totals AS (SELECT order_id,SUM(net_amount) order_net FROM fact_sales GROUP BY order_id)
SELECT ROUND(AVG(order_net),2) average_order_value FROM order_totals;
