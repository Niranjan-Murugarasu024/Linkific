import os
import pytest
from pathlib import Path


@pytest.mark.skipif(os.getenv("RUN_POSTGRES_INTEGRATION") != "1",
                    reason="Set RUN_POSTGRES_INTEGRATION=1 to run PostgreSQL integration test")
def test_postgres_export_loader():
    export_dir = Path("data/gold_export")
    required = ["dim_region.csv", "dim_customer.csv", "dim_product.csv", "dim_date.csv", "fact_sales.csv"]
    if not all((export_dir / name).exists() for name in required):
        pytest.skip("Gold export CSV files are not present")
    from src.postgres_loader import load_export
    assert load_export(export_dir) >= 0
