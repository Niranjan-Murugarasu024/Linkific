"""Deterministic synthetic e-commerce data generator for Day 27.

Uses only the Python standard library so it can run on a Windows laptop without
extra packages. The generated core orders file contains exactly 200,000 rows,
including controlled invalid records and duplicate order events.
"""

from __future__ import annotations

import csv
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

ORDER_FIELDS = [
    "source_row_id",
    "order_id",
    "customer_id",
    "product_id",
    "region_id",
    "order_ts",
    "quantity",
    "unit_price",
    "discount_pct",
    "order_amount",
    "order_status",
    "payment_method",
    "updated_at",
    "received_at",
    "batch_id",
]

MANIFEST_FIELDS = ["source_row_id", "expected_status", "expected_reason"]


def _write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def generate_dataset(
    output_dir: str | Path,
    *,
    order_records: int = 200_000,
    customer_records: int = 25_000,
    product_records: int = 5_000,
    region_records: int = 20,
    duplicate_records: int = 2_000,
    seed: int = 27,
) -> dict:
    """Generate dimensions, orders and an expected-results manifest.

    `order_records` is the exact number of raw order rows, including duplicate
    copies. The remaining unique source events are generated first, followed by
    duplicate copies. Records are assigned to four sequential 50K batches by
    their final position in the raw orders file.
    """
    if order_records <= 0 or customer_records <= 0 or product_records <= 0 or region_records <= 0:
        raise ValueError("All dataset sizes must be positive integers.")
    if duplicate_records < 0 or duplicate_records >= order_records:
        raise ValueError("duplicate_records must be >= 0 and smaller than order_records.")
    if order_records % 4 != 0:
        raise ValueError("For this exercise, order_records must divide evenly into four batches.")

    unique_records = order_records - duplicate_records
    rng = random.Random(seed)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    regions = [
        {
            "region_id": f"R{i:02d}",
            "region_name": name,
            "country": "India",
        }
        for i, name in enumerate(
            [
                "North", "South", "East", "West", "Central", "North-East", "North-West",
                "South-East", "South-West", "Metro-1", "Metro-2", "Coastal-1", "Coastal-2",
                "Industrial-1", "Industrial-2", "Rural-1", "Rural-2", "Tier-2-1", "Tier-2-2", "Other",
            ][:region_records],
            start=1,
        )
    ]
    if len(regions) < region_records:
        regions.extend(
            {"region_id": f"R{i:02d}", "region_name": f"Region-{i:02d}", "country": "India"}
            for i in range(len(regions) + 1, region_records + 1)
        )

    customers = []
    segments = ["Consumer", "Corporate", "Small Business", "Enterprise"]
    for i in range(1, customer_records + 1):
        region = regions[(i * 7) % len(regions)]
        customers.append(
            {
                "customer_id": f"C{i:06d}",
                "customer_name": f"Customer {i:06d}",
                "email": f"customer{i:06d}@example.test",
                "region_id": region["region_id"],
                "customer_segment": segments[i % len(segments)],
                "signup_date": (datetime(2023, 1, 1) + timedelta(days=(i * 13) % 900)).date().isoformat(),
            }
        )

    categories = ["Electronics", "Home", "Fashion", "Sports", "Books", "Beauty", "Grocery", "Toys"]
    products = []
    for i in range(1, product_records + 1):
        products.append(
            {
                "product_id": f"P{i:05d}",
                "product_name": f"Product {i:05d}",
                "category": categories[(i * 5) % len(categories)],
                "unit_price": f"{rng.uniform(5.0, 750.0):.2f}",
                "supplier_id": f"SUP{((i - 1) % 250) + 1:04d}",
            }
        )

    customer_ids = [row["customer_id"] for row in customers]
    product_ids = [row["product_id"] for row in products]
    region_ids = [row["region_id"] for row in regions]
    statuses = ["PLACED", "PAID", "SHIPPED", "DELIVERED", "CANCELLED", "REFUNDED"]
    payment_methods = ["CARD", "UPI", "NET_BANKING", "WALLET", "COD"]
    epoch = datetime(2025, 1, 1)
    base_rows: list[dict] = []
    valid_base_rows: list[dict] = []
    manifest_rows: list[dict] = []

    # Pairwise-coprime divisors distribute several independent data-quality
    # defects across the dataset. Overlapping defects are intentionally kept.
    for index in range(1, unique_records + 1):
        source_row_id = f"SRC{index:06d}"
        order_id = f"ORD{index:08d}"
        customer_id = rng.choice(customer_ids)
        product_id = rng.choice(product_ids)
        region_id = rng.choice(region_ids)
        order_dt = epoch + timedelta(seconds=rng.randrange(365 * 24 * 60 * 60))
        quantity = rng.randint(1, 8)
        unit_price = round(rng.uniform(8.0, 600.0), 2)
        discount_pct = round(rng.uniform(0.0, 0.30), 2)
        order_amount = round(quantity * unit_price * (1.0 - discount_pct), 2)
        received_dt = order_dt + timedelta(days=rng.randint(1, 5))
        if index % 97 == 0:
            received_dt = order_dt + timedelta(days=rng.randint(60, 90))
        updated_dt = received_dt + timedelta(hours=rng.randint(0, 12))
        reasons: list[str] = []

        if index % 997 == 0:
            customer_id = ""
            reasons.append("CUSTOMER_NOT_FOUND")
        if index % 991 == 0:
            product_id = "P999999"
            reasons.append("PRODUCT_NOT_FOUND")
        if index % 983 == 0:
            quantity = -1
            reasons.append("INVALID_QUANTITY")
        if index % 977 == 0:
            unit_price = -3.50
            reasons.append("INVALID_UNIT_PRICE")
        if index % 971 == 0:
            order_ts = "not-a-timestamp"
            reasons.append("INVALID_ORDER_TIMESTAMP")
        else:
            order_ts = order_dt.strftime("%Y-%m-%d %H:%M:%S")
        if index % 953 == 0:
            discount_pct = 1.25
            reasons.append("INVALID_DISCOUNT")
        if index % 967 == 0:
            order_amount = round(order_amount + 37.25, 2)
            reasons.append("ORDER_AMOUNT_MISMATCH")

        row = {
            "source_row_id": source_row_id,
            "order_id": order_id,
            "customer_id": customer_id,
            "product_id": product_id,
            "region_id": region_id,
            "order_ts": order_ts,
            "quantity": str(quantity),
            "unit_price": f"{unit_price:.2f}",
            "discount_pct": f"{discount_pct:.2f}",
            "order_amount": f"{order_amount:.2f}",
            "order_status": rng.choice(statuses),
            "payment_method": rng.choice(payment_methods),
            "updated_at": updated_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "received_at": received_dt.strftime("%Y-%m-%d %H:%M:%S"),
            # The final batch is completed after duplicate rows are appended.
            "batch_id": "",
        }
        base_rows.append(row)
        expected_status = "REJECT" if reasons else "VALID"
        manifest_rows.append(
            {
                "source_row_id": source_row_id,
                "expected_status": expected_status,
                "expected_reason": "|".join(reasons) if reasons else "",
            }
        )
        if not reasons:
            valid_base_rows.append(row)

    if duplicate_records and not valid_base_rows:
        raise RuntimeError("No valid source records available to copy as duplicates.")

    # Duplicate source events reuse an existing order_id and carry identical
    # business values. Their source_row_id remains unique for row-level testing.
    duplicate_rows = []
    for duplicate_index in range(1, duplicate_records + 1):
        original = rng.choice(valid_base_rows)
        duplicate = dict(original)
        new_index = unique_records + duplicate_index
        duplicate["source_row_id"] = f"SRC{new_index:06d}"
        duplicate["batch_id"] = "BATCH_4"
        duplicate_rows.append(duplicate)
        manifest_rows.append(
            {
                "source_row_id": duplicate["source_row_id"],
                "expected_status": "DUPLICATE",
                "expected_reason": "DUPLICATE_ORDER_ID",
            }
        )

    # Four evenly sized ingestion batches; duplicate copies are intentionally
    # placed in BATCH_4 so cross-batch duplicate detection is exercised.
    for position, row in enumerate(base_rows):
        row["batch_id"] = f"BATCH_{position // (order_records // 4) + 1}"
    all_orders = base_rows + duplicate_rows

    counts = {
        "orders": _write_csv(output_dir / "orders.csv", ORDER_FIELDS, all_orders),
        "customers": _write_csv(output_dir / "customers.csv", list(customers[0].keys()), customers),
        "products": _write_csv(output_dir / "products.csv", list(products[0].keys()), products),
        "regions": _write_csv(output_dir / "regions.csv", list(regions[0].keys()), regions),
        "expected_manifest": _write_csv(output_dir / "expected_manifest.csv", MANIFEST_FIELDS, manifest_rows),
    }

    summary = {
        "seed": seed,
        "orders_raw_records": order_records,
        "unique_order_events_before_duplicate_injection": unique_records,
        "duplicate_source_records": duplicate_records,
        "expected_valid_source_records": sum(x["expected_status"] == "VALID" for x in manifest_rows),
        "expected_rejected_source_records": sum(x["expected_status"] == "REJECT" for x in manifest_rows),
        "expected_duplicate_source_records": sum(x["expected_status"] == "DUPLICATE" for x in manifest_rows),
        "customers": customer_records,
        "products": product_records,
        "regions": region_records,
        "batches": {f"BATCH_{i}": order_records // 4 for i in range(1, 5)},
        "files": counts,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    (output_dir / "generation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
