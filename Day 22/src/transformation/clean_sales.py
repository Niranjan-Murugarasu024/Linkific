"""Standardize sales records and derive net line sales."""

import pandas as pd

from src.validation.data_quality import validate_no_nulls, validate_required_columns

SALES_COLUMNS = [
    "source_sales_id",
    "order_date",
    "product_id",
    "customer_id",
    "region_id",
    "quantity",
    "unit_price",
    "discount_amount",
]


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize sales, treating discount as a line-level amount."""
    validate_required_columns(df, SALES_COLUMNS)
    cleaned = df.loc[:, SALES_COLUMNS].copy()
    string_columns = [
        "source_sales_id",
        "product_id",
        "customer_id",
        "region_id",
    ]
    for column in string_columns:
        cleaned[column] = cleaned[column].astype("string").str.strip()

    cleaned["order_date"] = pd.to_datetime(cleaned["order_date"], errors="coerce")
    for column in ("quantity", "unit_price", "discount_amount"):
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    validate_no_nulls(cleaned, SALES_COLUMNS)
    cleaned["unit_price"] = cleaned["unit_price"].round(2)
    cleaned["discount_amount"] = cleaned["discount_amount"].round(2)
    if cleaned["source_sales_id"].eq("").any():
        raise ValueError("Sales source_sales_id values must not be empty.")
    if cleaned["quantity"].le(0).any():
        raise ValueError("Sales quantity values must be greater than zero.")
    if cleaned["quantity"].mod(1).ne(0).any():
        raise ValueError("Sales quantity values must be whole numbers.")
    if cleaned["unit_price"].lt(0).any():
        raise ValueError("Sales unit_price values must not be negative.")
    if cleaned["discount_amount"].lt(0).any():
        raise ValueError("Sales discount_amount values must not be negative.")

    gross_sales = cleaned["quantity"] * cleaned["unit_price"]
    if cleaned["discount_amount"].gt(gross_sales).any():
        raise ValueError("A sales discount cannot exceed its gross line amount.")

    cleaned["sales_amount"] = (gross_sales - cleaned["discount_amount"]).round(2)
    cleaned["quantity"] = cleaned["quantity"].astype("int64")
    return cleaned