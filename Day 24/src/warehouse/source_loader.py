from __future__ import annotations

import csv
from pathlib import Path

from warehouse.config import PROJECT_ROOT


FILES = {
    "regions": ("regions.csv", "source.regions", "region_code,region_name,country"),
    "customers": (
        "customers.csv", "source.customers",
        "customer_id,full_name,email,city,state,country,region_code,segment,updated_at",
    ),
    "products": (
        "products.csv", "source.products",
        "product_id,sku,product_name,category,brand,unit_cost,list_price,is_active,updated_at",
    ),
    "orders": ("orders.csv", "source.orders", "order_id,customer_id,order_date,order_status"),
    "order_items": (
        "order_items.csv", "source.order_items",
        "order_item_id,order_id,product_id,quantity,unit_price,discount_pct",
    ),
    "holidays": ("holidays.csv", "source.holidays", "holiday_date,holiday_name,country_code"),
}


def load_source_data(connection) -> dict[str, int]:
    """Load supplied CSV files into the source schema in FK-safe order."""
    cursor = connection.cursor()
    try:
        cursor.execute(
            "TRUNCATE TABLE source.order_items, source.orders, source.customers, "
            "source.products, source.holidays, source.regions CASCADE"
        )
        counts: dict[str, int] = {}
        for logical_name, (filename, table_name, columns) in FILES.items():
            path = PROJECT_ROOT / "data" / "source" / filename
            if not path.exists():
                raise FileNotFoundError(f"Missing source file: {path}. Run scripts/generate_sample_data.py")
            with path.open("r", encoding="utf-8", newline="") as source_file:
                reader = csv.DictReader(source_file)
                if reader.fieldnames != columns.split(","):
                    raise ValueError(f"Unexpected CSV columns in {filename}: {reader.fieldnames}")
                row_count = sum(1 for _ in reader)
            with path.open("r", encoding="utf-8", newline="") as source_file:
                cursor.copy_expert(
                    f"COPY {table_name} ({columns}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)",
                    source_file,
                )
            counts[logical_name] = row_count
        connection.commit()
        return counts
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
