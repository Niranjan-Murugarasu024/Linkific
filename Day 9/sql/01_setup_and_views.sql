CREATE OR REPLACE VIEW v_order_totals AS
SELECT o.order_id,o.customer_id,o.order_date,o.status,
       COALESCE(SUM(oi.quantity*oi.unit_price),0)::numeric(12,2) order_total
FROM orders o LEFT JOIN order_items oi USING(order_id)
GROUP BY o.order_id,o.customer_id,o.order_date,o.status;

CREATE OR REPLACE VIEW v_monthly_sales AS
SELECT DATE_TRUNC('month',o.order_date)::date sales_month,
       SUM(oi.quantity*oi.unit_price)::numeric(14,2) gross_sales,
       COUNT(DISTINCT o.order_id) order_count
FROM orders o JOIN order_items oi USING(order_id)
WHERE o.status<>'cancelled'
GROUP BY 1;
