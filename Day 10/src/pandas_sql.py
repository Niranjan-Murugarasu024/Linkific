import pandas as pd
from sqlalchemy import create_engine, text
from src.config import sqlalchemy_url

def make_engine():
    return create_engine(sqlalchemy_url(), pool_pre_ping=True)

def products_dataframe() -> pd.DataFrame:
    query = text("""SELECT p.product_id,p.product_name,c.category_name,p.unit_price,p.stock_quantity
                    FROM products p JOIN categories c USING(category_id) ORDER BY p.product_id""")
    with make_engine().connect() as conn:
        return pd.read_sql_query(query, conn)

def customers_in_chunks(chunksize: int = 1000):
    if chunksize < 1:
        raise ValueError("chunksize must be positive")
    query = text("SELECT customer_id,first_name,last_name,city,state FROM customers ORDER BY customer_id")
    with make_engine().connect() as conn:
        yield from pd.read_sql_query(query, conn, chunksize=chunksize)

def export_products_csv(output_path: str = "data/products_export.csv") -> int:
    df = products_dataframe()
    df.to_csv(output_path, index=False)
    return len(df)

def save_dataframe(df: pd.DataFrame, table_name: str = "product_analysis") -> int:
    if table_name not in {"product_analysis", "daily_sales_analysis"}:
        raise ValueError("table_name is not in the allowlist")
    with make_engine().begin() as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False, method="multi", chunksize=500)
    return len(df)

if __name__ == "__main__":
    df = products_dataframe()
    print(df.head())
    print(f"Rows read: {len(df)}")
