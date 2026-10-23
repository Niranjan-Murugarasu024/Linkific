CREATE TABLE IF NOT EXISTS daily_sales_staging (
    event_id TEXT NOT NULL,event_date TIMESTAMP NOT NULL,region TEXT NOT NULL,
    orders_count BIGINT NOT NULL CHECK (orders_count >= 0),
    sales_amount NUMERIC(14,2) NOT NULL CHECK (sales_amount >= 0)
);
CREATE INDEX IF NOT EXISTS idx_daily_sales_staging_date ON daily_sales_staging(event_date);
