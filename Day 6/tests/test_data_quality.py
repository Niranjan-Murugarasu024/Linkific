from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def test_sales_keys_and_foreign_keys():
    sales = pd.read_csv(ROOT / "data" / "sales.csv")
    customers = pd.read_csv(ROOT / "data" / "customers.csv")
    products = pd.read_csv(ROOT / "data" / "products.csv")
    assert sales["sale_id"].is_unique
    assert set(sales["customer_id"]).issubset(set(customers["customer_id"]))
    assert set(sales["product_id"]).issubset(set(products["product_id"]))

def test_daily_dates_are_unique_and_sorted():
    daily = pd.read_csv(ROOT / "data" / "daily_sales.csv", parse_dates=["date"])
    assert daily["date"].is_unique
    assert daily["date"].is_monotonic_increasing
