"""Normalize dimension source data and build the warehouse date dimension."""

import pandas as pd

from src.validation.data_quality import validate_no_nulls, validate_required_columns


def normalize_products(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize the product dimension source."""
    columns = ["product_id", "product_name", "category", "brand", "unit_cost"]
    validate_required_columns(df, columns)
    result = df.loc[:, columns].copy()
    for column in columns[:4]:
        result[column] = result[column].astype("string").str.strip()
    result["unit_cost"] = pd.to_numeric(result["unit_cost"], errors="coerce")
    validate_no_nulls(result, ["product_id", "product_name", "unit_cost"])
    result["unit_cost"] = result["unit_cost"].round(2)
    if result[["product_id", "product_name"]].eq("").any().any():
        raise ValueError("Product IDs and names must not be empty.")
    if result["unit_cost"].lt(0).any():
        raise ValueError("Product unit_cost must not be negative.")
    if result["product_id"].duplicated().any():
        raise ValueError("Product product_id values must be unique.")
    return result


def normalize_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize the customer dimension source."""
    columns = ["customer_id", "customer_name", "city", "segment"]
    validate_required_columns(df, columns)
    result = df.loc[:, columns].copy()
    for column in columns:
        result[column] = result[column].astype("string").str.strip()
    validate_no_nulls(result, ["customer_id"])
    if result["customer_id"].eq("").any():
        raise ValueError("Customer IDs must not be empty.")
    if result["customer_id"].duplicated().any():
        raise ValueError("Customer customer_id values must be unique.")
    return result


def normalize_regions(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize the region dimension source."""
    columns = ["region_id", "region_name", "state", "country"]
    validate_required_columns(df, columns)
    result = df.loc[:, columns].copy()
    for column in columns:
        result[column] = result[column].astype("string").str.strip()
    validate_no_nulls(result, ["region_id", "region_name"])
    if result[["region_id", "region_name"]].eq("").any().any():
        raise ValueError("Region IDs and names must not be empty.")
    if result["region_id"].duplicated().any():
        raise ValueError("Region region_id values must be unique.")
    return result


def build_date_dimension(dates: pd.Series) -> pd.DataFrame:
    """Build unique calendar rows for all dates present in the input facts."""
    normalized_dates = pd.to_datetime(dates, errors="coerce").dropna().dt.normalize()
    unique_dates = (
        pd.Series(normalized_dates.unique()).sort_values().reset_index(drop=True)
    )
    if unique_dates.empty:
        raise ValueError("At least one valid fact date is required.")

    result = pd.DataFrame({"full_date": unique_dates})
    result["date_key"] = result["full_date"].dt.strftime("%Y%m%d").astype("int64")
    result["day_of_month"] = result["full_date"].dt.day
    result["month"] = result["full_date"].dt.month
    result["month_name"] = result["full_date"].dt.strftime("%B")
    result["quarter"] = result["full_date"].dt.quarter
    result["year"] = result["full_date"].dt.year
    return result
