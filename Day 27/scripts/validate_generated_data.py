from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "generated"


def count_csv(path: Path) -> int:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return max(sum(1 for _ in csv.reader(handle)) - 1, 0)


def main() -> None:
    required = ["orders.csv", "customers.csv", "products.csv", "regions.csv", "expected_manifest.csv"]
    missing = [name for name in required if not (DATA_DIR / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing generated files: {missing}. Run scripts/generate_synthetic_data.py first.")

    orders = count_csv(DATA_DIR / "orders.csv")
    manifest_counts = Counter()
    with (DATA_DIR / "expected_manifest.csv").open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            manifest_counts[row["expected_status"]] += 1

    summary = json.loads((DATA_DIR / "generation_summary.json").read_text(encoding="utf-8"))
    assert orders == summary["orders_raw_records"], (orders, summary["orders_raw_records"])
    assert sum(manifest_counts.values()) == orders
    assert manifest_counts["DUPLICATE"] == summary["duplicate_source_records"]
    print("Generated-data validation passed.")
    print(f"Orders: {orders:,}")
    print(f"Manifest: {dict(manifest_counts)}")


if __name__ == "__main__":
    main()
