"""Generate deterministic, larger synthetic e-commerce source CSVs."""

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ("Accessories", "Electronics", "Home", "Office", "Outdoor")
BRANDS = ("DemoBrand", "Northstar", "Everyday", "Acme", "Contoso")
CITIES = (
    ("Chennai", "Tamil Nadu"),
    ("Coimbatore", "Tamil Nadu"),
    ("Bengaluru", "Karnataka"),
    ("Mysuru", "Karnataka"),
    ("Hyderabad", "Telangana"),
    ("Warangal", "Telangana"),
    ("Mumbai", "Maharashtra"),
    ("Pune", "Maharashtra"),
    ("Kochi", "Kerala"),
    ("Thiruvananthapuram", "Kerala"),
    ("Jaipur", "Rajasthan"),
    ("Jodhpur", "Rajasthan"),
    ("Ahmedabad", "Gujarat"),
    ("Surat", "Gujarat"),
    ("Lucknow", "Uttar Pradesh"),
    ("Kanpur", "Uttar Pradesh"),
    ("Bhopal", "Madhya Pradesh"),
    ("Indore", "Madhya Pradesh"),
    ("Patna", "Bihar"),
    ("Ranchi", "Jharkhand"),
)


def _write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def generate_sample_data(
    output_dir: str | Path = PROJECT_ROOT / "data" / "sample",
    sales_rows: int = 10_000,
    product_count: int = 250,
    customer_count: int = 1_000,
    region_count: int = 20,
    seed: int = 42,
) -> dict[str, int]:
    """Write a deterministic connected data set and return per-file row counts."""
    for name, count in (
        ("sales_rows", sales_rows),
        ("product_count", product_count),
        ("customer_count", customer_count),
        ("region_count", region_count),
    ):
        if count <= 0:
            raise ValueError(f"{name} must be greater than zero.")
    if region_count > len(CITIES):
        raise ValueError(f"region_count cannot exceed {len(CITIES)}.")

    randomizer = random.Random(seed)
    output_path = Path(output_dir)
    products = [
        {
            "product_id": f"P-{index:04d}",
            "product_name": f"{CATEGORIES[(index - 1) % len(CATEGORIES)]} Item {index:04d}",
            "category": CATEGORIES[(index - 1) % len(CATEGORIES)],
            "brand": BRANDS[(index - 1) % len(BRANDS)],
            "unit_cost": f"{randomizer.uniform(5, 800):.2f}",
        }
        for index in range(1, product_count + 1)
    ]
    customers = [
        {
            "customer_id": f"C-{index:05d}",
            "customer_name": f"Sample Customer {index:05d}",
            "city": CITIES[(index - 1) % region_count][0],
            "segment": ("Consumer", "Small Business", "Enterprise")[
                (index - 1) % 3
            ],
        }
        for index in range(1, customer_count + 1)
    ]
    regions = [
        {
            "region_id": f"R-{index:02d}",
            "region_name": CITIES[index - 1][0],
            "state": CITIES[index - 1][1],
            "country": "India",
        }
        for index in range(1, region_count + 1)
    ]

    first_order_date = date(2026, 1, 1)
    sales = []
    for index in range(1, sales_rows + 1):
        quantity = randomizer.randint(1, 5)
        unit_price = randomizer.randint(20, 2_500)
        gross_amount = quantity * unit_price
        discount_amount = randomizer.choice(
            (0, 0, 0, round(gross_amount * 0.05, 2), round(gross_amount * 0.1, 2))
        )
        sales.append(
            {
                "source_sales_id": f"S-{index:08d}-1",
                "order_date": (
                    first_order_date + timedelta(days=randomizer.randrange(365))
                ).isoformat(),
                "product_id": randomizer.choice(products)["product_id"],
                "customer_id": randomizer.choice(customers)["customer_id"],
                "region_id": randomizer.choice(regions)["region_id"],
                "quantity": quantity,
                "unit_price": f"{unit_price:.2f}",
                "discount_amount": f"{discount_amount:.2f}",
            }
        )

    snapshot_date = date(2026, 11, 6).isoformat()
    inventory = []
    for product in products:
        for region in regions:
            inventory.append(
                {
                    "snapshot_date": snapshot_date,
                    "product_id": product["product_id"],
                    "region_id": region["region_id"],
                    "available_quantity": randomizer.randint(0, 250),
                    "reorder_level": randomizer.randint(10, 50),
                    "unit_cost": product["unit_cost"],
                }
            )

    _write_csv(
        output_path / "products_sample.csv",
        ["product_id", "product_name", "category", "brand", "unit_cost"],
        products,
    )
    _write_csv(
        output_path / "customers_sample.csv",
        ["customer_id", "customer_name", "city", "segment"],
        customers,
    )
    _write_csv(
        output_path / "regions_sample.csv",
        ["region_id", "region_name", "state", "country"],
        regions,
    )
    _write_csv(
        output_path / "sales_sample.csv",
        [
            "source_sales_id",
            "order_date",
            "product_id",
            "customer_id",
            "region_id",
            "quantity",
            "unit_price",
            "discount_amount",
        ],
        sales,
    )
    _write_csv(
        output_path / "inventory_sample.csv",
        [
            "snapshot_date",
            "product_id",
            "region_id",
            "available_quantity",
            "reorder_level",
            "unit_cost",
        ],
        inventory,
    )
    return {
        "sales": len(sales),
        "products": len(products),
        "customers": len(customers),
        "regions": len(regions),
        "inventory": len(inventory),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "data" / "sample")
    parser.add_argument("--sales-rows", type=int, default=10_000)
    parser.add_argument("--products", type=int, default=250)
    parser.add_argument("--customers", type=int, default=1_000)
    parser.add_argument("--regions", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(
        generate_sample_data(
            output_dir=args.output_dir,
            sales_rows=args.sales_rows,
            product_count=args.products,
            customer_count=args.customers,
            region_count=args.regions,
            seed=args.seed,
        )
    )


if __name__ == "__main__":
    main()
