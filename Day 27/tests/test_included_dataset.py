from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "generated"


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_included_dataset_has_200k_orders_and_manifest_rows():
    orders = read_csv(DATA_DIR / "orders.csv")
    manifest = read_csv(DATA_DIR / "expected_manifest.csv")
    assert len(orders) == 200_000
    assert len(manifest) == 200_000


def test_included_dataset_has_four_50k_batches():
    orders = read_csv(DATA_DIR / "orders.csv")
    counts = Counter(row["batch_id"] for row in orders)
    assert counts == {"BATCH_1": 50_000, "BATCH_2": 50_000, "BATCH_3": 50_000, "BATCH_4": 50_000}


def test_included_manifest_matches_expected_classification_counts():
    manifest = read_csv(DATA_DIR / "expected_manifest.csv")
    counts = Counter(row["expected_status"] for row in manifest)
    assert counts["VALID"] == 196_586
    assert counts["REJECT"] == 1_414
    assert counts["DUPLICATE"] == 2_000
