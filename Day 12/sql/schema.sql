CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL
);

INSERT INTO customers (customer_id, customer_name)
VALUES
    (101, 'Anita'),
    (102, 'Rahul'),
    (103, 'Priya'),
    (104, 'Karthik')
ON CONFLICT (customer_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS product_catalog (
    product_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    price NUMERIC(12, 2)
);

CREATE TABLE IF NOT EXISTS fact_sales (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    customer_name TEXT,
    product_id INTEGER NOT NULL,
    product_name TEXT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    total_amount NUMERIC(14, 2) NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS etl_watermarks (
    pipeline_name TEXT PRIMARY KEY,
    last_updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS etl_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    load_type TEXT NOT NULL,
    status TEXT NOT NULL,
    records_processed INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_fact_sales_updated_at
ON fact_sales(updated_at);