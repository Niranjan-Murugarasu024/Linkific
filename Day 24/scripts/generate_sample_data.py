from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "source"
OUT.mkdir(parents=True, exist_ok=True)
RNG = random.Random(24024)


def write_csv(filename: str, columns: list[str], rows: list[dict]) -> None:
    path = OUT / filename
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Created {path.relative_to(ROOT)} ({len(rows):,} rows)")


regions = [
    {"region_code": "SOUTH", "region_name": "South", "country": "India"},
    {"region_code": "WEST", "region_name": "West", "country": "India"},
    {"region_code": "NORTH", "region_name": "North", "country": "India"},
    {"region_code": "EAST", "region_name": "East", "country": "India"},
    {"region_code": "CENTRAL", "region_name": "Central", "country": "India"},
]
write_csv("regions.csv", list(regions[0]), regions)

cities = [
    ("Coimbatore", "Tamil Nadu", "SOUTH"), ("Chennai", "Tamil Nadu", "SOUTH"),
    ("Bengaluru", "Karnataka", "SOUTH"), ("Hyderabad", "Telangana", "SOUTH"),
    ("Kochi", "Kerala", "SOUTH"), ("Mumbai", "Maharashtra", "WEST"),
    ("Pune", "Maharashtra", "WEST"), ("Ahmedabad", "Gujarat", "WEST"),
    ("Jaipur", "Rajasthan", "NORTH"), ("New Delhi", "Delhi", "NORTH"),
    ("Lucknow", "Uttar Pradesh", "NORTH"), ("Kolkata", "West Bengal", "EAST"),
    ("Bhubaneswar", "Odisha", "EAST"), ("Patna", "Bihar", "EAST"),
    ("Indore", "Madhya Pradesh", "CENTRAL"), ("Bhopal", "Madhya Pradesh", "CENTRAL"),
]
first_names = ["Aarav", "Aditya", "Ananya", "Diya", "Ishaan", "Kavya", "Meera", "Nila", "Rohan", "Sanjay", "Tara", "Vikram", "Priya", "Arjun", "Ira", "Kiran"]
last_names = ["Sharma", "Iyer", "Reddy", "Nair", "Patel", "Gupta", "Rao", "Menon", "Das", "Singh", "Kapoor", "Murthy"]
segments = ["Consumer", "Corporate", "Small Business", "Home Office"]
customers: list[dict] = []
for customer_id in range(1001, 1081):
    city, state, region_code = RNG.choice(cities)
    full_name = f"{RNG.choice(first_names)} {RNG.choice(last_names)}"
    updated_at = date(2023, 1, 1) + timedelta(days=RNG.randint(0, 360))
    customers.append({
        "customer_id": customer_id,
        "full_name": full_name,
        "email": f"customer{customer_id}@example.com",
        "city": city,
        "state": state,
        "country": "India",
        "region_code": region_code,
        "segment": RNG.choice(segments),
        "updated_at": updated_at.isoformat(),
    })
write_csv("customers.csv", list(customers[0]), customers)

categories = ["Electronics", "Home & Kitchen", "Office Supplies", "Clothing", "Sports"]
brands = ["Aster", "Northstar", "Nova", "Vertex", "Orbit", "BluePeak"]
products: list[dict] = []
for product_id in range(2001, 2031):
    category = RNG.choice(categories)
    unit_cost = round(RNG.uniform(120, 18000), 2)
    list_price = round(unit_cost * RNG.uniform(1.18, 1.85), 2)
    products.append({
        "product_id": product_id,
        "sku": f"SKU-{product_id}",
        "product_name": f"{category.split()[0]} Product {product_id - 2000:02d}",
        "category": category,
        "brand": RNG.choice(brands),
        "unit_cost": f"{unit_cost:.2f}",
        "list_price": f"{list_price:.2f}",
        "is_active": "true" if product_id % 13 else "false",
        "updated_at": (date(2023, 6, 1) + timedelta(days=RNG.randint(0, 300))).isoformat(),
    })
write_csv("products.csv", list(products[0]), products)

orders: list[dict] = []
order_items: list[dict] = []
start = date(2024, 1, 1)
end = date(2026, 11, 10)
days = (end - start).days
item_id = 500001
for order_id in range(30001, 30501):
    order_date = start + timedelta(days=RNG.randint(0, days))
    customer = RNG.choice(customers)
    status = RNG.choices(["Completed", "Shipped", "Processing", "Cancelled"], weights=[65, 20, 10, 5])[0]
    orders.append({
        "order_id": order_id,
        "customer_id": customer["customer_id"],
        "order_date": order_date.isoformat(),
        "order_status": status,
    })
    for _ in range(RNG.randint(1, 3)):
        product = RNG.choice(products)
        quantity = RNG.randint(1, 5)
        unit_price = round(float(product["list_price"]) * RNG.uniform(0.88, 1.05), 2)
        discount_pct = round(RNG.choice([0, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20]), 4)
        order_items.append({
            "order_item_id": item_id,
            "order_id": order_id,
            "product_id": product["product_id"],
            "quantity": quantity,
            "unit_price": f"{unit_price:.2f}",
            "discount_pct": f"{discount_pct:.4f}",
        })
        item_id += 1
write_csv("orders.csv", list(orders[0]), orders)
write_csv("order_items.csv", list(order_items[0]), order_items)

holidays: list[dict] = []
for year in range(2023, 2028):
    for month, day, name in [
        (1, 26, "Republic Day"),
        (8, 15, "Independence Day"),
        (10, 2, "Gandhi Jayanti"),
        (12, 25, "Christmas Day"),
    ]:
        holidays.append({"holiday_date": date(year, month, day).isoformat(), "holiday_name": name, "country_code": "IN"})
write_csv("holidays.csv", list(holidays[0]), holidays)

print("\nSample source data generated successfully.")
print(f"Orders: {len(orders):,} | Order lines: {len(order_items):,} | Customers: {len(customers):,} | Products: {len(products):,}")
