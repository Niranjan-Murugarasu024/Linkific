"""Tests for the e-commerce pipeline's core transformations."""

from pathlib import Path

import pandas as pd
import pytest

from src.ingestion.common import read_source_csv
from src.ingestion.extract_customers import extract_customers
from src.ingestion.extract_products import extract_products
from src.ingestion.extract_sales import extract_sales
from src.pipeline import _write_batch_csvs
from src.transformation.clean_sales import clean_sales
from src.transformation.transform_dimensions import (
    build_date_dimension,
    normalize_customers,
    normalize_products,
    normalize_regions,
)
from src.transformation.transform_inventory import transform_inventory
from src.validation.data_quality import validate_foreign_keys

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_clean_sales_calculates_line_net_sales() -> None:
    sales = pd.DataFrame(
        {
            "source_sales_id": ["S-1"],
            "order_date": ["2026-11-01"],
            "product_id": ["P-1"],
            "customer_id": ["C-1"],
            "region_id": ["R-1"],
            "quantity": ["2"],
            "unit_price": ["499.00"],
            "discount_amount": ["50.00"],
        }
    )

    result = clean_sales(sales)

    assert result.loc[0, "quantity"] == 2
    assert result.loc[0, "sales_amount"] == 948.0
    assert pd.api.types.is_datetime64_any_dtype(result["order_date"])


def test_clean_sales_rejects_discount_larger_than_gross_sales() -> None:
    sales = pd.DataFrame(
        {
            "source_sales_id": ["S-1"],
            "order_date": ["2026-11-01"],
            "product_id": ["P-1"],
            "customer_id": ["C-1"],
            "region_id": ["R-1"],
            "quantity": ["1"],
            "unit_price": ["10"],
            "discount_amount": ["11"],
        }
    )

    with pytest.raises(ValueError, match="discount cannot exceed"):
        clean_sales(sales)


def test_inventory_builds_stable_snapshot_id_and_value() -> None:
    inventory = pd.DataFrame(
        {
            "snapshot_date": ["2026-11-06"],
            "product_id": ["P-01"],
            "region_id": ["R-01"],
            "available_quantity": ["14"],
            "reorder_level": ["10"],
            "unit_cost": ["250"],
        }
    )

    result = transform_inventory(inventory)

    assert result.loc[0, "snapshot_id"] == "20261106-P-01-R-01"
    assert result.loc[0, "stock_value"] == 3500


def test_normalize_products_rejects_duplicate_business_keys() -> None:
    products = pd.DataFrame(
        {
            "product_id": ["P-1", "P-1"],
            "product_name": ["Mouse", "Mouse"],
            "category": ["Accessories", "Accessories"],
            "brand": ["Demo", "Demo"],
            "unit_cost": ["10", "10"],
        }
    )

    with pytest.raises(ValueError, match="must be unique"):
        normalize_products(products)


def test_date_dimension_uses_integer_calendar_keys() -> None:
    dates = pd.Series(pd.to_datetime(["2026-11-01", "2026-11-01"]))

    result = build_date_dimension(dates)

    assert len(result) == 1
    assert result.loc[0, "date_key"] == 20261101
    assert result.loc[0, "quarter"] == 4


def test_sample_sources_pass_pipeline_contract() -> None:
    sample_dir = PROJECT_ROOT / "data" / "sample"
    sales = clean_sales(extract_sales(sample_dir))
    products = normalize_products(extract_products(sample_dir))
    customers = normalize_customers(extract_customers(sample_dir))
    regions = normalize_regions(read_source_csv(sample_dir, "regions"))
    inventory = transform_inventory(read_source_csv(sample_dir, "inventory"))

    validate_foreign_keys(sales, "product_id", products["product_id"], "products")
    validate_foreign_keys(sales, "customer_id", customers["customer_id"], "customers")
    validate_foreign_keys(sales, "region_id", regions["region_id"], "regions")
    validate_foreign_keys(inventory, "product_id", products["product_id"], "products")
    validate_foreign_keys(inventory, "region_id", regions["region_id"], "regions")

    assert len(sales) >= 1_000
    assert len(inventory) >= 500


def test_batch_csvs_are_written_to_raw_and_processed_folders(tmp_path: Path) -> None:
    batch_id = "test-batch"
    raw_data = {"sales": pd.DataFrame({"source_sales_id": ["S-1"]})}
    processed_data = {"fact_sales": pd.DataFrame({"sales_amount": [12.5]})}

    output_files = _write_batch_csvs(
        tmp_path,
        batch_id,
        raw_data,
        processed_data,
    )

    raw_path = Path(output_files["raw"]["sales"])
    processed_path = Path(output_files["processed"]["fact_sales"])
    raw_result = pd.read_csv(raw_path)
    processed_result = pd.read_csv(processed_path)
    assert raw_path.parent == tmp_path / "raw"
    assert processed_path.parent == tmp_path / "processed"
    assert raw_result.loc[0, "batch_id"] == batch_id
    assert pd.notna(raw_result.loc[0, "ingested_at_utc"])
    assert processed_result.loc[0, "batch_id"] == batch_id

    next_batch_id = "next-batch"
    _write_batch_csvs(
        tmp_path,
        next_batch_id,
        {"sales": pd.DataFrame({"source_sales_id": ["S-2"]})},
        {"fact_sales": pd.DataFrame({"sales_amount": [20.0]})},
    )
    latest_raw = pd.read_csv(raw_path)
    latest_processed = pd.read_csv(processed_path)
    assert latest_raw.loc[0, "batch_id"] == next_batch_id
    assert latest_raw.loc[0, "source_sales_id"] == "S-2"
    assert latest_processed.loc[0, "batch_id"] == next_batch_id
