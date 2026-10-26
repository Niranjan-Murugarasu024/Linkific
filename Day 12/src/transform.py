import pandas as pd

from .config import logger


OUTPUT_COLUMNS = [
    "order_id",
    "customer_id",
    "customer_name",
    "product_id",
    "product_name",
    "quantity",
    "unit_price",
    "total_amount",
    "updated_at",
]


def transform_sales(sales, customers, products):
    """Clean and enrich sales transactions."""

    logger.info("Starting sales transformations")

    sales = sales.copy()

    required = [
        "order_id",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
        "updated_at",
    ]

    missing = set(required) - set(sales.columns)

    if missing:
        raise ValueError(f"Missing sales columns: {missing}")

    for column in [
        "order_id",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
    ]:
        sales[column] = pd.to_numeric(
            sales[column],
            errors="coerce",
        )

    sales["updated_at"] = pd.to_datetime(
        sales["updated_at"],
        errors="coerce",
        utc=True,
    ).dt.tz_localize(None)

    original_count = len(sales)

    sales = sales.dropna(subset=required)

    sales = sales[
        (sales["quantity"] > 0)
        & (sales["unit_price"] >= 0)
    ].copy()

    for column in [
        "order_id",
        "customer_id",
        "product_id",
        "quantity",
    ]:
        sales = sales[
            sales[column] % 1 == 0
        ].copy()

        sales[column] = sales[column].astype("int64")

    sales = (
        sales.sort_values("updated_at")
        .drop_duplicates("order_id", keep="last")
    )

    rejected = original_count - len(sales)

    logger.info(
        "Removed %s invalid or duplicate sales rows",
        rejected,
    )

    customers = customers[
        ["customer_id", "customer_name"]
    ].copy()

    if customers["customer_id"].duplicated().any():
        raise ValueError("Duplicate customer IDs detected")

    catalog = products[
        ["id", "title"]
    ].rename(
        columns={
            "id": "product_id",
            "title": "product_name",
        }
    )

    catalog["product_id"] = pd.to_numeric(
        catalog["product_id"],
        errors="coerce",
    )

    catalog = catalog.dropna(subset=["product_id"])
    catalog = catalog.drop_duplicates("product_id")

    catalog["product_id"] = (
        catalog["product_id"].astype("int64")
    )

    result = sales.merge(
        customers,
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    result = result.merge(
        catalog,
        on="product_id",
        how="left",
        validate="many_to_one",
    )

    result["customer_name"] = (
        result["customer_name"].fillna("Unknown")
    )

    result["product_name"] = (
        result["product_name"].fillna("Unknown")
    )

    result["total_amount"] = (
        result["quantity"] * result["unit_price"]
    ).round(2)

    logger.info(
        "Transformation completed: %s rows",
        len(result),
    )

    return result[OUTPUT_COLUMNS]