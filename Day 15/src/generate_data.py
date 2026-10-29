"""Create a reproducible, synthetic retail-sales dataset for visualization practice.

The generated records are fictional and do not represent a real company or customer.
Run from the project root: python src/generate_data.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

SEED = 42
N_ROWS = 1600
rng = np.random.default_rng(SEED)

products = {
    "Electronics": [("Wireless Mouse", 800, 0.24), ("Keyboard", 1500, 0.22), ("Headphones", 2400, 0.26), ("Monitor", 12500, 0.18)],
    "Home": [("Desk Lamp", 1200, 0.30), ("Storage Box", 650, 0.28), ("Office Chair", 7800, 0.21), ("Water Bottle", 450, 0.32)],
    "Clothing": [("T-Shirt", 700, 0.35), ("Jeans", 1800, 0.31), ("Jacket", 3200, 0.26), ("Sneakers", 2800, 0.24)],
    "Books": [("Data Science Book", 900, 0.33), ("Business Book", 600, 0.36), ("Exam Guide", 500, 0.34), ("Design Handbook", 1100, 0.30)],
    "Office Supplies": [("Notebook Pack", 250, 0.38), ("Pen Set", 180, 0.40), ("Backpack", 1600, 0.29), ("Whiteboard", 2100, 0.25)],
}
regions = {
    "South": ["Chennai", "Coimbatore", "Bengaluru", "Hyderabad", "Kochi"],
    "West": ["Mumbai", "Pune", "Ahmedabad", "Surat", "Panaji"],
    "North": ["Delhi", "Jaipur", "Lucknow", "Chandigarh", "Dehradun"],
    "East": ["Kolkata", "Bhubaneswar", "Guwahati", "Patna", "Ranchi"],
}

categories = list(products)
category_prob = [0.23, 0.20, 0.22, 0.15, 0.20]
cat_choices = rng.choice(categories, size=N_ROWS, p=category_prob)
start = np.datetime64("2024-01-01")
end = np.datetime64("2026-01-01")
day_offsets = rng.integers(0, int((end - start) / np.timedelta64(1, "D")), size=N_ROWS)
order_dates = pd.to_datetime(start + day_offsets.astype("timedelta64[D]"))

rows = []
for i, (cat, date) in enumerate(zip(cat_choices, order_dates), start=1):
    product, base_price, margin = products[cat][int(rng.integers(0, len(products[cat])))]
    quantity = int(rng.choice([1, 2, 3, 4, 5], p=[0.43, 0.28, 0.15, 0.09, 0.05]))
    # Promotions vary by period and channel; discounts stay within a realistic 0–30% range.
    channel = str(rng.choice(["Online", "Retail Store", "Marketplace"], p=[0.48, 0.30, 0.22]))
    max_discount = 0.30 if channel != "Retail Store" else 0.20
    discount = float(rng.choice([0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], p=[0.24, 0.18, 0.22, 0.16, 0.12, 0.06, 0.02]))
    discount = min(discount, max_discount)
    unit_price = round(float(base_price * rng.uniform(0.88, 1.14)), 2)
    sales = round(unit_price * quantity * (1 - discount), 2)
    noise = float(rng.normal(0, 0.045))
    profit = round(sales * (margin - discount * 0.75 + noise), 2)
    region = str(rng.choice(list(regions)))
    city = str(rng.choice(regions[region]))
    segment = str(rng.choice(["Consumer", "Small Business", "Enterprise"], p=[0.62, 0.27, 0.11]))
    rows.append({
        "order_id": f"ORD-{i:05d}",
        "order_date": date.strftime("%Y-%m-%d"),
        "region": region,
        "city": city,
        "category": cat,
        "product": product,
        "quantity": quantity,
        "unit_price": unit_price,
        "discount": discount,
        "sales": sales,
        "profit": profit,
        "channel": channel,
        "customer_segment": segment,
    })

df = pd.DataFrame(rows).sort_values("order_date").reset_index(drop=True)
output = DATA_DIR / "sales.csv"
df.to_csv(output, index=False)
print(f"Created {len(df):,} fictional sales rows: {output}")
print(df.head(5).to_string(index=False))
