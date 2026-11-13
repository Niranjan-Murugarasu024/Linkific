from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warehouse.db import database_connection  # noqa: E402


def main() -> int:
    try:
        with database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE source.customers
                       SET city = CASE WHEN city = 'Chennai' THEN 'Coimbatore' ELSE 'Chennai' END,
                           segment = CASE WHEN segment = 'Corporate' THEN 'Small Business' ELSE 'Corporate' END,
                           updated_at = GREATEST(CURRENT_DATE, updated_at + 1)
                       WHERE customer_id = (SELECT MIN(customer_id) FROM source.customers)
                       RETURNING customer_id, full_name, city, segment, updated_at"""
                )
                changed = cursor.fetchone()
                if not changed:
                    raise RuntimeError("No customer found to update")
            connection.commit()
        print("Updated one source customer to demonstrate SCD Type 2:")
        print(f"  customer_id={changed[0]}, name={changed[1]}, city={changed[2]}, segment={changed[3]}, updated_at={changed[4]}")
        print("Now run: py scripts/run_pipeline.py")
        return 0
    except Exception as exc:
        print(f"SCD2 demo failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
