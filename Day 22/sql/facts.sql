INSERT INTO warehouse.fact_sales (
    source_sales_id,
    date_key,
    product_key,
    customer_key,
    region_key,
    quantity,
    unit_price,
    discount_amount,
    sales_amount
)
SELECT
    source.source_sales_id,
    source.date_key,
    product.product_key,
    customer.customer_key,
    region.region_key,
    source.quantity,
    source.unit_price,
    source.discount_amount,
    source.sales_amount
FROM staging.sales AS source
JOIN warehouse.dim_product AS product
    ON product.product_id = source.product_id
JOIN warehouse.dim_customer AS customer
    ON customer.customer_id = source.customer_id
JOIN warehouse.dim_region AS region
    ON region.region_id = source.region_id
ON CONFLICT (source_sales_id) DO UPDATE SET
    date_key = EXCLUDED.date_key,
    product_key = EXCLUDED.product_key,
    customer_key = EXCLUDED.customer_key,
    region_key = EXCLUDED.region_key,
    quantity = EXCLUDED.quantity,
    unit_price = EXCLUDED.unit_price,
    discount_amount = EXCLUDED.discount_amount,
    sales_amount = EXCLUDED.sales_amount;

INSERT INTO warehouse.fact_inventory (
    snapshot_id,
    date_key,
    product_key,
    region_key,
    available_quantity,
    reorder_level,
    stock_value
)
SELECT
    source.snapshot_id,
    source.date_key,
    product.product_key,
    region.region_key,
    source.available_quantity,
    source.reorder_level,
    source.stock_value
FROM staging.inventory AS source
JOIN warehouse.dim_product AS product
    ON product.product_id = source.product_id
JOIN warehouse.dim_region AS region
    ON region.region_id = source.region_id
ON CONFLICT (snapshot_id) DO UPDATE SET
    date_key = EXCLUDED.date_key,
    product_key = EXCLUDED.product_key,
    region_key = EXCLUDED.region_key,
    available_quantity = EXCLUDED.available_quantity,
    reorder_level = EXCLUDED.reorder_level,
    stock_value = EXCLUDED.stock_value;
