INSERT INTO warehouse.dim_date (
    date_key,
    full_date,
    day_of_month,
    month,
    month_name,
    quarter,
    year
)
SELECT
    date_key,
    full_date,
    day_of_month,
    month,
    month_name,
    quarter,
    year
FROM staging.dates
ON CONFLICT (date_key) DO UPDATE SET
    full_date = EXCLUDED.full_date,
    day_of_month = EXCLUDED.day_of_month,
    month = EXCLUDED.month,
    month_name = EXCLUDED.month_name,
    quarter = EXCLUDED.quarter,
    year = EXCLUDED.year;

INSERT INTO warehouse.dim_product (
    product_id,
    product_name,
    category,
    brand,
    unit_cost
)
SELECT product_id, product_name, category, brand, unit_cost
FROM staging.products
ON CONFLICT (product_id) DO UPDATE SET
    product_name = EXCLUDED.product_name,
    category = EXCLUDED.category,
    brand = EXCLUDED.brand,
    unit_cost = EXCLUDED.unit_cost,
    is_current = TRUE;

INSERT INTO warehouse.dim_customer (
    customer_id,
    customer_name,
    city,
    segment
)
SELECT customer_id, customer_name, city, segment
FROM staging.customers
ON CONFLICT (customer_id) DO UPDATE SET
    customer_name = EXCLUDED.customer_name,
    city = EXCLUDED.city,
    segment = EXCLUDED.segment,
    is_current = TRUE;

INSERT INTO warehouse.dim_region (region_id, region_name, state, country)
SELECT region_id, region_name, state, country
FROM staging.regions
ON CONFLICT (region_id) DO UPDATE SET
    region_name = EXCLUDED.region_name,
    state = EXCLUDED.state,
    country = EXCLUDED.country;
