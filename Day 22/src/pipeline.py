"""Command-line entry point for the e-commerce batch ETL pipeline."""

import argparse
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

from src.ingestion.common import read_source_csv
from src.ingestion.extract_customers import extract_customers
from src.ingestion.extract_products import extract_products
from src.ingestion.extract_sales import extract_sales
from src.transformation.clean_sales import clean_sales
from src.transformation.transform_dimensions import (
    build_date_dimension,
    normalize_customers,
    normalize_products,
    normalize_regions,
)
from src.transformation.transform_inventory import transform_inventory
from src.validation.data_quality import validate_foreign_keys, validate_unique
from src.warehouse.load_warehouse import (
    load_dimensions,
    load_facts,
    run_quality_checks,
)

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _resolve_path(configured_path: str, project_root: Path) -> Path:
    path = Path(configured_path)
    return path if path.is_absolute() else project_root / path


def _write_batch_csvs(
    data_root: Path,
    batch_id: str,
    raw_data: dict[str, pd.DataFrame],
    processed_data: dict[str, pd.DataFrame] | None = None,
) -> dict[str, dict[str, str]]:
    """Write latest raw and processed CSV snapshots using stable file names."""
    batch_root = Path(data_root)
    output_files = {"raw": {}, "processed": {}}
    if raw_data:
        raw_dir = batch_root / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        ingestion_time = datetime.now(timezone.utc).isoformat()
        for name, frame in raw_data.items():
            raw_frame = frame.copy()
            raw_frame.insert(0, "batch_id", batch_id)
            raw_frame.insert(1, "ingested_at_utc", ingestion_time)
            output_path = raw_dir / f"{name}.csv"
            raw_frame.to_csv(output_path, index=False)
            output_files["raw"][name] = str(output_path)

    if processed_data is not None:
        processed_dir = batch_root / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        for name, frame in processed_data.items():
            processed_frame = frame.copy()
            processed_frame.insert(0, "batch_id", batch_id)
            output_path = processed_dir / f"{name}.csv"
            processed_frame.to_csv(output_path, index=False)
            output_files["processed"][name] = str(output_path)

    return output_files


def extract_batch(
    data_dir: str | Path | None = None,
    project_root: str | Path = PROJECT_ROOT,
    batch_id: str | None = None,
) -> dict:
    """Extract all source CSVs and persist an immutable raw batch."""
    root = Path(project_root).resolve()
    load_dotenv(root / ".env")
    configured_data_dir = data_dir or os.getenv("DATA_DIR", "data/sample")
    source_dir = _resolve_path(str(configured_data_dir), root)
    batch_id = batch_id or str(uuid4())

    raw_data = {
        "sales": extract_sales(source_dir),
        "products": extract_products(source_dir),
        "customers": extract_customers(source_dir),
        "regions": read_source_csv(source_dir, "regions"),
        "inventory": read_source_csv(source_dir, "inventory"),
    }
    _write_batch_csvs(root / "data", batch_id, raw_data)
    row_counts = {name: len(frame) for name, frame in raw_data.items()}
    LOGGER.info(
        "Extracted batch %s from %s with row counts %s",
        batch_id,
        source_dir,
        row_counts,
    )
    return {"batch_id": batch_id, "rows": row_counts}


def _read_batch_files(
    directory: Path,
    names: tuple[str, ...],
    batch_id: str,
) -> dict[str, pd.DataFrame]:
    """Read the latest flat CSVs and ensure they belong to the requested batch."""
    if not directory.is_dir():
        raise FileNotFoundError(f"Data directory was not found: {directory}")
    frames = {}
    for name in names:
        path = directory / f"{name}.csv"
        if not path.is_file():
            raise FileNotFoundError(f"Data file was not found: {path}")
        frame = pd.read_csv(path)
        if "batch_id" not in frame.columns:
            raise ValueError(f"Batch metadata is missing from {path}.")
        observed_batch_ids = set(frame["batch_id"].dropna().astype(str))
        if observed_batch_ids != {batch_id}:
            raise RuntimeError(
                f"Expected batch {batch_id} in {path}, found "
                f"{sorted(observed_batch_ids)}. Another run may have replaced "
                "the latest-only output."
            )
        frames[name] = frame.drop(
            columns=["batch_id", "ingested_at_utc"],
            errors="ignore",
        )
    return frames


def transform_batch(
    batch_id: str,
    project_root: str | Path = PROJECT_ROOT,
) -> dict:
    """Validate a saved raw batch, transform it, and persist processed CSVs."""
    root = Path(project_root).resolve()
    raw_data = _read_batch_files(
        root / "data" / "raw",
        ("sales", "products", "customers", "regions", "inventory"),
        batch_id,
    )
    sales = clean_sales(raw_data["sales"])
    products = normalize_products(raw_data["products"])
    customers = normalize_customers(raw_data["customers"])
    regions = normalize_regions(raw_data["regions"])
    inventory = transform_inventory(raw_data["inventory"])

    validate_unique(sales, ["source_sales_id"])
    validate_unique(inventory, ["snapshot_id"])
    validate_foreign_keys(sales, "product_id", products["product_id"], "products")
    validate_foreign_keys(sales, "customer_id", customers["customer_id"], "customers")
    validate_foreign_keys(sales, "region_id", regions["region_id"], "regions")
    validate_foreign_keys(inventory, "product_id", products["product_id"], "products")
    validate_foreign_keys(inventory, "region_id", regions["region_id"], "regions")

    dates = build_date_dimension(
        pd.concat(
            [sales["order_date"], inventory["snapshot_date"]],
            ignore_index=True,
        )
    )
    sales["date_key"] = sales["order_date"].dt.strftime("%Y%m%d").astype("int64")
    inventory["date_key"] = (
        inventory["snapshot_date"].dt.strftime("%Y%m%d").astype("int64")
    )
    processed_data = {
        "dim_date": dates,
        "dim_products": products,
        "dim_customers": customers,
        "dim_regions": regions,
        "fact_sales": sales,
        "fact_inventory": inventory,
    }
    output_files = _write_batch_csvs(
        root / "data",
        batch_id,
        {},
        processed_data,
    )["processed"]
    row_counts = {
        "sales": len(sales),
        "products": len(products),
        "customers": len(customers),
        "regions": len(regions),
        "inventory": len(inventory),
    }
    LOGGER.info(
        "Validated and transformed batch %s with row counts %s",
        batch_id,
        row_counts,
    )
    return {
        "batch_id": batch_id,
        "rows": row_counts,
        "output_files": output_files,
    }


def _read_processed_batch(
    batch_id: str,
    project_root: str | Path,
) -> dict[str, pd.DataFrame]:
    """Read the typed dimension and fact frames for a persisted batch."""
    root = Path(project_root).resolve()
    batch_dir = root / "data" / "processed"
    names = {
        "dates": "dim_date",
        "products": "dim_products",
        "customers": "dim_customers",
        "regions": "dim_regions",
        "sales": "fact_sales",
        "inventory": "fact_inventory",
    }
    frames = {}
    for key, file_name in names.items():
        path = batch_dir / f"{file_name}.csv"
        if not path.is_file():
            raise FileNotFoundError(f"Processed data file was not found: {path}")
        frame = pd.read_csv(path, parse_dates=["full_date"] if key == "dates" else [])
        if "batch_id" not in frame.columns:
            raise ValueError(f"Batch metadata is missing from {path}.")
        observed_batch_ids = set(frame["batch_id"].dropna().astype(str))
        if observed_batch_ids != {batch_id}:
            raise RuntimeError(
                f"Expected batch {batch_id} in {path}, found "
                f"{sorted(observed_batch_ids)}. Another run may have replaced "
                "the latest-only output."
            )
        frames[key] = frame.drop(columns=["batch_id"], errors="ignore")

    for column in ("order_date",):
        frames["sales"][column] = pd.to_datetime(
            frames["sales"][column], errors="raise"
        )
    frames["inventory"]["snapshot_date"] = pd.to_datetime(
        frames["inventory"]["snapshot_date"], errors="raise"
    )
    return frames


def _connection_url(database_url: str | None, project_root: str | Path) -> str:
    """Resolve the database URL from an argument or the project environment."""
    root = Path(project_root).resolve()
    load_dotenv(root / ".env")
    resolved_url = database_url or os.getenv("DATABASE_URL")
    if not resolved_url:
        raise ValueError(
            "DATABASE_URL is not configured. Set it in .env or the environment."
        )
    return resolved_url


def load_dimension_batch(
    batch_id: str,
    database_url: str | None = None,
    project_root: str | Path = PROJECT_ROOT,
) -> dict:
    """Load date, product, customer, and region dimensions for one batch."""
    frames = _read_processed_batch(batch_id, project_root)
    engine = create_engine(_connection_url(database_url, project_root), pool_pre_ping=True)
    try:
        with engine.begin() as connection:
            load_dimensions(connection, frames)
    finally:
        engine.dispose()
    LOGGER.info("Loaded dimensions for batch %s", batch_id)
    return {"batch_id": batch_id, "status": "dimensions_loaded"}


def load_fact_batch(
    batch_id: str,
    database_url: str | None = None,
    project_root: str | Path = PROJECT_ROOT,
) -> dict:
    """Load sales and inventory facts after their dimensions are available."""
    frames = _read_processed_batch(batch_id, project_root)
    engine = create_engine(_connection_url(database_url, project_root), pool_pre_ping=True)
    try:
        with engine.begin() as connection:
            load_facts(connection, frames)
    finally:
        engine.dispose()
    LOGGER.info("Loaded facts for batch %s", batch_id)
    return {"batch_id": batch_id, "status": "facts_loaded"}


def run_warehouse_quality_checks(
    database_url: str | None = None,
    project_root: str | Path = PROJECT_ROOT,
) -> list[dict]:
    """Run warehouse-level quality checks in a read-only transaction."""
    engine = create_engine(_connection_url(database_url, project_root), pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            checks = run_quality_checks(connection)
    finally:
        engine.dispose()
    LOGGER.info("Warehouse quality checks passed: %s", checks)
    return checks


def run_pipeline(
    data_dir: str | Path | None = None,
    database_url: str | None = None,
    project_root: str | Path = PROJECT_ROOT,
) -> dict:
    """Extract CSVs, validate and transform data, then load PostgreSQL."""
    root = Path(project_root).resolve()
    connection_url = _connection_url(database_url, root)
    extraction = extract_batch(data_dir, root)
    transformation = transform_batch(extraction["batch_id"], root)
    load_dimension_batch(extraction["batch_id"], connection_url, root)
    load_fact_batch(extraction["batch_id"], connection_url, root)
    quality_checks = run_warehouse_quality_checks(connection_url, root)

    result = {
        "batch_id": extraction["batch_id"],
        "rows": transformation["rows"],
        "quality_checks": quality_checks,
        "output_files": {
            "raw": {
                name: str(root / "data" / "raw" / f"{name}.csv")
                for name in extraction["rows"]
            },
            "processed": transformation["output_files"],
        },
    }
    LOGGER.info(
        "ETL batch %s completed: %s",
        extraction["batch_id"],
        result["rows"],
    )
    return result


def main() -> None:
    """Parse command-line options and run one ETL batch."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        help=(
            "Directory containing sales, products, customers, regions, "
            "and inventory CSVs."
        ),
    )
    parser.add_argument(
        "--database-url",
        help="SQLAlchemy PostgreSQL URL; defaults to DATABASE_URL from .env.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    result = run_pipeline(data_dir=args.data_dir, database_url=args.database_url)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
