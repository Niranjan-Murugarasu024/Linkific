"""Standardize inventory snapshots and calculate their cost value."""

import pandas as pd

from src.validation.data_quality import validate_no_nulls, validate_required_columns

INVENTORY_COLUMNS = [
    "snapshot_date",
    "product_id",
    "region_id",
    "available_quantity",
    "reorder_level",
    "unit_cost",
]


def transform_inventory(df: pd.DataFrame) -> pd.DataFrame:
    """Validate inventory snapshots and calculate quantity times unit cost."""
    validate_required_columns(df, INVENTORY_COLUMNS)
    transformed = df.loc[:, INVENTORY_COLUMNS].copy()
    for column in ("product_id", "region_id"):
        transformed[column] = transformed[column].astype("string").str.strip()
    transformed["snapshot_date"] = pd.to_datetime(
        transformed["snapshot_date"], errors="coerce"
    )
    for column in ("available_quantity", "reorder_level", "unit_cost"):
        transformed[column] = pd.to_numeric(transformed[column], errors="coerce")

    validate_no_nulls(transformed, INVENTORY_COLUMNS)
    transformed["unit_cost"] = transformed["unit_cost"].round(2)
    if transformed[["product_id", "region_id"]].eq("").any().any():
        raise ValueError("Inventory product_id and region_id must not be empty.")
    if transformed["available_quantity"].lt(0).any():
        raise ValueError("Inventory available_quantity must not be negative.")
    if transformed["reorder_level"].lt(0).any():
        raise ValueError("Inventory reorder_level must not be negative.")
    if (
        transformed[["available_quantity", "reorder_level"]]
        .mod(1)
        .ne(0)
        .any()
        .any()
    ):
        raise ValueError("Inventory quantities and reorder levels must be whole numbers.")
    if transformed["unit_cost"].lt(0).any():
        raise ValueError("Inventory unit_cost must not be negative.")

    transformed["available_quantity"] = transformed[
        "available_quantity"
    ].astype("int64")
    transformed["reorder_level"] = transformed["reorder_level"].astype("int64")
    transformed["stock_value"] = (
        transformed["available_quantity"] * transformed["unit_cost"]
    ).round(2)
    transformed["snapshot_id"] = (
        transformed["snapshot_date"].dt.strftime("%Y%m%d")
        + "-"
        + transformed["product_id"]
        + "-"
        + transformed["region_id"]
    )
    return transformed