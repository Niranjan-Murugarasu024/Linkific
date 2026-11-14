"""Reusable, dependency-light data quality helpers for unit testing and local checks."""
from __future__ import annotations
from datetime import date
from typing import Iterable


def is_non_empty(value) -> bool:
    return value is not None and str(value).strip() != ""


def is_positive_number(value) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def is_valid_email(value) -> bool:
    if not isinstance(value, str) or "@" not in value:
        return False
    local, _, domain = value.strip().partition("@")
    return bool(local and "." in domain and not domain.startswith(".") and not domain.endswith("."))


def validate_order(row: dict) -> list[str]:
    """Return all quality rule failures for one order-line dictionary."""
    failures = []
    required = ("order_id", "line_id", "customer_id", "product_id", "region_id", "order_date")
    for field in required:
        if not is_non_empty(row.get(field)):
            failures.append(f"{field}:NULL_OR_EMPTY")
    if not is_positive_number(row.get("quantity")):
        failures.append("quantity:NOT_POSITIVE")
    try:
        if float(row.get("unit_price")) < 0:
            failures.append("unit_price:NEGATIVE")
    except (TypeError, ValueError):
        failures.append("unit_price:INVALID_NUMBER")
    try:
        discount = float(row.get("discount_pct"))
        if not 0 <= discount <= 1:
            failures.append("discount_pct:OUT_OF_RANGE")
    except (TypeError, ValueError):
        failures.append("discount_pct:INVALID_NUMBER")
    try:
        date.fromisoformat(str(row.get("order_date"))[:10])
    except (TypeError, ValueError):
        failures.append("order_date:INVALID_FORMAT")
    if str(row.get("status", "")).upper() not in {"PENDING", "SHIPPED", "COMPLETED", "CANCELLED"}:
        failures.append("status:INVALID_VALUE")
    return failures


def duplicate_keys(rows: Iterable[dict], key_fields=("order_id", "line_id")) -> set[tuple]:
    seen, duplicates = set(), set()
    for row in rows:
        key = tuple(row.get(field) for field in key_fields)
        if key in seen:
            duplicates.add(key)
        seen.add(key)
    return duplicates


def validate_references(rows, customer_ids, product_ids, region_ids):
    failures = []
    for row in rows:
        key = (row.get("order_id"), row.get("line_id"))
        if row.get("customer_id") not in customer_ids:
            failures.append((key, "UNKNOWN_CUSTOMER"))
        if row.get("product_id") not in product_ids:
            failures.append((key, "UNKNOWN_PRODUCT"))
        if row.get("region_id") not in region_ids:
            failures.append((key, "UNKNOWN_REGION"))
    return failures
