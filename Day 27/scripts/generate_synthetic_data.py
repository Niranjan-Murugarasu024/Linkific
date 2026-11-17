from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.day27.data_generator import generate_dataset  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate reproducible Day 27 e-commerce test data.")
    parser.add_argument("--output", default=str(PROJECT_ROOT / "data" / "generated"), help="Output directory")
    parser.add_argument("--orders", type=int, default=200_000, help="Exact raw order-row count")
    parser.add_argument("--customers", type=int, default=25_000)
    parser.add_argument("--products", type=int, default=5_000)
    parser.add_argument("--regions", type=int, default=20)
    parser.add_argument("--duplicates", type=int, default=2_000)
    parser.add_argument("--seed", type=int, default=27)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = generate_dataset(
        args.output,
        order_records=args.orders,
        customer_records=args.customers,
        product_records=args.products,
        region_records=args.regions,
        duplicate_records=args.duplicates,
        seed=args.seed,
    )
    print(json.dumps(summary, indent=2))
    print(f"\nSynthetic data written to: {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
