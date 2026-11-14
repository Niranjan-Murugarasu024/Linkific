"""Load Databricks Gold CSV exports into PostgreSQL analytics schema."""
from __future__ import annotations
import argparse
import csv
import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
from src.monitoring.logger import get_logger
from src.monitoring.retry import run_with_retry

logger = get_logger()


def connect():
    load_dotenv()
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "ecommerce_practice"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
        sslmode=os.getenv("PGSSLMODE", "prefer"),
        connect_timeout=10,
    )


def read_csv(path: Path):
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_export(input_dir: Path, connection=None):
    own_connection = connection is None
    conn = connection or run_with_retry(connect, attempts=3)
    try:
        with conn:
            with conn.cursor() as cur:
                # Dimensions are loaded before the fact table.
                dimension_specs = [
                    ("dim_region", ["region_key", "region_id", "region_name", "country"],
                     ["region_key"], ["region_id", "region_name", "country"]),
                    ("dim_customer", ["customer_key", "customer_id", "customer_name", "email", "region_key"],
                     ["customer_key"], ["customer_id", "customer_name", "email", "region_key"]),
                    ("dim_product", ["product_key", "product_id", "product_name", "category", "unit_price"],
                     ["product_key"], ["product_id", "product_name", "category", "unit_price"]),
                    ("dim_date", ["date_key", "full_date", "year", "quarter", "month", "month_name", "day"],
                     ["date_key"], ["full_date", "year", "quarter", "month", "month_name", "day"]),
                ]
                for table, columns, conflict, updates in dimension_specs:
                    rows = read_csv(input_dir / f"{table}.csv")
                    if rows:
                        values = [tuple(row.get(c) if row.get(c) != "" else None for c in columns) for row in rows]
                        update_sql = ", ".join(f"{c}=EXCLUDED.{c}" for c in updates)
                        sql = (
                            f"INSERT INTO analytics.{table} ({','.join(columns)}) VALUES %s "
                            f"ON CONFLICT ({','.join(conflict)}) DO UPDATE SET {update_sql}"
                        )
                        execute_values(cur, sql, values, page_size=1000)
                    logger.info("Loaded %s rows into %s", len(rows), table)

                fact_columns = [
                    "order_id", "line_id", "customer_key", "product_key", "region_key",
                    "date_key", "quantity", "unit_price", "discount_pct", "gross_amount",
                    "discount_amount", "net_amount", "status", "updated_at"
                ]
                fact_rows = read_csv(input_dir / "fact_sales.csv")
                # Gold export is a current-state snapshot: delete rows absent from it,
                # then upsert the complete current set so CDC deletes propagate.
                cur.execute("CREATE TEMP TABLE incoming_fact_sales (LIKE analytics.fact_sales INCLUDING DEFAULTS) ON COMMIT DROP")
                if fact_rows:
                    values = [tuple(row.get(c) if row.get(c) != "" else None for c in fact_columns) for row in fact_rows]
                    insert_sql = (
                        f"INSERT INTO incoming_fact_sales ({','.join(fact_columns)}) VALUES %s"
                    )
                    execute_values(cur, insert_sql, values, page_size=1000)
                cur.execute("""
                    DELETE FROM analytics.fact_sales target
                    WHERE NOT EXISTS (
                        SELECT 1 FROM incoming_fact_sales incoming
                        WHERE incoming.order_id = target.order_id
                          AND incoming.line_id = target.line_id
                    )
                """)
                cur.execute(f"""
                    INSERT INTO analytics.fact_sales ({','.join(fact_columns)})
                    SELECT {','.join(fact_columns)} FROM incoming_fact_sales
                    ON CONFLICT (order_id, line_id) DO UPDATE SET
                      customer_key=EXCLUDED.customer_key,
                      product_key=EXCLUDED.product_key,
                      region_key=EXCLUDED.region_key,
                      date_key=EXCLUDED.date_key,
                      quantity=EXCLUDED.quantity,
                      unit_price=EXCLUDED.unit_price,
                      discount_pct=EXCLUDED.discount_pct,
                      gross_amount=EXCLUDED.gross_amount,
                      discount_amount=EXCLUDED.discount_amount,
                      net_amount=EXCLUDED.net_amount,
                      status=EXCLUDED.status,
                      updated_at=EXCLUDED.updated_at
                """)
                logger.info("Synchronized %s fact rows", len(fact_rows))
                cur.execute("""
                    INSERT INTO analytics.pipeline_audit
                    (pipeline_name, status, records_processed, message)
                    VALUES (%s, %s, %s, %s)
                """, ("day24_gold_to_postgres", "SUCCESS", len(fact_rows), "Gold snapshot synchronized"))
        return len(fact_rows)
    except Exception:
        logger.exception("PostgreSQL Gold load failed; transaction rolled back")
        raise
    finally:
        if own_connection:
            conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("data/gold_export"))
    args = parser.parse_args()
    count = load_export(args.input_dir)
    print(f"Successfully synchronized {count:,} fact rows.")
