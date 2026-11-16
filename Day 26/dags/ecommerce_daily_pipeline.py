"""Day 26: scheduled, monitored e-commerce ETL pipeline for Apache Airflow 3.4."""

from __future__ import annotations

import json
import logging
import os
import re
import smtplib
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import pendulum
from airflow.sdk import dag, get_current_context, task

LOGGER = logging.getLogger(__name__)
DATA_ROOT = Path(os.environ.get("DAY26_DATA_DIR", "/opt/airflow/data"))
MAX_REJECT_RATE = float(os.environ.get("MAX_REJECT_RATE", "0.10"))


def _safe_name(value: str) -> str:
    """Convert a run identifier into a filesystem-safe directory name."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "run"


def _run_id(context: dict[str, Any] | None = None) -> str:
    if context is None:
        from airflow.sdk import get_current_context

        context = get_current_context()
    return str(context.get("run_id", "manual_run"))


def _run_dir(context: dict[str, Any] | None = None) -> Path:
    return DATA_ROOT / "staging" / _safe_name(_run_id(context))


def _notify(title: str, message: str) -> None:
    """Send optional Slack/email alerts. Notification failures never mask ETL failures."""
    webhook = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if webhook:
        try:
            payload = json.dumps({"text": f"*{title}*\n{message}"}).encode("utf-8")
            request = urllib.request.Request(
                webhook,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=8) as response:
                LOGGER.info("Slack alert delivered; HTTP status=%s", response.status)
        except Exception:
            LOGGER.exception("Unable to send Slack alert")

    smtp_host = os.environ.get("SMTP_HOST", "").strip()
    recipients = [x.strip() for x in os.environ.get("ALERT_EMAIL_TO", "").split(",") if x.strip()]
    sender = os.environ.get("SMTP_FROM", "airflow@localhost").strip()
    if smtp_host and recipients:
        try:
            email = EmailMessage()
            email["Subject"] = f"[Day26 Airflow] {title}"
            email["From"] = sender
            email["To"] = ", ".join(recipients)
            email.set_content(message)
            with smtplib.SMTP(smtp_host, int(os.environ.get("SMTP_PORT", "587")), timeout=10) as server:
                server.starttls()
                username = os.environ.get("SMTP_USER", "").strip()
                password = os.environ.get("SMTP_PASSWORD", "")
                if username:
                    server.login(username, password)
                server.send_message(email)
            LOGGER.info("Email alert delivered to %s", recipients)
        except Exception:
            LOGGER.exception("Unable to send email alert")


def _task_failure_callback(context: dict[str, Any]) -> None:
    """Persist task failure metadata so failures remain inspectable outside the UI."""
    ti = context.get("task_instance")
    run_id = _run_id(context)
    event = {
        "dag_id": getattr(ti, "dag_id", context.get("dag", "unknown")),
        "task_id": getattr(ti, "task_id", "unknown"),
        "run_id": run_id,
        "try_number": getattr(ti, "try_number", None),
        "failed_at_utc": datetime.now(timezone.utc).isoformat(),
        "exception": str(context.get("exception", "Unknown task failure")),
    }
    try:
        target = DATA_ROOT / "dead_letter" / "task_failures" / _safe_name(run_id)
        target.mkdir(parents=True, exist_ok=True)
        task_id = _safe_name(str(event["task_id"]))
        (target / f"{task_id}.json").write_text(json.dumps(event, indent=2), encoding="utf-8")
    except Exception:
        LOGGER.exception("Could not persist task failure event")


def _retry_callback(context: dict[str, Any]) -> None:
    ti = context.get("task_instance")
    LOGGER.warning(
        "TASK RETRY | dag=%s task=%s try=%s run_id=%s",
        getattr(ti, "dag_id", "unknown"),
        getattr(ti, "task_id", "unknown"),
        getattr(ti, "try_number", "unknown"),
        _run_id(context),
    )


def _dag_failure_callback(context: dict[str, Any]) -> None:
    dag_run = context.get("dag_run")
    run_id = _run_id(context)
    task_instance = context.get("task_instance")
    failed_task = getattr(task_instance, "task_id", "see Airflow Grid view")
    message = f"DAG=ecommerce_daily_pipeline | run_id={run_id} | failed_task={failed_task}"
    LOGGER.error("DAG FAILURE | %s", message)
    _notify("DAG FAILED", message)


def _dag_success_callback(context: dict[str, Any]) -> None:
    message = f"DAG=ecommerce_daily_pipeline | run_id={_run_id(context)} | status=SUCCESS"
    LOGGER.info("DAG SUCCESS | %s", message)
    _notify("DAG SUCCEEDED", message)


def _extract_snapshot(filename: str, required_columns: list[str]) -> str:
    """Snapshot one input CSV for this run and return its small XCom path."""
    import pandas as pd

    started = time.monotonic()
    context = get_current_context()
    source = DATA_ROOT / "input" / filename
    if not source.exists():
        raise FileNotFoundError(f"Required input file not found: {source}")

    dataframe = pd.read_csv(source, dtype=str)
    if dataframe.empty:
        raise ValueError(f"Input file contains no records: {source}")

    missing = sorted(set(required_columns) - set(dataframe.columns))
    if missing:
        raise ValueError(f"{filename} is missing required columns: {missing}")

    target_dir = _run_dir(context)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / filename
    dataframe.to_csv(target, index=False)

    LOGGER.info(
        "EXTRACT COMPLETE | file=%s | rows=%d | bytes=%d | output=%s",
        filename,
        len(dataframe),
        source.stat().st_size,
        target,
    )
    LOGGER.info("EXTRACT PERFORMANCE | file=%s | seconds=%.3f", filename, time.monotonic() - started)
    return str(target)


@dag(
    dag_id="ecommerce_daily_pipeline",
    description="Daily e-commerce ingestion, transformation, validation and PostgreSQL load.",
    doc_md=__doc__,
    schedule="0 2 * * *",  # 02:00 UTC = 07:30 Asia/Kolkata
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    max_active_tasks=4,
    dagrun_timeout=timedelta(hours=1),
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=15),
        "execution_timeout": timedelta(minutes=30),
        "on_failure_callback": _task_failure_callback,
        "on_retry_callback": _retry_callback,
    },
    on_failure_callback=_dag_failure_callback,
    on_success_callback=_dag_success_callback,
    tags=["day26", "e-commerce", "etl", "data-quality", "postgres"],
)
def ecommerce_daily_pipeline():
    """Orchestrate one complete, idempotent e-commerce daily batch."""

    @task(task_id="extract_orders")
    def extract_orders() -> str:
        return _extract_snapshot(
            "orders.csv",
            ["order_line_id", "order_id", "order_date", "customer_id", "product_id", "quantity", "unit_price", "status"],
        )

    @task(task_id="extract_customers")
    def extract_customers() -> str:
        return _extract_snapshot("customers.csv", ["customer_id", "customer_name", "city", "region"])

    @task(task_id="extract_products")
    def extract_products() -> str:
        return _extract_snapshot("products.csv", ["product_id", "product_name", "category", "unit_cost"])

    @task(task_id="transform_and_enrich")
    def transform_and_enrich(orders_path: str, customers_path: str, products_path: str) -> dict[str, Any]:
        import pandas as pd

        context = get_current_context()
        started = time.monotonic()
        orders = pd.read_csv(orders_path, dtype=str)
        customers = pd.read_csv(customers_path, dtype=str)
        products = pd.read_csv(products_path, dtype=str)

        if customers["customer_id"].duplicated().any():
            raise ValueError("Customer dimension contains duplicate customer_id values")
        if products["product_id"].duplicated().any():
            raise ValueError("Product dimension contains duplicate product_id values")

        orders["quantity_num"] = pd.to_numeric(orders["quantity"], errors="coerce")
        orders["unit_price_num"] = pd.to_numeric(orders["unit_price"], errors="coerce")
        orders["order_date_parsed"] = pd.to_datetime(orders["order_date"], errors="coerce", utc=False)
        products["unit_cost_num"] = pd.to_numeric(products["unit_cost"], errors="coerce")

        enriched = orders.merge(
            customers[["customer_id", "customer_name", "city", "region"]],
            on="customer_id",
            how="left",
            validate="many_to_one",
            indicator="_customer_match",
        )
        enriched = enriched.merge(
            products[["product_id", "product_name", "category", "unit_cost_num"]],
            on="product_id",
            how="left",
            validate="many_to_one",
            indicator="_product_match",
        )

        reasons = pd.Series("", index=enriched.index, dtype="object")

        def add_reason(mask, label: str) -> None:
            mask = mask.fillna(True) if hasattr(mask, "fillna") else mask
            existing = reasons.loc[mask]
            reasons.loc[mask] = existing.map(lambda value: f"{value};{label}" if value else label)

        line_ids = enriched["order_line_id"].fillna("").astype(str).str.strip()
        add_reason(line_ids.eq(""), "MISSING_ORDER_LINE_ID")
        add_reason(enriched.duplicated(subset=["order_line_id"], keep=False), "DUPLICATE_ORDER_LINE_ID")
        add_reason(enriched["order_date_parsed"].isna(), "INVALID_ORDER_DATE")
        add_reason(
            enriched["quantity_num"].isna()
            | (enriched["quantity_num"] <= 0)
            | ((enriched["quantity_num"] % 1) != 0),
            "INVALID_QUANTITY",
        )
        add_reason(enriched["unit_price_num"].isna() | (enriched["unit_price_num"] < 0), "INVALID_UNIT_PRICE")
        add_reason(enriched["unit_cost_num"].isna() | (enriched["unit_cost_num"] < 0), "INVALID_UNIT_COST")
        add_reason(enriched["_customer_match"] != "both", "UNKNOWN_CUSTOMER_ID")
        add_reason(enriched["_product_match"] != "both", "UNKNOWN_PRODUCT_ID")

        enriched["reject_reason"] = reasons
        accepted = enriched.loc[reasons.eq("")].copy()
        rejected = enriched.loc[reasons.ne("")].copy()

        accepted["quantity"] = accepted["quantity_num"].astype(int)
        accepted["order_date"] = accepted["order_date_parsed"].dt.strftime("%Y-%m-%d")
        accepted["unit_price"] = accepted["unit_price_num"].round(2)
        accepted["unit_cost"] = accepted["unit_cost_num"].round(2)
        accepted["line_revenue"] = (accepted["quantity"] * accepted["unit_price"]).round(2)
        accepted["line_cost"] = (accepted["quantity"] * accepted["unit_cost"]).round(2)
        accepted["gross_profit"] = (accepted["line_revenue"] - accepted["line_cost"]).round(2)
        accepted["order_status"] = accepted["status"].fillna("UNKNOWN").str.strip().str.upper()

        output_columns = [
            "order_line_id", "order_id", "order_date", "customer_id", "customer_name", "city", "region",
            "product_id", "product_name", "category", "quantity", "unit_price", "unit_cost", "line_revenue",
            "line_cost", "gross_profit", "order_status",
        ]
        accepted = accepted[output_columns]

        run_dir = _run_dir(context)
        run_dir.mkdir(parents=True, exist_ok=True)
        valid_path = run_dir / "enriched_orders.csv"
        rejected_path = DATA_ROOT / "dead_letter" / "rejected_records" / _safe_name(_run_id(context)) / "rejected_orders.csv"
        report_path = run_dir / "quality_report.json"
        rejected_path.parent.mkdir(parents=True, exist_ok=True)

        accepted.to_csv(valid_path, index=False)
        rejected.to_csv(rejected_path, index=False)

        input_rows = int(len(orders))
        rejected_rows = int(len(rejected))
        valid_rows = int(len(accepted))
        reject_rate = rejected_rows / input_rows if input_rows else 1.0
        report = {
            "dag_id": "ecommerce_daily_pipeline",
            "run_id": _run_id(context),
            "input_rows": input_rows,
            "valid_rows": valid_rows,
            "rejected_rows": rejected_rows,
            "reject_rate": round(reject_rate, 6),
            "duplicate_order_line_ids": int(orders["order_line_id"].duplicated(keep=False).sum()),
            "revenue_total": round(float(accepted["line_revenue"].sum()), 2) if valid_rows else 0.0,
            "transformation_seconds": round(time.monotonic() - started, 3),
            "valid_file": str(valid_path),
            "dead_letter_file": str(rejected_path),
        }
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

        LOGGER.info(
            "TRANSFORM COMPLETE | source_rows=%d | valid_rows=%d | rejected_rows=%d | reject_rate=%.2f%% | seconds=%.3f",
            input_rows,
            valid_rows,
            rejected_rows,
            reject_rate * 100,
            report["transformation_seconds"],
        )
        LOGGER.info("DLQ OUTPUT | path=%s", rejected_path)
        return report

    @task(task_id="data_quality_check")
    def data_quality_check(report: dict[str, Any]) -> dict[str, Any]:
        from airflow.exceptions import AirflowException

        checks = {
            "at_least_one_valid_record": report["valid_rows"] > 0,
            "reject_rate_within_threshold": report["reject_rate"] <= MAX_REJECT_RATE,
            "duplicate_order_line_ids_absent": report["duplicate_order_line_ids"] == 0,
        }
        report["quality_checks"] = checks
        report["quality_status"] = "PASSED" if all(checks.values()) else "FAILED"
        report_path = Path(report["valid_file"]).parent / "quality_report.json"
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

        LOGGER.info("DATA QUALITY RESULTS | %s", json.dumps(checks, sort_keys=True))
        if not all(checks.values()):
            failed = [name for name, passed in checks.items() if not passed]
            message = (
                f"Quality checks failed: {failed}; reject_rate={report['reject_rate']:.2%}; "
                f"threshold={MAX_REJECT_RATE:.2%}; rejected_rows={report['rejected_rows']}; "
                f"DLQ={report['dead_letter_file']}"
            )
            _notify("DATA QUALITY FAILURE", message)
            raise AirflowException(message)

        if report["rejected_rows"] > 0:
            warning = (
                f"{report['rejected_rows']} records were quarantined; reject_rate={report['reject_rate']:.2%}; "
                f"DLQ={report['dead_letter_file']}"
            )
            LOGGER.warning("DATA QUALITY WARNING | %s", warning)
            _notify("DATA QUALITY WARNING", warning)

        LOGGER.info("DATA QUALITY PASSED | valid_rows=%d | rejected_rows=%d", report["valid_rows"], report["rejected_rows"])
        return report

    @task(task_id="load_to_postgresql")
    def load_to_postgresql(report: dict[str, Any]) -> dict[str, Any]:
        import pandas as pd
        import psycopg2
        from psycopg2.extras import execute_values

        context = get_current_context()
        started = time.monotonic()
        run_id = _run_id(context)
        connection = psycopg2.connect(
            host=os.environ.get("WAREHOUSE_HOST", "postgres"),
            port=int(os.environ.get("WAREHOUSE_PORT", "5432")),
            dbname=os.environ.get("WAREHOUSE_DB", "ecommerce_dw"),
            user=os.environ.get("WAREHOUSE_USER", "airflow"),
            password=os.environ.get("WAREHOUSE_PASSWORD", "day26_local_only"),
            connect_timeout=10,
        )

        create_table_sql = """
            CREATE SCHEMA IF NOT EXISTS analytics;
            CREATE TABLE IF NOT EXISTS analytics.fact_order_lines (
                order_line_id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                order_date DATE NOT NULL,
                customer_id TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                city TEXT,
                region TEXT,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
                unit_cost NUMERIC(12,2) NOT NULL CHECK (unit_cost >= 0),
                line_revenue NUMERIC(14,2) NOT NULL,
                line_cost NUMERIC(14,2) NOT NULL,
                gross_profit NUMERIC(14,2) NOT NULL,
                order_status TEXT,
                pipeline_run_id TEXT NOT NULL,
                loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """
        insert_sql = """
            INSERT INTO analytics.fact_order_lines (
                order_line_id, order_id, order_date, customer_id, customer_name, city, region,
                product_id, product_name, category, quantity, unit_price, unit_cost,
                line_revenue, line_cost, gross_profit, order_status, pipeline_run_id
            ) VALUES %s
            ON CONFLICT (order_line_id) DO UPDATE SET
                order_id = EXCLUDED.order_id,
                order_date = EXCLUDED.order_date,
                customer_id = EXCLUDED.customer_id,
                customer_name = EXCLUDED.customer_name,
                city = EXCLUDED.city,
                region = EXCLUDED.region,
                product_id = EXCLUDED.product_id,
                product_name = EXCLUDED.product_name,
                category = EXCLUDED.category,
                quantity = EXCLUDED.quantity,
                unit_price = EXCLUDED.unit_price,
                unit_cost = EXCLUDED.unit_cost,
                line_revenue = EXCLUDED.line_revenue,
                line_cost = EXCLUDED.line_cost,
                gross_profit = EXCLUDED.gross_profit,
                order_status = EXCLUDED.order_status,
                pipeline_run_id = EXCLUDED.pipeline_run_id,
                loaded_at = NOW();
        """

        total_rows = 0
        batch_size = 10_000
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(create_table_sql)
                    for dataframe in pd.read_csv(report["valid_file"], chunksize=batch_size):
                        rows = []
                        for row in dataframe.itertuples(index=False):
                            rows.append((
                                str(row.order_line_id), str(row.order_id), row.order_date, str(row.customer_id), str(row.customer_name),
                                None if pd.isna(row.city) else str(row.city), None if pd.isna(row.region) else str(row.region),
                                str(row.product_id), str(row.product_name), None if pd.isna(row.category) else str(row.category),
                                int(row.quantity), round(float(row.unit_price), 2), round(float(row.unit_cost), 2),
                                round(float(row.line_revenue), 2), round(float(row.line_cost), 2), round(float(row.gross_profit), 2),
                                str(row.order_status), run_id,
                            ))
                        if rows:
                            execute_values(cursor, insert_sql, rows, page_size=1000)
                            total_rows += len(rows)
                        LOGGER.info("POSTGRES BATCH LOADED | batch_rows=%d | cumulative_rows=%d", len(rows), total_rows)
        finally:
            connection.close()

        elapsed = round(time.monotonic() - started, 3)
        result = {
            **report,
            "rows_written": total_rows,
            "load_seconds": elapsed,
            "pipeline_run_id": run_id,
        }
        LOGGER.info("LOAD COMPLETE | rows_written=%d | load_seconds=%.3f | destination=analytics.fact_order_lines", len(rows), elapsed)
        return result

    @task(task_id="reconcile_postgresql_load")
    def reconcile_postgresql_load(load_result: dict[str, Any]) -> dict[str, Any]:
        import psycopg2

        from airflow.exceptions import AirflowException

        started = time.monotonic()
        connection = psycopg2.connect(
            host=os.environ.get("WAREHOUSE_HOST", "postgres"),
            port=int(os.environ.get("WAREHOUSE_PORT", "5432")),
            dbname=os.environ.get("WAREHOUSE_DB", "ecommerce_dw"),
            user=os.environ.get("WAREHOUSE_USER", "airflow"),
            password=os.environ.get("WAREHOUSE_PASSWORD", "day26_local_only"),
            connect_timeout=10,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*), COALESCE(SUM(line_revenue), 0) "
                    "FROM analytics.fact_order_lines WHERE pipeline_run_id = %s",
                    (load_result["pipeline_run_id"],),
                )
                actual_rows, actual_revenue = cursor.fetchone()
        finally:
            connection.close()

        expected_rows = int(load_result["valid_rows"])
        expected_revenue = round(float(load_result["revenue_total"]), 2)
        actual_revenue = round(float(actual_revenue), 2)
        if actual_rows != expected_rows or actual_revenue != expected_revenue:
            message = (
                f"Post-load reconciliation failed: expected_rows={expected_rows}, actual_rows={actual_rows}, "
                f"expected_revenue={expected_revenue:.2f}, actual_revenue={actual_revenue:.2f}"
            )
            _notify("POST-LOAD RECONCILIATION FAILURE", message)
            raise AirflowException(message)

        result = {
            **load_result,
            "warehouse_rows_verified": int(actual_rows),
            "warehouse_revenue_verified": actual_revenue,
            "reconciliation_status": "PASSED",
            "reconciliation_seconds": round(time.monotonic() - started, 3),
        }
        LOGGER.info(
            "RECONCILIATION PASSED | rows=%d | revenue=%.2f | seconds=%.3f",
            actual_rows,
            actual_revenue,
            result["reconciliation_seconds"],
        )
        return result

    @task(task_id="publish_run_summary")
    def publish_run_summary(result: dict[str, Any]) -> str:
        context = get_current_context()
        logical_date = context.get("logical_date")
        summary = {
            "dag_id": "ecommerce_daily_pipeline",
            "run_id": _run_id(context),
            "logical_date": logical_date.isoformat() if logical_date else None,
            "schedule": "0 2 * * * UTC (07:30 Asia/Kolkata)",
            "status": "SUCCESS",
            "source_rows": int(result["input_rows"]),
            "valid_rows": int(result["valid_rows"]),
            "rejected_rows": int(result["rejected_rows"]),
            "reject_rate_pct": round(float(result["reject_rate"]) * 100, 2),
            "rows_written": int(result["rows_written"]),
            "warehouse_rows_verified": int(result["warehouse_rows_verified"]),
            "revenue_total": round(float(result["revenue_total"]), 2),
            "warehouse_revenue_verified": round(float(result["warehouse_revenue_verified"]), 2),
            "quality_status": result["quality_status"],
            "reconciliation_status": result["reconciliation_status"],
            "transformation_seconds": result["transformation_seconds"],
            "load_seconds": result["load_seconds"],
            "reconciliation_seconds": result["reconciliation_seconds"],
            "dead_letter_file": result["dead_letter_file"],
            "warehouse_table": "analytics.fact_order_lines",
        }
        destination = DATA_ROOT / "reports" / _safe_name(_run_id(context))
        destination.mkdir(parents=True, exist_ok=True)
        summary_path = destination / "run_summary.json"
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        LOGGER.info("PIPELINE RUN SUMMARY | %s", json.dumps(summary, sort_keys=True))
        return str(summary_path)

    orders = extract_orders()
    customers = extract_customers()
    products = extract_products()
    transformed = transform_and_enrich(orders, customers, products)
    quality_checked = data_quality_check(transformed)
    loaded = load_to_postgresql(quality_checked)
    reconciled = reconcile_postgresql_load(loaded)
    publish_run_summary(reconciled)


ecommerce_daily_pipeline()
