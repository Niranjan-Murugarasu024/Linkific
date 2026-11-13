from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warehouse.config import PROJECT_ROOT, connect  # noqa: E402
from warehouse.source_loader import load_source_data  # noqa: E402


def main() -> int:
    connection = None
    try:
        connection = connect()
        cursor = connection.cursor()
        for sql_file in (PROJECT_ROOT / "sql" / "01_source_schema.sql", PROJECT_ROOT / "sql" / "02_warehouse_schema.sql"):
            cursor.execute(sql_file.read_text(encoding="utf-8"))
            connection.commit()
            print(f"Applied {sql_file.name}")
        cursor.close()
        counts = load_source_data(connection)
        print("\nSource tables loaded:")
        for table, count in counts.items():
            print(f"  {table:14s} {count:>7,}")
        print("\nDatabase setup complete. Run scripts/run_pipeline.py next.")
        return 0
    except Exception as exc:
        if connection:
            connection.rollback()
        print(f"Database setup failed: {exc}")
        return 1
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
