from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
data = ROOT / "data"
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)

sales = pd.read_csv(data / "sales.csv", parse_dates=["order_date"])
customers = pd.read_csv(data / "customers.csv")
products = pd.read_csv(data / "products.csv")

enriched = sales.merge(customers, on="customer_id", how="left", validate="many_to_one", indicator="customer_match")
if not enriched["customer_match"].eq("both").all():
    raise ValueError("Some sales rows have no matching customer.")
enriched = enriched.drop(columns="customer_match").merge(
    products, on="product_id", how="left", validate="many_to_one", indicator="product_match"
)
if not enriched["product_match"].eq("both").all():
    raise ValueError("Some sales rows have no matching product.")
enriched["gross_margin"] = enriched["revenue"] - enriched["quantity"] * enriched["unit_cost"]
enriched.to_csv(reports / "enriched_sales.csv", index=False)
print(f"Saved {len(enriched)} enriched rows.")
