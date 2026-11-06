"""Load staging frames and upsert warehouse dimensions and fact tables."""

from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _stage_frame(
    connection: Connection,
    table_name: str,
    frame: pd.DataFrame,
) -> None:
    frame.to_sql(
        table_name,
        connection,
        schema="staging",
        if_exists="replace",
        index=False,
        chunksize=1000,
        method="multi",
    )


def _execute_sql_file(connection: Connection, file_name: str) -> None:
    sql_path = PROJECT_ROOT / "sql" / file_name
    if not sql_path.is_file():
        raise FileNotFoundError(f"Warehouse SQL file was not found: {sql_path}")
    statements = [
        statement.strip()
        for statement in sql_path.read_text(encoding="utf-8").split(";")
        if statement.strip()
    ]
    for statement in statements:
        connection.execute(text(statement))


def load_dimensions(connection: Connection, transformed_data: dict) -> None:
    """Stage normalized dimensions and upsert their warehouse rows."""
    for table_name in ("dates", "products", "customers", "regions"):
        _stage_frame(connection, table_name, transformed_data[table_name])
    _execute_sql_file(connection, "dimensions.sql")


def load_facts(connection: Connection, transformed_data: dict) -> None:
    """Stage transformed facts and idempotently upsert sales and inventory."""
    _stage_frame(connection, "sales", transformed_data["sales"])
    _stage_frame(connection, "inventory", transformed_data["inventory"])
    _execute_sql_file(connection, "facts.sql")


def run_quality_checks(connection: Connection) -> list[dict]:
    """Run warehouse-level checks and fail if any violations are found."""
    sql_path = PROJECT_ROOT / "sql" / "quality_checks.sql"
    if not sql_path.is_file():
        raise FileNotFoundError(f"Quality SQL file was not found: {sql_path}")
    result = connection.execute(text(sql_path.read_text(encoding="utf-8")))
    checks = [dict(row) for row in result.mappings()]
    failed_checks = [check for check in checks if check["violations"]]
    if failed_checks:
        details = ", ".join(
            f"{check['check_name']}: {check['violations']}"
            for check in failed_checks
        )
        raise ValueError(f"Warehouse quality checks failed: {details}")
    return checks
