-- Reference schema; the ETL DAG creates this table automatically.
CREATE TABLE IF NOT EXISTS sales (
  order_id INTEGER PRIMARY KEY,
  order_date DATE NOT NULL,
  customer_id INTEGER NOT NULL,
  product TEXT NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
  total_amount NUMERIC(14,2) NOT NULL
);
