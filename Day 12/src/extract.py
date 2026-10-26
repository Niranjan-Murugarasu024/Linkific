import time

import pandas as pd
import requests
from sqlalchemy import text

from .config import (
    API_URL,
    API_PAGE_SIZE,
    API_MAX_PAGES,
    ROOT,
    logger,
)


def extract_products():
    """Extract paginated product data from REST API."""

    logger.info("Starting product API extraction")

    products = []
    offset = 0

    with requests.Session() as session:

        for page in range(API_MAX_PAGES):
            payload = None

            for attempt in range(3):
                try:
                    response = session.get(
                        API_URL,
                        params={
                            "limit": API_PAGE_SIZE,
                            "skip": offset,
                        },
                        timeout=15,
                    )

                    response.raise_for_status()
                    payload = response.json()
                    break

                except requests.RequestException as exc:
                    logger.warning(
                        "API request failed, attempt %s: %s",
                        attempt + 1,
                        exc,
                    )

                    if attempt == 2:
                        raise

                    time.sleep(2 ** attempt)

            batch = payload.get("products", [])
            products.extend(batch)
            offset += len(batch)

            logger.info(
                "Extracted API page %s: %s products",
                page + 1,
                len(batch),
            )

            if not batch or offset >= payload.get("total", offset):
                break

        else:
            raise RuntimeError(
                "API pagination reached maximum page limit"
            )

    if not products:
        raise ValueError("API returned no products")

    return pd.DataFrame(products)


def extract_sales():
    """Extract sales records from CSV."""

    file_path = ROOT / "data" / "sales.csv"

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    df = pd.read_csv(file_path)

    logger.info("Extracted %s sales records", len(df))
    return df


def extract_customers(connection):
    """Extract customers from PostgreSQL."""

    query = text("""
        SELECT customer_id, customer_name
        FROM customers
    """)

    df = pd.read_sql(query, connection)

    logger.info("Extracted %s customers", len(df))
    return df