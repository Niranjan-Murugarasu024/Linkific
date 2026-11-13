CREATE SCHEMA IF NOT EXISTS source;

CREATE TABLE IF NOT EXISTS source.regions (
    region_code VARCHAR(20) PRIMARY KEY,
    region_name VARCHAR(80) NOT NULL,
    country VARCHAR(80) NOT NULL
);

CREATE TABLE IF NOT EXISTS source.customers (
    customer_id BIGINT PRIMARY KEY,
    full_name VARCHAR(160) NOT NULL,
    email VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(80) NOT NULL,
    region_code VARCHAR(20) NOT NULL REFERENCES source.regions(region_code),
    segment VARCHAR(40),
    updated_at DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS source.products (
    product_id BIGINT PRIMARY KEY,
    sku VARCHAR(40) NOT NULL UNIQUE,
    product_name VARCHAR(160) NOT NULL,
    category VARCHAR(80),
    brand VARCHAR(80),
    unit_cost NUMERIC(12,2) NOT NULL CHECK (unit_cost >= 0),
    list_price NUMERIC(12,2) NOT NULL CHECK (list_price >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS source.orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES source.customers(customer_id),
    order_date DATE NOT NULL,
    order_status VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS source.order_items (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES source.orders(order_id),
    product_id BIGINT NOT NULL REFERENCES source.products(product_id),
    quantity NUMERIC(12,2) NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    discount_pct NUMERIC(6,4) NOT NULL DEFAULT 0 CHECK (discount_pct BETWEEN 0 AND 1)
);

CREATE TABLE IF NOT EXISTS source.holidays (
    holiday_date DATE NOT NULL,
    holiday_name VARCHAR(120) NOT NULL,
    country_code CHAR(2) NOT NULL DEFAULT 'IN',
    PRIMARY KEY (holiday_date, country_code)
);

CREATE INDEX IF NOT EXISTS ix_source_orders_order_date ON source.orders(order_date);
CREATE INDEX IF NOT EXISTS ix_source_orders_customer ON source.orders(customer_id);
CREATE INDEX IF NOT EXISTS ix_source_order_items_order ON source.order_items(order_id);
CREATE INDEX IF NOT EXISTS ix_source_order_items_product ON source.order_items(product_id);
