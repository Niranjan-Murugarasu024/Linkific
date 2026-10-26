import argparse
import traceback

from sqlalchemy import create_engine, text

from .alerts import send_failure_alert
from .config import DATABASE_URL, ROOT, logger
from .extract import (
    extract_products,
    extract_sales,
    extract_customers,
)
from .transform import transform_sales
from .load import (
    load_products,
    load_sales,
    get_watermark,
    save_watermark,
)


def initialize_database(engine):
    """Create required PostgreSQL tables."""

    schema_path = ROOT / "sql" / "schema.sql"
    schema = schema_path.read_text(encoding="utf-8")

    with engine.begin() as connection:
        for statement in schema.split(";"):
            if statement.strip():
                connection.execute(text(statement))

    logger.info("Database schema initialized")


def create_run(engine, load_type):
    """Create a pipeline execution record."""

    with engine.begin() as connection:
        return connection.execute(
            text("""
                INSERT INTO etl_runs (
                    pipeline_name,
                    load_type,
                    status
                )
                VALUES (
                    'sales',
                    :load_type,
                    'RUNNING'
                )
                RETURNING run_id
            """),
            {"load_type": load_type},
        ).scalar_one()


def update_run(
    engine,
    run_id,
    status,
    records_processed=0,
    error_message=None,
):
    """Update execution status."""

    with engine.begin() as connection:
        connection.execute(
            text("""
                UPDATE etl_runs
                SET
                    status = :status,
                    records_processed = :records,
                    finished_at = NOW(),
                    error_message = :error
                WHERE run_id = :run_id
            """),
            {
                "status": status,
                "records": records_processed,
                "error": error_message,
                "run_id": run_id,
            },
        )


def run(full=False):
    """Execute the complete ETL workflow."""

    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL is missing from .env"
        )

    load_type = "FULL" if full else "INCREMENTAL"

    logger.info("Starting %s ETL pipeline", load_type)

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )

    run_id = None

    try:
        initialize_database(engine)

        run_id = create_run(engine, load_type)

        products = extract_products()
        sales = extract_sales()

        with engine.begin() as connection:
            customers = extract_customers(connection)

        transformed = transform_sales(
            sales,
            customers,
            products,
        )

        # Keep warehouse changes and watermark
        # updates in one transaction.
        with engine.begin() as connection:

            # Serialize pipeline runs through a
            # PostgreSQL transaction-level advisory lock.
            connection.execute(
                text("SELECT pg_advisory_xact_lock(120012)")
            )

            watermark = None

            if full:
                connection.execute(
                    text("DELETE FROM fact_sales")
                )
            else:
                watermark = get_watermark(connection)

                if watermark is not None:
                    transformed = transformed[
                        transformed["updated_at"] >= watermark
                    ].copy()

            load_products(connection, products)
            load_sales(connection, transformed)

            if not transformed.empty:
                latest_timestamp = (
                    transformed["updated_at"]
                    .max()
                    .to_pydatetime()
                )

                save_watermark(
                    connection,
                    latest_timestamp,
                    full=full,
                )

            elif full:
                connection.execute(
                    text("""
                        DELETE FROM etl_watermarks
                        WHERE pipeline_name = 'sales'
                    """)
                )

        processed = len(transformed)

        update_run(
            engine,
            run_id,
            "SUCCESS",
            records_processed=processed,
        )

        logger.info(
            "ETL completed successfully: %s rows",
            processed,
        )

    except Exception as exc:
        logger.exception("ETL pipeline failed")

        if run_id is not None:
            try:
                update_run(
                    engine,
                    run_id,
                    "FAILED",
                    error_message=str(exc)[:2000],
                )
            except Exception:
                logger.exception(
                    "Failed to update ETL run status"
                )

        send_failure_alert(traceback.format_exc())
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="E-Commerce ETL Pipeline"
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Perform full warehouse refresh",
    )

    args = parser.parse_args()

    run(full=args.full)