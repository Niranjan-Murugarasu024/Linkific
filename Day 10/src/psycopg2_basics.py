from contextlib import closing
import psycopg2
from psycopg2.extras import RealDictCursor
from src.config import database_config

def test_connection() -> str:
    with closing(psycopg2.connect(**database_config())) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user, version()")
            db, user, version = cur.fetchone()
            return f"Connected to {db} as {user}\n{version}"

def list_products(limit: int = 10) -> list[dict]:
    if not 1 <= limit <= 1000:
        raise ValueError("limit must be between 1 and 1000")
    with closing(psycopg2.connect(**database_config())) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT product_id, product_name, unit_price, stock_quantity FROM products ORDER BY product_id LIMIT %s", (limit,))
            return [dict(row) for row in cur.fetchall()]

def update_product_price(product_id: int, new_price: float) -> dict:
    if new_price < 0:
        raise ValueError("new_price cannot be negative")
    with closing(psycopg2.connect(**database_config())) as conn:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("UPDATE products SET unit_price=%s WHERE product_id=%s RETURNING product_id,product_name,unit_price", (new_price, product_id))
                row = cur.fetchone()
                if row is None:
                    raise LookupError(f"No product found with product_id={product_id}")
                return dict(row)

if __name__ == "__main__":
    print(test_connection())
    print(list_products(5))
