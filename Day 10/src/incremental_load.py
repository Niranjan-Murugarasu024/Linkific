from sqlalchemy import create_engine, text
from src.config import sqlalchemy_url

def run() -> int:
    engine = create_engine(sqlalchemy_url(), pool_pre_ping=True)
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE IF NOT EXISTS order_extract (
            order_id BIGINT PRIMARY KEY,customer_id BIGINT NOT NULL,order_date TIMESTAMPTZ NOT NULL,
            status TEXT NOT NULL,extracted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP)"""))
        watermark = conn.execute(text("SELECT COALESCE(MAX(order_id),0) FROM order_extract")).scalar_one()
        rows = conn.execute(text("""SELECT order_id,customer_id,order_date,status FROM orders
            WHERE order_id > :watermark ORDER BY order_id"""), {"watermark":watermark}).mappings().all()
        for row in rows:
            conn.execute(text("""INSERT INTO order_extract(order_id,customer_id,order_date,status)
                VALUES (:order_id,:customer_id,:order_date,:status)
                ON CONFLICT(order_id) DO UPDATE SET status=EXCLUDED.status,
                customer_id=EXCLUDED.customer_id,order_date=EXCLUDED.order_date,
                extracted_at=CURRENT_TIMESTAMP"""), row)
    engine.dispose()
    print(f"Loaded {len(rows)} new rows after watermark {watermark}.")
    return len(rows)

if __name__ == "__main__":
    run()
