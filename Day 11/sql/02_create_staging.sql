-- Raw-ish landing tables: stage first, validate, then load dimensions and facts.
CREATE TABLE IF NOT EXISTS stg_customer (
 customer_id VARCHAR(30) NOT NULL, full_name VARCHAR(120) NOT NULL,
 email VARCHAR(200), city VARCHAR(80), state VARCHAR(80), segment VARCHAR(40) NOT NULL,
 updated_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS stg_customer_changes (
 customer_id VARCHAR(30) NOT NULL, full_name VARCHAR(120) NOT NULL,
 email VARCHAR(200), city VARCHAR(80), state VARCHAR(80), segment VARCHAR(40) NOT NULL,
 updated_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS stg_product (
 product_id VARCHAR(30) NOT NULL, product_name VARCHAR(120) NOT NULL,
 category VARCHAR(80) NOT NULL, brand VARCHAR(80), unit_price NUMERIC(12,2) NOT NULL,
 updated_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS stg_sales (
 order_id VARCHAR(40) NOT NULL, order_line_id INTEGER NOT NULL, order_date DATE NOT NULL,
 customer_id VARCHAR(30) NOT NULL, product_id VARCHAR(30) NOT NULL,
 channel VARCHAR(30) NOT NULL, quantity INTEGER NOT NULL,
 unit_price NUMERIC(12,2) NOT NULL, discount_amount NUMERIC(14,2) NOT NULL DEFAULT 0
);
-- To reload CSVs, first TRUNCATE the specific staging tables to avoid duplicate rows.
