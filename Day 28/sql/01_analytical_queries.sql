/*
E-COMMERCE ANALYTICAL QUERY LIBRARY — CORRECTED FOR YOUR GOLD SCHEMA

Database: ecommerce_practice
Schema: day24_gold

Verified column names from your screenshots:
fact_sales:
  order_id, line_id, customer_key, product_key, region_key, date_key,
  quantity, unit_price, discount_pct, gross_amount, discount_amount,
  net_amount, status

Dimensions:
  dim_customer(customer_key, customer_id, customer_name, email, region_key)
  dim_product(product_key, product_id, product_name, category, unit_price)
  dim_region(region_key, region_id, region_name, country)
  dim_date(date_key, full_date, year, quarter, month, month_name, day)

IMPORTANT:
- net_amount is used as sales revenue (after discount).
- gross_amount is before discount.
- discount_amount is the discount value.
- fact_sales is a line-item fact table; aggregate line amounts to order level
  when calculating order-level metrics.
- This script uses only columns visible in the screenshots.
*/

SET search_path TO day24_gold, public;

-- 01. Overall business KPI baseline
SELECT
    SUM(net_amount) AS total_net_revenue,
    SUM(gross_amount) AS total_gross_amount,
    SUM(discount_amount) AS total_discount,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_key) AS unique_customers,
    SUM(quantity) AS units_sold,
    SUM(net_amount) / NULLIF(COUNT(DISTINCT order_id), 0) AS average_order_value
FROM fact_sales;

-- 02. Monthly revenue trend
SELECT
    d.year,
    d.month,
    d.month_name,
    SUM(f.net_amount) AS net_revenue,
    COUNT(DISTINCT f.order_id) AS total_orders
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- 03. Quarterly revenue trend
SELECT
    d.year,
    d.quarter,
    SUM(f.net_amount) AS net_revenue,
    COUNT(DISTINCT f.order_id) AS total_orders
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.year, d.quarter
ORDER BY d.year, d.quarter;

-- 04. Revenue by region
SELECT
    r.region_name,
    r.country,
    SUM(f.net_amount) AS net_revenue,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.customer_key) AS unique_customers
FROM fact_sales f
JOIN dim_region r ON r.region_key = f.region_key
GROUP BY r.region_name, r.country
ORDER BY net_revenue DESC;

-- 05. Revenue by product category
SELECT
    p.category,
    SUM(f.net_amount) AS net_revenue,
    SUM(f.gross_amount) AS gross_amount,
    SUM(f.discount_amount) AS discount_amount,
    SUM(f.quantity) AS units_sold
FROM fact_sales f
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY p.category
ORDER BY net_revenue DESC;

-- 06. Top 10 products by net revenue
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(f.net_amount) AS net_revenue,
    SUM(f.quantity) AS units_sold
FROM fact_sales f
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY p.product_key, p.product_id, p.product_name, p.category
ORDER BY net_revenue DESC
LIMIT 10;

-- 07. Top 10 customers by net revenue
SELECT
    c.customer_id,
    c.customer_name,
    SUM(f.net_amount) AS net_revenue,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.net_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0) AS average_order_value
FROM fact_sales f
JOIN dim_customer c ON c.customer_key = f.customer_key
GROUP BY c.customer_key, c.customer_id, c.customer_name
ORDER BY net_revenue DESC
LIMIT 10;

-- 08. Average order value by region
-- First aggregate line items to order level, then average order values.
WITH order_totals AS (
    SELECT
        region_key,
        order_id,
        SUM(net_amount) AS order_net_amount
    FROM fact_sales
    GROUP BY region_key, order_id
)
SELECT
    r.region_name,
    AVG(o.order_net_amount) AS average_order_value,
    COUNT(*) AS order_count
FROM order_totals o
JOIN dim_region r ON r.region_key = o.region_key
GROUP BY r.region_name
ORDER BY average_order_value DESC;

-- 09. Month-over-month net revenue growth
WITH monthly AS (
    SELECT
        d.year,
        d.month,
        MIN(d.full_date) AS month_date,
        SUM(f.net_amount) AS net_revenue
    FROM fact_sales f
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY d.year, d.month
),
lagged AS (
    SELECT
        *,
        LAG(net_revenue) OVER (ORDER BY month_date) AS previous_month_revenue
    FROM monthly
)
SELECT
    year,
    month,
    net_revenue,
    previous_month_revenue,
    ROUND(
        100.0 * (net_revenue - previous_month_revenue)
        / NULLIF(previous_month_revenue, 0),
        2
    ) AS mom_growth_pct
FROM lagged
ORDER BY month_date;

-- 10. Year-over-year net revenue growth
WITH yearly AS (
    SELECT
        d.year,
        SUM(f.net_amount) AS net_revenue
    FROM fact_sales f
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY d.year
),
lagged AS (
    SELECT
        *,
        LAG(net_revenue) OVER (ORDER BY year) AS previous_year_revenue
    FROM yearly
)
SELECT
    year,
    net_revenue,
    previous_year_revenue,
    ROUND(
        100.0 * (net_revenue - previous_year_revenue)
        / NULLIF(previous_year_revenue, 0),
        2
    ) AS yoy_growth_pct
FROM lagged
ORDER BY year;

-- 11. Cumulative monthly net revenue
WITH monthly AS (
    SELECT
        d.year,
        d.month,
        MIN(d.full_date) AS month_date,
        SUM(f.net_amount) AS net_revenue
    FROM fact_sales f
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY d.year, d.month
)
SELECT
    month_date,
    net_revenue,
    SUM(net_revenue) OVER (
        ORDER BY month_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_net_revenue
FROM monthly
ORDER BY month_date;

-- 12. Customer revenue ranking
WITH customer_revenue AS (
    SELECT
        c.customer_key,
        c.customer_id,
        c.customer_name,
        SUM(f.net_amount) AS net_revenue
    FROM fact_sales f
    JOIN dim_customer c ON c.customer_key = f.customer_key
    GROUP BY c.customer_key, c.customer_id, c.customer_name
)
SELECT
    *,
    DENSE_RANK() OVER (ORDER BY net_revenue DESC) AS revenue_rank
FROM customer_revenue
ORDER BY revenue_rank, customer_name;

-- 13. Revenue contribution percentage by category
WITH category_revenue AS (
    SELECT
        p.category,
        SUM(f.net_amount) AS net_revenue
    FROM fact_sales f
    JOIN dim_product p ON p.product_key = f.product_key
    GROUP BY p.category
)
SELECT
    category,
    net_revenue,
    ROUND(
        100.0 * net_revenue / NULLIF(SUM(net_revenue) OVER (), 0),
        2
    ) AS revenue_share_pct
FROM category_revenue
ORDER BY net_revenue DESC;

-- 14. Customer purchase-frequency segmentation
WITH customer_orders AS (
    SELECT
        customer_key,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(net_amount) AS lifetime_net_revenue
    FROM fact_sales
    GROUP BY customer_key
),
segmented AS (
    SELECT
        CASE
            WHEN order_count = 1 THEN 'One-time'
            WHEN order_count BETWEEN 2 AND 4 THEN 'Repeat'
            ELSE 'Frequent'
        END AS customer_segment,
        order_count,
        lifetime_net_revenue
    FROM customer_orders
)
SELECT
    customer_segment,
    COUNT(*) AS customers,
    SUM(lifetime_net_revenue) AS segment_net_revenue,
    ROUND(AVG(order_count), 2) AS average_orders_per_customer
FROM segmented
GROUP BY customer_segment
ORDER BY segment_net_revenue DESC;

-- 15. Order status distribution
SELECT
    status,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(net_amount) AS net_revenue,
    SUM(quantity) AS units_sold
FROM fact_sales
GROUP BY status
ORDER BY total_orders DESC;

-- 16. Discount analysis by product category
SELECT
    p.category,
    SUM(f.gross_amount) AS gross_amount,
    SUM(f.discount_amount) AS total_discount,
    SUM(f.net_amount) AS net_revenue,
    ROUND(
        100.0 * SUM(f.discount_amount)
        / NULLIF(SUM(f.gross_amount), 0),
        2
    ) AS effective_discount_pct
FROM fact_sales f
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY p.category
ORDER BY total_discount DESC;

-- 17. Net revenue per customer by region
SELECT
    r.region_name,
    COUNT(DISTINCT f.customer_key) AS unique_customers,
    SUM(f.net_amount) AS net_revenue,
    SUM(f.net_amount)
        / NULLIF(COUNT(DISTINCT f.customer_key), 0) AS revenue_per_customer
FROM fact_sales f
JOIN dim_region r ON r.region_key = f.region_key
GROUP BY r.region_name
ORDER BY revenue_per_customer DESC;

-- 18. Pareto analysis: cumulative customer revenue contribution
WITH customer_revenue AS (
    SELECT
        customer_key,
        SUM(net_amount) AS net_revenue
    FROM fact_sales
    GROUP BY customer_key
),
ranked AS (
    SELECT
        customer_key,
        net_revenue,
        SUM(net_revenue) OVER (
            ORDER BY net_revenue DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_revenue,
        SUM(net_revenue) OVER () AS total_revenue
    FROM customer_revenue
)
SELECT
    customer_key,
    net_revenue,
    ROUND(
        100.0 * cumulative_revenue / NULLIF(total_revenue, 0),
        2
    ) AS cumulative_revenue_pct
FROM ranked
ORDER BY net_revenue DESC;

-- 19. Product performance ranking within each region
WITH regional_product_sales AS (
    SELECT
        r.region_name,
        p.product_id,
        p.product_name,
        p.category,
        SUM(f.net_amount) AS net_revenue,
        SUM(f.quantity) AS units_sold
    FROM fact_sales f
    JOIN dim_region r ON r.region_key = f.region_key
    JOIN dim_product p ON p.product_key = f.product_key
    GROUP BY
        r.region_name,
        p.product_key,
        p.product_id,
        p.product_name,
        p.category
)
SELECT
    *,
    DENSE_RANK() OVER (
        PARTITION BY region_name
        ORDER BY net_revenue DESC
    ) AS product_rank_in_region
FROM regional_product_sales
ORDER BY region_name, product_rank_in_region;

-- 20. Data quality checks on key analytical fields
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE order_id IS NULL) AS null_order_ids,
    COUNT(*) FILTER (WHERE line_id IS NULL) AS null_line_ids,
    COUNT(*) FILTER (WHERE date_key IS NULL) AS null_date_keys,
    COUNT(*) FILTER (WHERE net_amount IS NULL) AS null_net_amount,
    COUNT(*) FILTER (WHERE gross_amount IS NULL) AS null_gross_amount,
    COUNT(*) FILTER (WHERE quantity IS NULL) AS null_quantity,
    COUNT(*) FILTER (WHERE status IS NULL) AS null_status
FROM fact_sales;
