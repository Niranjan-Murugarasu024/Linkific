WITH totals AS (
 SELECT o.order_id,o.customer_id,o.order_date,SUM(oi.quantity*oi.unit_price) order_total
 FROM orders o JOIN order_items oi USING(order_id) GROUP BY o.order_id
)
SELECT *,
 ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY order_date) sequence_number,
 RANK() OVER(ORDER BY order_total DESC) overall_rank,
 DENSE_RANK() OVER(ORDER BY order_total DESC) dense_rank,
 SUM(order_total) OVER(PARTITION BY customer_id ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) running_total,
 LAG(order_total) OVER(PARTITION BY customer_id ORDER BY order_date) previous_order,
 LEAD(order_total) OVER(PARTITION BY customer_id ORDER BY order_date) next_order,
 AVG(order_total) OVER(PARTITION BY customer_id ORDER BY order_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) rolling_average
FROM totals ORDER BY customer_id,order_date;
