-- Run only after importing the initial customer, product and sales CSVs.
-- Initial customer snapshot: create version 1 per business key.
INSERT INTO dim_customer(customer_id, full_name, email, city, state, segment,
                         valid_from, valid_to, is_current, version_number, source_updated_at)
SELECT DISTINCT ON (customer_id) customer_id, full_name, email, city, state, segment,
       updated_at, TIMESTAMP '9999-12-31 00:00:00', TRUE, 1, updated_at
FROM stg_customer ORDER BY customer_id, updated_at DESC
ON CONFLICT (customer_id, version_number) DO NOTHING;

-- Type 1 product dimension: overwrite descriptive attributes for newer source records.
INSERT INTO dim_product(product_id, product_name, category, brand, current_unit_price, source_updated_at)
SELECT DISTINCT ON (product_id) product_id, product_name, category, brand, unit_price, updated_at
FROM stg_product ORDER BY product_id, updated_at DESC
ON CONFLICT (product_id) DO UPDATE SET
 product_name=EXCLUDED.product_name, category=EXCLUDED.category, brand=EXCLUDED.brand,
 current_unit_price=EXCLUDED.current_unit_price, source_updated_at=EXCLUDED.source_updated_at
WHERE dim_product.source_updated_at IS NULL OR EXCLUDED.source_updated_at >= dim_product.source_updated_at;

INSERT INTO dim_channel(channel_name)
SELECT DISTINCT TRIM(channel) FROM stg_sales WHERE TRIM(channel) <> ''
ON CONFLICT (channel_name) DO NOTHING;

INSERT INTO dim_date(date_sk, full_date, day_of_month, day_of_week, day_name, week_of_year,
                     month_number, month_name, quarter_number, year_number, is_weekend)
SELECT DISTINCT TO_CHAR(order_date,'YYYYMMDD')::INTEGER, order_date,
       EXTRACT(DAY FROM order_date)::SMALLINT, EXTRACT(ISODOW FROM order_date)::SMALLINT,
       TO_CHAR(order_date,'FMDay'), EXTRACT(WEEK FROM order_date)::SMALLINT,
       EXTRACT(MONTH FROM order_date)::SMALLINT, TO_CHAR(order_date,'FMMonth'),
       EXTRACT(QUARTER FROM order_date)::SMALLINT, EXTRACT(YEAR FROM order_date)::INTEGER,
       EXTRACT(ISODOW FROM order_date) IN (6,7)
FROM stg_sales ON CONFLICT(date_sk) DO NOTHING;

-- Fact grain: one row per (order_id, order_line_id). Resolve the customer version valid at event time.
INSERT INTO fact_sales(order_id, order_line_id, date_sk, customer_sk, product_sk, channel_sk,
                       quantity, unit_price, gross_amount, discount_amount, net_amount)
SELECT s.order_id, s.order_line_id, TO_CHAR(s.order_date,'YYYYMMDD')::INTEGER,
       c.customer_sk, p.product_sk, ch.channel_sk, s.quantity, s.unit_price,
       ROUND(s.quantity*s.unit_price,2), s.discount_amount,
       ROUND(s.quantity*s.unit_price-s.discount_amount,2)
FROM stg_sales s
JOIN dim_customer c ON c.customer_id=s.customer_id
 AND s.order_date::TIMESTAMP >= c.valid_from AND s.order_date::TIMESTAMP < c.valid_to
JOIN dim_product p ON p.product_id=s.product_id
JOIN dim_channel ch ON ch.channel_name=TRIM(s.channel)
WHERE s.quantity > 0 AND s.unit_price >= 0 AND s.discount_amount >= 0
  AND s.discount_amount <= s.quantity*s.unit_price
ON CONFLICT(order_id, order_line_id) DO NOTHING;
