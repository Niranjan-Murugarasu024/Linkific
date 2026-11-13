from __future__ import annotations

from datetime import date

from warehouse.transformations import customer_record_hash


def load_region_dimension(connection) -> int:
    sql = """
        INSERT INTO dw.dim_region (region_code, region_name, country, is_active)
        SELECT region_code, region_name, country, TRUE
        FROM source.regions
        ON CONFLICT (region_code) DO UPDATE SET
            region_name = EXCLUDED.region_name,
            country = EXCLUDED.country,
            is_active = TRUE
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        count = cursor.rowcount
    connection.commit()
    return count


def load_product_dimension(connection) -> int:
    sql = """
        INSERT INTO dw.dim_product (
            product_id, sku, product_name, category, brand,
            unit_cost, list_price, is_active, source_updated_at
        )
        SELECT product_id, sku, product_name, category, brand,
               unit_cost, list_price, is_active, updated_at
        FROM source.products
        ON CONFLICT (product_id) DO UPDATE SET
            sku = EXCLUDED.sku,
            product_name = EXCLUDED.product_name,
            category = EXCLUDED.category,
            brand = EXCLUDED.brand,
            unit_cost = EXCLUDED.unit_cost,
            list_price = EXCLUDED.list_price,
            is_active = EXCLUDED.is_active,
            source_updated_at = EXCLUDED.source_updated_at
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        count = cursor.rowcount
    connection.commit()
    return count


def load_customer_dimension_scd2(connection) -> dict[str, int]:
    """Load customer history using SCD Type 2 with an exclusive end-date convention."""
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT customer_id, full_name, email, city, state, country,
                      region_code, segment, updated_at
               FROM source.customers ORDER BY customer_id"""
        )
        source_rows = cursor.fetchall()
        cursor.execute("SELECT region_code FROM dw.dim_region")
        region_codes = {row[0] for row in cursor.fetchall()}

    inserted = 0
    expired = 0
    unchanged = 0
    for row in source_rows:
        customer = {
            "customer_id": row[0], "full_name": row[1], "email": row[2],
            "city": row[3], "state": row[4], "country": row[5],
            "region_code": row[6], "segment": row[7], "updated_at": row[8],
        }
        if customer["region_code"] not in region_codes:
            raise ValueError(f"Customer {customer['customer_id']} has unknown region {customer['region_code']}")
        record_hash = customer_record_hash(customer)
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT customer_key, record_hash, valid_from
                   FROM dw.dim_customer
                   WHERE customer_id = %s AND is_current = TRUE
                   FOR UPDATE""",
                (customer["customer_id"],),
            )
            current = cursor.fetchone()
            if current and current[1] == record_hash:
                unchanged += 1
                continue

            effective_date = customer["updated_at"]
            if current:
                old_valid_from = current[2]
                if effective_date <= old_valid_from:
                    raise ValueError(
                        f"SCD2 effective date for customer {customer['customer_id']} "
                        f"({effective_date}) must be after the current version start ({old_valid_from}). "
                        "Correct source.customers.updated_at before re-running."
                    )
                cursor.execute(
                    """UPDATE dw.dim_customer
                       SET valid_to = %s, is_current = FALSE
                       WHERE customer_key = %s""",
                    (effective_date.fromordinal(effective_date.toordinal() - 1), current[0]),
                )
                expired += cursor.rowcount

            cursor.execute(
                """INSERT INTO dw.dim_customer (
                       customer_id, full_name, email, city, state, country,
                       region_code, segment, record_hash, source_updated_at,
                       valid_from, valid_to, is_current
                   ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, DATE '9999-12-31', TRUE)""",
                (
                    customer["customer_id"], customer["full_name"], customer["email"],
                    customer["city"], customer["state"], customer["country"],
                    customer["region_code"], customer["segment"], record_hash,
                    customer["updated_at"], effective_date,
                ),
            )
            inserted += cursor.rowcount
        connection.commit()
    return {"inserted_versions": inserted, "expired_versions": expired, "unchanged": unchanged}


def load_date_dimension(connection) -> int:
    """Generate a date range one year wider than the source order dates."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT MIN(order_date), MAX(order_date) FROM source.orders")
        bounds = cursor.fetchone()
        if not bounds or bounds[0] is None:
            raise ValueError("source.orders is empty; load source data before the date dimension")
        start_date = date(bounds[0].year - 1, 1, 1)
        end_date = date(bounds[1].year + 1, 12, 31)
        cursor.execute(
            """WITH calendar AS (
                   SELECT gs.generated::date AS d
                   FROM generate_series(%s::date, %s::date, INTERVAL '1 day') AS gs(generated)
               ), holiday_rollup AS (
                   SELECT holiday_date,
                          STRING_AGG(DISTINCT holiday_name, ', ' ORDER BY holiday_name) AS holiday_name,
                          STRING_AGG(DISTINCT country_code, ', ' ORDER BY country_code) AS country_codes
                   FROM source.holidays GROUP BY holiday_date
               )
               INSERT INTO dw.dim_date (
                   date_key, full_date, day_of_month, day_name, iso_day_of_week,
                   week_of_year, month_number, month_name, quarter_number,
                   quarter_label, year_number, fiscal_year, fiscal_quarter,
                   is_weekend, is_month_start, is_month_end, is_holiday,
                   holiday_name, holiday_country_codes
               )
               SELECT
                   TO_CHAR(c.d, 'YYYYMMDD')::INTEGER,
                   c.d,
                   EXTRACT(DAY FROM c.d)::SMALLINT,
                   TO_CHAR(c.d, 'FMDay'),
                   EXTRACT(ISODOW FROM c.d)::SMALLINT,
                   EXTRACT(WEEK FROM c.d)::SMALLINT,
                   EXTRACT(MONTH FROM c.d)::SMALLINT,
                   TO_CHAR(c.d, 'FMMonth'),
                   EXTRACT(QUARTER FROM c.d)::SMALLINT,
                   'Q' || EXTRACT(QUARTER FROM c.d)::TEXT,
                   EXTRACT(YEAR FROM c.d)::SMALLINT,
                   (EXTRACT(YEAR FROM c.d) + CASE WHEN EXTRACT(MONTH FROM c.d) >= 4 THEN 1 ELSE 0 END)::SMALLINT,
                   (CASE
                       WHEN EXTRACT(MONTH FROM c.d) BETWEEN 4 AND 6 THEN 1
                       WHEN EXTRACT(MONTH FROM c.d) BETWEEN 7 AND 9 THEN 2
                       WHEN EXTRACT(MONTH FROM c.d) BETWEEN 10 AND 12 THEN 3
                       ELSE 4
                    END)::SMALLINT,
                   EXTRACT(ISODOW FROM c.d) IN (6, 7),
                   c.d = DATE_TRUNC('month', c.d)::date,
                   c.d = (DATE_TRUNC('month', c.d) + INTERVAL '1 month' - INTERVAL '1 day')::date,
                   h.holiday_date IS NOT NULL,
                   h.holiday_name,
                   h.country_codes
               FROM calendar c
               LEFT JOIN holiday_rollup h ON h.holiday_date = c.d
               ON CONFLICT (date_key) DO UPDATE SET
                   is_holiday = EXCLUDED.is_holiday,
                   holiday_name = EXCLUDED.holiday_name,
                   holiday_country_codes = EXCLUDED.holiday_country_codes""",
            (start_date, end_date),
        )
        count = cursor.rowcount
    connection.commit()
    return count


def load_all_dimensions(connection) -> dict:
    results = {
        "regions_upserted": load_region_dimension(connection),
        "products_upserted": load_product_dimension(connection),
        "customers_scd2": load_customer_dimension_scd2(connection),
        "date_rows_inserted_or_refreshed": load_date_dimension(connection),
    }
    return results
