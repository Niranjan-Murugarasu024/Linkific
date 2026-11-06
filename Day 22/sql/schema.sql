-- E-commerce analytics warehouse schema
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS warehouse;

CREATE TABLE IF NOT EXISTS warehouse.dim_date (
 date_key INTEGER PRIMARY KEY,
 full_date DATE NOT NULL UNIQUE,
 day_of_month INTEGER NOT NULL,
 month INTEGER NOT NULL,
 month_name VARCHAR(15) NOT NULL,
 quarter INTEGER NOT NULL,
 year INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse.dim_product (
 product_key BIGSERIAL PRIMARY KEY,
 product_id VARCHAR(100) NOT NULL UNIQUE,
 product_name VARCHAR(255) NOT NULL,
 category VARCHAR(100),
 brand VARCHAR(100),
 unit_cost NUMERIC(12,2),
 is_current BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS warehouse.dim_customer (
 customer_key BIGSERIAL PRIMARY KEY,
 customer_id VARCHAR(100) NOT NULL UNIQUE,
 customer_name VARCHAR(255),
 city VARCHAR(100),
 segment VARCHAR(100),
 is_current BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS warehouse.dim_region (
 region_key BIGSERIAL PRIMARY KEY,
 region_id VARCHAR(100) NOT NULL UNIQUE,
 region_name VARCHAR(150) NOT NULL,
 state VARCHAR(100),
 country VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS warehouse.fact_sales (
 sales_key BIGSERIAL PRIMARY KEY,
 source_sales_id VARCHAR(150) NOT NULL UNIQUE,
 date_key INTEGER NOT NULL REFERENCES warehouse.dim_date(date_key),
 product_key BIGINT NOT NULL REFERENCES warehouse.dim_product(product_key),
 customer_key BIGINT NOT NULL REFERENCES warehouse.dim_customer(customer_key),
 region_key BIGINT NOT NULL REFERENCES warehouse.dim_region(region_key),
 quantity INTEGER NOT NULL CHECK (quantity > 0),
 unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
 discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0
     CHECK (discount_amount >= 0 AND discount_amount <= quantity * unit_price),
 sales_amount NUMERIC(14,2) NOT NULL
     CHECK (sales_amount = quantity * unit_price - discount_amount),
 loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS warehouse.fact_inventory (
 inventory_key BIGSERIAL PRIMARY KEY,
 snapshot_id VARCHAR(200) NOT NULL UNIQUE,
 date_key INTEGER NOT NULL REFERENCES warehouse.dim_date(date_key),
 product_key BIGINT NOT NULL REFERENCES warehouse.dim_product(product_key),
 region_key BIGINT NOT NULL REFERENCES warehouse.dim_region(region_key),
 available_quantity INTEGER NOT NULL CHECK (available_quantity >= 0),
 reorder_level INTEGER NOT NULL CHECK (reorder_level >= 0),
 stock_value NUMERIC(14,2) NOT NULL CHECK (stock_value >= 0),
 loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sales_date ON warehouse.fact_sales(date_key);
CREATE INDEX IF NOT EXISTS idx_sales_product ON warehouse.fact_sales(product_key);
CREATE INDEX IF NOT EXISTS idx_sales_customer ON warehouse.fact_sales(customer_key);
CREATE INDEX IF NOT EXISTS idx_sales_region ON warehouse.fact_sales(region_key);
