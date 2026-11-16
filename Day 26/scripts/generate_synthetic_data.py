"""Generate reproducible e-commerce CSV inputs for Day 26 scale testing.

Examples:
    python scripts/generate_synthetic_data.py --orders 100000 --customers 5000 --products 40 --invalid-rate 0.01 --seed 42
    python scripts/generate_synthetic_data.py --orders 500000 --customers 15000 --products 80 --invalid-rate 0.005 --seed 42

This overwrites data/input/orders.csv, customers.csv and products.csv.
"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = ROOT / "data" / "input"

CITIES = [
    ("Coimbatore", "South"),
    ("Chennai", "South"),
    ("Bengaluru", "South"),
    ("Hyderabad", "South"),
    ("Kochi", "South"),
    ("Mumbai", "West"),
    ("Pune", "West"),
    ("Delhi", "North"),
    ("Kolkata", "East"),
    ("Jaipur", "North"),
    ("Ahmedabad", "West"),
    ("Patna", "East"),
]

PRODUCT_FAMILIES = [
    ("Accessories", "Wireless Mouse", 420.00, 799.00),
    ("Accessories", "Mechanical Keyboard", 310.00, 499.00),
    ("Accessories", "USB-C Cable", 110.00, 299.00),
    ("Accessories", "Laptop Stand", 1450.00, 2499.00),
    ("Accessories", "Bluetooth Speaker", 980.00, 1899.00),
    ("Peripherals", "Webcam", 850.00, 1499.00),
    ("Audio", "Headset", 1250.00, 2199.00),
    ("Storage", "SSD 1TB", 2800.00, 4299.00),
    ("Storage", "Portable HDD", 2400.00, 3599.00),
    ("Displays", "27-inch Monitor", 920.00, 1299.00),
    ("Displays", "4K Monitor", 1320.00, 2099.00),
    ("Networking", "Wi-Fi Router", 1750.00, 2799.00),
    ("Office", "Printer", 6400.00, 9999.00),
    ("Office", "Docking Station", 5200.00, 7999.00),
    ("Gaming", "Gaming Mouse", 840.00, 1699.00),
    ("Gaming", "Mechanical Gaming Keyboard", 1500.00, 3499.00),
    ("Audio", "USB Microphone", 990.00, 1899.00),
    ("Accessories", "Laptop Sleeve", 520.00, 1299.00),
    ("Storage", "USB Flash Drive", 210.00, 599.00),
    ("Peripherals", "Graphics Tablet", 4200.00, 8999.00),
]


def build_products(product_count: int) -> list[dict[str, object]]:
    if product_count <= 0:
        raise ValueError("--products must be a positive integer")

    catalog = []
    for index in range(1, product_count + 1):
        family, name, cost, price = PRODUCT_FAMILIES[(index - 1) % len(PRODUCT_FAMILIES)]
        catalog.append({
            "product_id": f"P{index:04d}",
            "product_name": f"{name} {((index - 1) // len(PRODUCT_FAMILIES)) + 1}",
            "category": family,
            "unit_cost": round(cost + ((index % 7) * 13.50), 2),
            "unit_price": round(price + ((index % 5) * 8.25), 2),
        })
    return catalog


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_dataset(
    orders: int,
    customers: int,
    products: int,
    invalid_rate: float,
    seed: int,
    input_dir: Path,
    days: int = 180,
) -> tuple[int, int, int, int]:
    rng = random.Random(seed)
    input_dir.mkdir(parents=True, exist_ok=True)

    customer_rows = []
    for number in range(1, customers + 1):
        city, region = rng.choice(CITIES)
        customer_rows.append({
            "customer_id": f"C{number:06d}",
            "customer_name": f"Customer {number:06d}",
            "city": city,
            "region": region,
        })

    product_rows = build_products(products)

    write_rows(input_dir / "customers.csv", ["customer_id", "customer_name", "city", "region"], customer_rows)
    write_rows(input_dir / "products.csv", ["product_id", "product_name", "category", "unit_cost"], [
        {key: value for key, value in product.items() if key != "unit_price"} for product in product_rows
    ])

    customer_ids = [customer["customer_id"] for customer in customer_rows]
    start_date = date(2026, 1, 1)
    invalid_count = 0
    order_rows = []
    statuses = ["delivered", "shipped", "processing", "cancelled"]

    for number in range(1, orders + 1):
        product = rng.choice(product_rows)
        invalid = rng.random() < invalid_rate
        if invalid:
            invalid_count += 1
        order_date = start_date + timedelta(days=rng.randrange(0, days))
        order_rows.append({
            "order_line_id": f"OL-{number:010d}",
            "order_id": f"ORD-{(number // 5) + 1:010d}",
            "order_date": order_date.isoformat(),
            "customer_id": rng.choice(customer_ids),
            "product_id": "P9999" if invalid else product["product_id"],
            "quantity": rng.randint(1, 5),
            "unit_price": f"{float(product['unit_price']):.2f}",
            "status": rng.choice(statuses),
        })

    write_rows(input_dir / "orders.csv", [
        "order_line_id",
        "order_id",
        "order_date",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
        "status",
    ], order_rows)

    invalid_pct = (invalid_count / orders) * 100 if orders else 0.0
    return orders, customers, len(product_rows), invalid_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic e-commerce CSV datasets for Day 26.")
    parser.add_argument("--orders", type=int, default=100_000, help="Number of order-line records to generate")
    parser.add_argument("--customers", type=int, default=5_000, help="Number of unique customers")
    parser.add_argument("--products", type=int, default=40, help="Number of unique product rows to generate")
    parser.add_argument("--invalid-rate", type=float, default=0.01, help="Fraction of orders with unknown product IDs (0 to 1)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible data")
    parser.add_argument("--days", type=int, default=180, help="Date span in days for order transactions")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR, help="Directory where CSV inputs will be written")
    args = parser.parse_args()

    if args.orders <= 0 or args.customers <= 0 or args.products <= 0:
        parser.error("--orders, --customers and --products must be positive integers")
    if not 0 <= args.invalid_rate < 1:
        parser.error("--invalid-rate must be >= 0 and < 1")
    if args.days <= 0:
        parser.error("--days must be a positive integer")

    generated_orders, generated_customers, generated_products, invalid_count = generate_dataset(
        orders=args.orders,
        customers=args.customers,
        products=args.products,
        invalid_rate=args.invalid_rate,
        seed=args.seed,
        input_dir=args.input_dir,
        days=args.days,
    )

    invalid_pct = (invalid_count / generated_orders) * 100 if generated_orders else 0.0
    print(f"Generated {generated_orders:,} order lines in {args.input_dir / 'orders.csv'}")
    print(f"Customers: {generated_customers:,} | Products: {generated_products:,}")
    print(f"Deliberately invalid product references: {invalid_count:,} ({invalid_pct:.2f}%)")
    print("Input CSVs have been overwritten. Trigger a new Airflow DAG run to process them.")


if __name__ == "__main__":
    main()
