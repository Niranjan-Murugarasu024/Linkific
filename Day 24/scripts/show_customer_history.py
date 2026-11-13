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
                    """SELECT customer_id, full_name, city, segment, valid_from,
                              valid_to, is_current
                       FROM dw.dim_customer
                       WHERE customer_id = (SELECT MIN(customer_id) FROM dw.dim_customer)
                       ORDER BY valid_from"""
                )
                rows = cursor.fetchall()
        print("Customer SCD Type 2 history:")
        print("customer_id | full_name | city | segment | valid_from | valid_to | is_current")
        for row in rows:
            print(" | ".join(str(value) for value in row))
        return 0
    except Exception as exc:
        print(f"Could not read customer history: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
