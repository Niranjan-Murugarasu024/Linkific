-- CAUTION: DROP statements reset tables in this lab database.
DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_channel CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;

CREATE TABLE dim_date (
  date_sk INTEGER PRIMARY KEY, -- YYYYMMDD
  full_date DATE NOT NULL UNIQUE,
  day_of_month SMALLINT NOT NULL,
  day_of_week SMALLINT NOT NULL, -- ISO Monday=1 ... Sunday=7
  day_name VARCHAR(9) NOT NULL,
  week_of_year SMALLINT NOT NULL,
  month_number SMALLINT NOT NULL,
  month_name VARCHAR(9) NOT NULL,
  quarter_number SMALLINT NOT NULL,
  year_number INTEGER NOT NULL,
  is_weekend BOOLEAN NOT NULL
);

CREATE TABLE dim_customer (
  customer_sk BIGSERIAL PRIMARY KEY,
  customer_id VARCHAR(30) NOT NULL, -- natural/business key
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(200),
  city VARCHAR(80),
  state VARCHAR(80),
  segment VARCHAR(40) NOT NULL,
  valid_from TIMESTAMP NOT NULL,
  valid_to TIMESTAMP NOT NULL,
  is_current BOOLEAN NOT NULL DEFAULT TRUE,
  version_number INTEGER NOT NULL DEFAULT 1,
  source_updated_at TIMESTAMP,
  CONSTRAINT ck_customer_window CHECK (valid_from < valid_to),
  CONSTRAINT ck_customer_version CHECK (version_number >= 1),
  CONSTRAINT uq_customer_version UNIQUE(customer_id, version_number)
);
CREATE UNIQUE INDEX uq_dim_customer_current ON dim_customer(customer_id) WHERE is_current;
CREATE INDEX ix_customer_history ON dim_customer(customer_id, valid_from, valid_to);

CREATE TABLE dim_product (
  product_sk BIGSERIAL PRIMARY KEY,
  product_id VARCHAR(30) NOT NULL UNIQUE,
  product_name VARCHAR(120) NOT NULL,
  category VARCHAR(80) NOT NULL,
  brand VARCHAR(80),
  current_unit_price NUMERIC(12,2) NOT NULL CHECK (current_unit_price >= 0),
  source_updated_at TIMESTAMP
);
CREATE TABLE dim_channel (
  channel_sk SMALLSERIAL PRIMARY KEY,
  channel_name VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE fact_sales (
  sales_sk BIGSERIAL PRIMARY KEY,
  order_id VARCHAR(40) NOT NULL,
  order_line_id INTEGER NOT NULL,
  date_sk INTEGER NOT NULL REFERENCES dim_date(date_sk),
  customer_sk BIGINT NOT NULL REFERENCES dim_customer(customer_sk),
  product_sk BIGINT NOT NULL REFERENCES dim_product(product_sk),
  channel_sk SMALLINT NOT NULL REFERENCES dim_channel(channel_sk),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
  gross_amount NUMERIC(14,2) NOT NULL CHECK (gross_amount >= 0),
  discount_amount NUMERIC(14,2) NOT NULL CHECK (discount_amount >= 0),
  net_amount NUMERIC(14,2) NOT NULL CHECK (net_amount >= 0),
  source_loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uq_fact_order_line UNIQUE(order_id, order_line_id)
);
CREATE INDEX ix_fact_date ON fact_sales(date_sk);
CREATE INDEX ix_fact_customer ON fact_sales(customer_sk);
CREATE INDEX ix_fact_product ON fact_sales(product_sk);
CREATE INDEX ix_fact_channel ON fact_sales(channel_sk);
