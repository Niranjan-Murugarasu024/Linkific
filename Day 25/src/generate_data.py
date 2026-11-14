"""Generate deterministic e-commerce snapshot and CDC sample CSV files."""
from __future__ import annotations
import argparse
from pathlib import Path
import random
from datetime import date, datetime, timedelta
import pandas as pd


def generate(output: Path, orders: int = 5000, seed: int = 42) -> None:
    random.seed(seed)
    output.mkdir(parents=True, exist_ok=True)
    regions = [
        {"region_id": 1, "region_name": "South", "country": "India"},
        {"region_id": 2, "region_name": "North", "country": "India"},
        {"region_id": 3, "region_name": "West", "country": "India"},
        {"region_id": 4, "region_name": "East", "country": "India"},
    ]
    customers = []
    for cid in range(1, 501):
        customers.append({
            "customer_id": cid,
            "customer_name": f"Customer {cid:04d}",
            "email": f"customer{cid:04d}@example.com",
            "region_id": random.choice(regions)["region_id"],
            "created_at": (date(2024, 1, 1) + timedelta(days=random.randint(0, 700))).isoformat(),
        })
    products = []
    categories = ["Electronics", "Home", "Fashion", "Books", "Sports"]
    for pid in range(1, 101):
        products.append({
            "product_id": pid,
            "product_name": f"Product {pid:03d}",
            "category": categories[(pid - 1) % len(categories)],
            "unit_price": round(random.uniform(100, 25000), 2),
            "is_active": True,
        })
    orders_rows = []
    start = date(2025, 1, 1)
    for idx in range(1, orders + 1):
        pid = random.randint(1, 100)
        product = products[pid - 1]
        qty = random.randint(1, 5)
        order_date = start + timedelta(days=random.randint(0, 650))
        unit_price = round(product["unit_price"] * random.uniform(0.9, 1.1), 2)
        discount = round(random.choice([0, 0, 0.05, 0.10, 0.15]), 2)
        orders_rows.append({
            "order_id": idx,
            "line_id": 1,
            "customer_id": random.randint(1, 500),
            "product_id": pid,
            "region_id": None,  # resolved from customer in the transformation layer
            "order_date": order_date.isoformat(),
            "quantity": qty,
            "unit_price": unit_price,
            "discount_pct": discount,
            "status": random.choice(["COMPLETED", "COMPLETED", "SHIPPED", "PENDING"]),
            "updated_at": datetime.combine(order_date, datetime.min.time()).isoformat(sep=" "),
        })
    customer_region = {c["customer_id"]: c["region_id"] for c in customers}
    for row in orders_rows:
        row["region_id"] = customer_region[row["customer_id"]]

    # Deterministic change set: 20 inserts, 15 updates, 5 deletes.
    changes = []
    next_id = orders + 1
    for j in range(20):
        pid = random.randint(1, 100)
        prod = products[pid - 1]
        cid = random.randint(1, 500)
        od = date(2026, 11, 1) + timedelta(days=j % 10)
        changes.append({
            "order_id": next_id + j, "line_id": 1, "customer_id": cid,
            "product_id": pid, "region_id": customer_region[cid],
            "order_date": od.isoformat(), "quantity": random.randint(1, 4),
            "unit_price": round(prod["unit_price"], 2), "discount_pct": 0.05,
            "status": "COMPLETED", "updated_at": f"2026-11-14 08:{j:02d}:00", "op": "I",
        })
    for j in range(min(15, orders)):
        original = orders_rows[j]
        changes.append({
            **original, "quantity": original["quantity"] + 1,
            "status": "COMPLETED", "updated_at": f"2026-11-14 09:{j:02d}:00", "op": "U",
        })
    for j in range(min(5, orders)):
        original = orders_rows[-(j + 1)]
        changes.append({
            **original, "updated_at": f"2026-11-14 10:{j:02d}:00", "op": "D",
        })

    pd.DataFrame(customers).to_csv(output / "customers.csv", index=False)
    pd.DataFrame(products).to_csv(output / "products.csv", index=False)
    pd.DataFrame(regions).to_csv(output / "regions.csv", index=False)
    pd.DataFrame(orders_rows).to_csv(output / "orders.csv", index=False)
    pd.DataFrame(changes).to_csv(output / "order_changes.csv", index=False)
    print(f"Generated {len(orders_rows):,} order lines and {len(changes):,} CDC events in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data"))
    parser.add_argument("--orders", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    generate(args.output, args.orders, args.seed)
