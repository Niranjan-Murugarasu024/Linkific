from sqlalchemy import text

from .config import logger


PRODUCT_UPSERT = text("""
    INSERT INTO product_catalog (
        product_id, title, price
    )
    VALUES (
        :product_id, :title, :price
    )
    ON CONFLICT (product_id)
    DO UPDATE SET
        title = EXCLUDED.title,
        price = EXCLUDED.price
""")


SALES_UPSERT = text("""
    INSERT INTO fact_sales (
        order_id,
        customer_id,
        customer_name,
        product_id,
        product_name,
        quantity,
        unit_price,
        total_amount,
        updated_at
    )
    VALUES (
        :order_id,
        :customer_id,
        :customer_name,
        :product_id,
        :product_name,
        :quantity,
        :unit_price,
        :total_amount,
        :updated_at
    )
    ON CONFLICT (order_id)
    DO UPDATE SET
        customer_id = EXCLUDED.customer_id,
        customer_name = EXCLUDED.customer_name,
        product_id = EXCLUDED.product_id,
        product_name = EXCLUDED.product_name,
        quantity = EXCLUDED.quantity,
        unit_price = EXCLUDED.unit_price,
        total_amount = EXCLUDED.total_amount,
        updated_at = EXCLUDED.updated_at
    WHERE fact_sales.updated_at <= EXCLUDED.updated_at
""")


def load_products(connection, products):
    """Upsert product catalog records."""

    records = []

    for row in products.to_dict("records"):
        records.append({
            "product_id": int(row["id"]),
            "title": row["title"],
            "price": row.get("price"),
        })

    if records:
        connection.execute(PRODUCT_UPSERT, records)

    logger.info("Loaded %s products", len(records))


def load_sales(connection, sales):
    """Upsert transformed sales records."""

    if sales.empty:
        logger.info("No sales records to load")
        return

    records = sales.to_dict("records")

    connection.execute(SALES_UPSERT, records)

    logger.info("Loaded %s sales records", len(records))


def get_watermark(connection):
    """Read the previous successful watermark."""

    return connection.execute(
        text("""
            SELECT last_updated_at
            FROM etl_watermarks
            WHERE pipeline_name = 'sales'
        """)
    ).scalar_one_or_none()


def save_watermark(connection, timestamp, full=False):
    """Persist the maximum successfully loaded timestamp."""

    if full:
        connection.execute(
            text("""
                DELETE FROM etl_watermarks
                WHERE pipeline_name = 'sales'
            """)
        )

    connection.execute(
        text("""
            INSERT INTO etl_watermarks (
                pipeline_name,
                last_updated_at
            )
            VALUES ('sales', :timestamp)
            ON CONFLICT (pipeline_name)
            DO UPDATE SET
                last_updated_at = GREATEST(
                    etl_watermarks.last_updated_at,
                    EXCLUDED.last_updated_at
                )
        """),
        {"timestamp": timestamp},
    )