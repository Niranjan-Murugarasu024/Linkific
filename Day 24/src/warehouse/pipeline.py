from __future__ import annotations

import json

from warehouse.db import database_connection
from warehouse.dimensions import load_all_dimensions
from warehouse.facts import load_sales_fact
from warehouse.validation import run_validations


def run_pipeline() -> dict:
    with database_connection() as connection:
        dimension_result = load_all_dimensions(connection)
        fact_rows_processed = load_sales_fact(connection)
        validation_result = run_validations(connection)
    return {
        "dimensions": dimension_result,
        "fact_rows_inserted_or_updated": fact_rows_processed,
        "validation": validation_result,
    }


def main() -> int:
    try:
        result = run_pipeline()
    except Exception as exc:
        print(f"\nPIPELINE FAILED: {exc}")
        return 1
    print("\nDAY 24 WAREHOUSE ETL SUMMARY")
    print(json.dumps(result, indent=2, default=str))
    return 0 if result["validation"]["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
