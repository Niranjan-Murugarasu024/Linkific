CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE IF NOT EXISTS dw.dim_region (
    region_key SMALLSERIAL PRIMARY KEY,
    region_code VARCHAR(20) NOT NULL UNIQUE,
    region_name VARCHAR(80) NOT NULL,
    country VARCHAR(80) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS dw.dim_customer (
    customer_key BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    full_name VARCHAR(160) NOT NULL,
    email VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(80) NOT NULL,
    region_code VARCHAR(20) NOT NULL REFERENCES dw.dim_region(region_code),
    segment VARCHAR(40),
    record_hash CHAR(64) NOT NULL,
    source_updated_at DATE NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL DEFAULT DATE '9999-12-31',
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_customer_valid_dates CHECK (valid_to >= valid_from)
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_dim_customer_one_current
    ON dw.dim_customer(customer_id) WHERE is_current = TRUE;
CREATE INDEX IF NOT EXISTS ix_dim_customer_natural_dates
    ON dw.dim_customer(customer_id, valid_from, valid_to);
CREATE INDEX IF NOT EXISTS ix_dim_customer_region ON dw.dim_customer(region_code);

CREATE TABLE IF NOT EXISTS dw.dim_product (
    product_key BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL UNIQUE,
    sku VARCHAR(40) NOT NULL UNIQUE,
    product_name VARCHAR(160) NOT NULL,
    category VARCHAR(80),
    brand VARCHAR(80),
    unit_cost NUMERIC(12,2) NOT NULL CHECK (unit_cost >= 0),
    list_price NUMERIC(12,2) NOT NULL CHECK (list_price >= 0),
    is_active BOOLEAN NOT NULL,
    source_updated_at DATE NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_dim_product_category ON dw.dim_product(category);

CREATE TABLE IF NOT EXISTS dw.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day_of_month SMALLINT NOT NULL,
    day_name VARCHAR(12) NOT NULL,
    iso_day_of_week SMALLINT NOT NULL,
    week_of_year SMALLINT NOT NULL,
    month_number SMALLINT NOT NULL,
    month_name VARCHAR(12) NOT NULL,
    quarter_number SMALLINT NOT NULL,
    quarter_label VARCHAR(8) NOT NULL,
    year_number SMALLINT NOT NULL,
    fiscal_year SMALLINT NOT NULL,
    fiscal_quarter SMALLINT NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_month_start BOOLEAN NOT NULL,
    is_month_end BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL DEFAULT FALSE,
    holiday_name VARCHAR(250),
    holiday_country_codes VARCHAR(50)
);
CREATE INDEX IF NOT EXISTS ix_dim_date_year_month ON dw.dim_date(year_number, month_number);
CREATE INDEX IF NOT EXISTS ix_dim_date_fiscal ON dw.dim_date(fiscal_year, fiscal_quarter);

CREATE TABLE IF NOT EXISTS dw.fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,
    source_order_item_id BIGINT NOT NULL UNIQUE,
    order_id BIGINT NOT NULL,
    date_key INTEGER NOT NULL REFERENCES dw.dim_date(date_key),
    customer_key BIGINT NOT NULL REFERENCES dw.dim_customer(customer_key),
    product_key BIGINT NOT NULL REFERENCES dw.dim_product(product_key),
    region_key SMALLINT NOT NULL REFERENCES dw.dim_region(region_key),
    order_status VARCHAR(30) NOT NULL,
    quantity NUMERIC(12,2) NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    discount_pct NUMERIC(6,4) NOT NULL CHECK (discount_pct BETWEEN 0 AND 1),
    gross_sales NUMERIC(14,2) NOT NULL,
    discount_amount NUMERIC(14,2) NOT NULL,
    net_sales NUMERIC(14,2) NOT NULL,
    unit_cost NUMERIC(12,2) NOT NULL,
    total_cost NUMERIC(14,2) NOT NULL,
    profit NUMERIC(14,2) NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_fact_sales_date ON dw.fact_sales(date_key);
CREATE INDEX IF NOT EXISTS ix_fact_sales_customer_date ON dw.fact_sales(customer_key, date_key);
CREATE INDEX IF NOT EXISTS ix_fact_sales_product_date ON dw.fact_sales(product_key, date_key);
CREATE INDEX IF NOT EXISTS ix_fact_sales_region_date ON dw.fact_sales(region_key, date_key);
CREATE INDEX IF NOT EXISTS ix_fact_sales_order ON dw.fact_sales(order_id);
