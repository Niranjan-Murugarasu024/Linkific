from __future__ import annotations

import csv
from collections import Counter

from src.day27.data_generator import generate_dataset


def read_rows(path):
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_small_dataset_has_exact_requested_order_count(tmp_path):
    summary = generate_dataset(
        tmp_path,
        order_records=400,
        customer_records=80,
        product_records=30,
        region_records=5,
        duplicate_records=40,
        seed=99,
    )
    orders = read_rows(tmp_path / "orders.csv")
    manifest = read_rows(tmp_path / "expected_manifest.csv")
    assert len(orders) == 400
    assert len(manifest) == 400
    assert summary["batches"] == {"BATCH_1": 100, "BATCH_2": 100, "BATCH_3": 100, "BATCH_4": 100}


def test_manifest_reconciles_and_has_duplicate_class(tmp_path):
    generate_dataset(
        tmp_path,
        order_records=400,
        customer_records=80,
        product_records=30,
        region_records=5,
        duplicate_records=40,
        seed=100,
    )
    manifest = read_rows(tmp_path / "expected_manifest.csv")
    counts = Counter(row["expected_status"] for row in manifest)
    assert sum(counts.values()) == 400
    assert counts["DUPLICATE"] == 40
    assert counts["VALID"] + counts["REJECT"] == 360


def test_duplicate_events_have_distinct_source_ids_and_repeated_order_ids(tmp_path):
    generate_dataset(
        tmp_path,
        order_records=400,
        customer_records=80,
        product_records=30,
        region_records=5,
        duplicate_records=40,
        seed=101,
    )
    orders = read_rows(tmp_path / "orders.csv")
    source_ids = [row["source_row_id"] for row in orders]
    order_ids = [row["order_id"] for row in orders]
    assert len(source_ids) == len(set(source_ids))
    assert len(order_ids) > len(set(order_ids))


def test_generator_is_deterministic_for_same_seed(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    kwargs = dict(order_records=400, customer_records=80, product_records=30, region_records=5, duplicate_records=40, seed=123)
    generate_dataset(first, **kwargs)
    generate_dataset(second, **kwargs)
    assert (first / "orders.csv").read_bytes() == (second / "orders.csv").read_bytes()
    assert (first / "expected_manifest.csv").read_bytes() == (second / "expected_manifest.csv").read_bytes()


def test_invalid_batch_configuration_is_rejected(tmp_path):
    try:
        generate_dataset(tmp_path, order_records=401, duplicate_records=20)
    except ValueError as exc:
        assert "divide evenly into four batches" in str(exc)
    else:
        raise AssertionError("Expected ValueError for a non-divisible order count.")
