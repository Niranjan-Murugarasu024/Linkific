from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from warehouse.config import PROJECT_ROOT


def _scalar_check(cursor, name: str, sql: str, expected=None, comparator="equals_zero", detail="") -> dict:
    cursor.execute(sql)
    actual = cursor.fetchone()[0]
    if comparator == "equals_zero":
        passed = actual == 0
    elif comparator == "equals":
        passed = actual == expected
    elif comparator == "greater_than_zero":
        passed = actual > 0
    else:
        raise ValueError(f"Unsupported validation comparator: {comparator}")
    return {
        "check": name,
        "status": "PASS" if passed else "FAIL",
        "expected": expected if comparator == "equals" else comparator,
        "actual": actual,
        "detail": detail,
    }


def run_validations(connection) -> dict:
    checks: list[dict] = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM source.order_items")
        source_line_count = cursor.fetchone()[0]
        checks.append(_scalar_check(
            cursor, "Fact row count equals source order-line count",
            "SELECT ABS((SELECT COUNT(*) FROM dw.fact_sales) - (SELECT COUNT(*) FROM source.order_items))",
            detail=f"Source order lines: {source_line_count}",
        ))
        checks.append(_scalar_check(
            cursor, "Current customer dimension count equals source customers",
            "SELECT ABS((SELECT COUNT(*) FROM dw.dim_customer WHERE is_current) - (SELECT COUNT(*) FROM source.customers))",
        ))
        checks.append(_scalar_check(
            cursor, "Product dimension count equals source products",
            "SELECT ABS((SELECT COUNT(*) FROM dw.dim_product) - (SELECT COUNT(*) FROM source.products))",
        ))
        checks.append(_scalar_check(
            cursor, "Region dimension count equals source regions",
            "SELECT ABS((SELECT COUNT(*) FROM dw.dim_region) - (SELECT COUNT(*) FROM source.regions))",
        ))
        checks.append(_scalar_check(
            cursor, "Fact rows with missing date dimension key",
            "SELECT COUNT(*) FROM dw.fact_sales f LEFT JOIN dw.dim_date d ON d.date_key=f.date_key WHERE d.date_key IS NULL",
        ))
        checks.append(_scalar_check(
            cursor, "Fact rows with missing customer dimension key",
            "SELECT COUNT(*) FROM dw.fact_sales f LEFT JOIN dw.dim_customer d ON d.customer_key=f.customer_key WHERE d.customer_key IS NULL",
        ))
        checks.append(_scalar_check(
            cursor, "Fact rows with missing product dimension key",
            "SELECT COUNT(*) FROM dw.fact_sales f LEFT JOIN dw.dim_product d ON d.product_key=f.product_key WHERE d.product_key IS NULL",
        ))
        checks.append(_scalar_check(
            cursor, "Fact rows with missing region dimension key",
            "SELECT COUNT(*) FROM dw.fact_sales f LEFT JOIN dw.dim_region d ON d.region_key=f.region_key WHERE d.region_key IS NULL",
        ))
        checks.append(_scalar_check(
            cursor, "Fact sales arithmetic is consistent",
            """SELECT COUNT(*) FROM dw.fact_sales
               WHERE ABS(net_sales - (gross_sales - discount_amount)) > 0.01
                  OR ABS(profit - (net_sales - total_cost)) > 0.01
                  OR ABS(total_cost - (quantity * unit_cost)) > 0.01""",
        ))
        checks.append(_scalar_check(
            cursor, "No invalid fact quantities or discounts",
            "SELECT COUNT(*) FROM dw.fact_sales WHERE quantity <= 0 OR discount_pct < 0 OR discount_pct > 1",
        ))
        checks.append(_scalar_check(
            cursor, "Each customer has at most one current SCD2 row",
            """SELECT COUNT(*) FROM (
                   SELECT customer_id FROM dw.dim_customer WHERE is_current
                   GROUP BY customer_id HAVING COUNT(*) > 1
               ) duplicates""",
        ))
        checks.append(_scalar_check(
            cursor, "All source order dates exist in date dimension",
            """SELECT COUNT(*) FROM source.orders o
               LEFT JOIN dw.dim_date d ON d.full_date=o.order_date
               WHERE d.date_key IS NULL""",
        ))
        checks.append(_scalar_check(
            cursor, "No overlapping customer validity ranges",
            """SELECT COUNT(*) FROM dw.dim_customer a
               JOIN dw.dim_customer b
                 ON a.customer_id=b.customer_id AND a.customer_key < b.customer_key
                AND daterange(a.valid_from, a.valid_to, '[]') && daterange(b.valid_from, b.valid_to, '[]')""",
        ))
        cursor.execute("SELECT COUNT(*) FROM dw.fact_sales")
        fact_count = cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(SUM(net_sales), 0) FROM dw.fact_sales")
        total_net_sales = str(cursor.fetchone()[0])
        cursor.execute("SELECT COALESCE(SUM(profit), 0) FROM dw.fact_sales")
        total_profit = str(cursor.fetchone()[0])
        cursor.execute("SELECT COUNT(*) FROM dw.dim_date WHERE is_holiday")
        holiday_dates = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM dw.dim_customer WHERE NOT is_current")
        historical_customer_rows = cursor.fetchone()[0]

    report = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "overall_status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "summary": {
            "checks_passed": sum(item["status"] == "PASS" for item in checks),
            "checks_failed": sum(item["status"] == "FAIL" for item in checks),
            "fact_rows": fact_count,
            "net_sales": total_net_sales,
            "profit": total_profit,
            "holiday_dates_in_calendar": holiday_dates,
            "historical_customer_versions": historical_customer_rows,
        },
        "checks": checks,
    }
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = reports_dir / f"validation_report_{stamp}.json"
    text_path = reports_dir / f"validation_report_{stamp}.txt"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        f"DAY 24 DATA WAREHOUSE VALIDATION: {report['overall_status']}",
        f"Generated: {report['generated_at']}",
        f"Checks passed: {report['summary']['checks_passed']}",
        f"Checks failed: {report['summary']['checks_failed']}",
        f"Fact rows: {fact_count:,}",
        f"Net sales: {total_net_sales}",
        f"Profit: {total_profit}",
        f"Holiday dates: {holiday_dates}",
        f"Historical customer versions: {historical_customer_rows}",
        "",
    ]
    lines.extend(f"[{item['status']}] {item['check']} | expected={item['expected']} | actual={item['actual']}" for item in checks)
    text_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    report["files"] = {"json": str(json_path.relative_to(PROJECT_ROOT)), "text": str(text_path.relative_to(PROJECT_ROOT))}
    return report
