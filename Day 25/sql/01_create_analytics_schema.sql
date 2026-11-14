CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.dim_region (
    region_key BIGINT PRIMARY KEY,
    region_id BIGINT UNIQUE NOT NULL,
    region_name TEXT NOT NULL,
    country TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_customer (
    customer_key BIGINT PRIMARY KEY,
    customer_id BIGINT UNIQUE NOT NULL,
    customer_name TEXT NOT NULL,
    email TEXT,
    region_key BIGINT REFERENCES analytics.dim_region(region_key)
);

CREATE TABLE IF NOT EXISTS analytics.dim_product (
    product_key BIGINT PRIMARY KEY,
    product_id BIGINT UNIQUE NOT NULL,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_price NUMERIC(14,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day INTEGER NOT NULL
);

-- Grain: one row per order_id + line_id.
CREATE TABLE IF NOT EXISTS analytics.fact_sales (
    order_id BIGINT NOT NULL,
    line_id INTEGER NOT NULL,
    customer_key BIGINT NOT NULL REFERENCES analytics.dim_customer(customer_key),
    product_key BIGINT NOT NULL REFERENCES analytics.dim_product(product_key),
    region_key BIGINT NOT NULL REFERENCES analytics.dim_region(region_key),
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(14,2) NOT NULL CHECK (unit_price >= 0),
    discount_pct NUMERIC(5,4) NOT NULL CHECK (discount_pct BETWEEN 0 AND 1),
    gross_amount NUMERIC(16,2) NOT NULL,
    discount_amount NUMERIC(16,2) NOT NULL,
    net_amount NUMERIC(16,2) NOT NULL,
    status TEXT NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    PRIMARY KEY (order_id, line_id)
);

CREATE TABLE IF NOT EXISTS analytics.pipeline_audit (
    audit_id BIGSERIAL PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    status TEXT NOT NULL,
    records_processed BIGINT NOT NULL DEFAULT 0,
    message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics.data_quality_results (
    result_id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL,
    dataset_name TEXT NOT NULL,
    rule_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    failed_records BIGINT NOT NULL DEFAULT 0,
    checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fact_sales_date ON analytics.fact_sales(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_customer ON analytics.fact_sales(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product ON analytics.fact_sales(product_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_region ON analytics.fact_sales(region_key);
