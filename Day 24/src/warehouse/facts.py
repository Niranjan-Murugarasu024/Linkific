from __future__ import annotations


def load_sales_fact(connection) -> int:
    """Load one fact row per source order line; safe to re-run (upsert by source key)."""
    sql = """
        INSERT INTO dw.fact_sales (
            source_order_item_id, order_id, date_key, customer_key,
            product_key, region_key, order_status, quantity, unit_price,
            discount_pct, gross_sales, discount_amount, net_sales,
            unit_cost, total_cost, profit
        )
        SELECT
            oi.order_item_id,
            o.order_id,
            d.date_key,
            c.customer_key,
            p.product_key,
            r.region_key,
            o.order_status,
            oi.quantity,
            oi.unit_price,
            oi.discount_pct,
            ROUND(oi.quantity * oi.unit_price, 2),
            ROUND(oi.quantity * oi.unit_price * oi.discount_pct, 2),
            ROUND(oi.quantity * oi.unit_price, 2)
                - ROUND(oi.quantity * oi.unit_price * oi.discount_pct, 2),
            p.unit_cost,
            ROUND(oi.quantity * p.unit_cost, 2),
            ROUND(oi.quantity * oi.unit_price, 2)
                - ROUND(oi.quantity * oi.unit_price * oi.discount_pct, 2)
                - ROUND(oi.quantity * p.unit_cost, 2)
        FROM source.order_items oi
        JOIN source.orders o ON o.order_id = oi.order_id
        JOIN dw.dim_customer c
          ON c.customer_id = o.customer_id
         AND o.order_date BETWEEN c.valid_from AND c.valid_to
        JOIN dw.dim_product p ON p.product_id = oi.product_id
        JOIN dw.dim_region r ON r.region_code = c.region_code
        JOIN dw.dim_date d ON d.full_date = o.order_date
        ON CONFLICT (source_order_item_id) DO UPDATE SET
            order_id = EXCLUDED.order_id,
            date_key = EXCLUDED.date_key,
            customer_key = EXCLUDED.customer_key,
            product_key = EXCLUDED.product_key,
            region_key = EXCLUDED.region_key,
            order_status = EXCLUDED.order_status,
            quantity = EXCLUDED.quantity,
            unit_price = EXCLUDED.unit_price,
            discount_pct = EXCLUDED.discount_pct,
            gross_sales = EXCLUDED.gross_sales,
            discount_amount = EXCLUDED.discount_amount,
            net_sales = EXCLUDED.net_sales,
            unit_cost = EXCLUDED.unit_cost,
            total_cost = EXCLUDED.total_cost,
            profit = EXCLUDED.profit,
            loaded_at = CURRENT_TIMESTAMP
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        loaded = cursor.rowcount
        cursor.execute("SELECT COUNT(*) FROM source.order_items")
        source_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM dw.fact_sales")
        target_count = cursor.fetchone()[0]
    if source_count != target_count:
        connection.rollback()
        raise RuntimeError(
            f"Fact load row-count mismatch: source has {source_count}, warehouse has {target_count}. "
            "The fact insert/upsert was rolled back. Check missing dimension lookups and source referential integrity."
        )
    connection.commit()
    return loaded
