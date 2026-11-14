from src.quality.validators import (
    validate_order, duplicate_keys, validate_references, is_valid_email
)


def test_valid_order_passes(valid_order):
    assert validate_order(valid_order) == []


def test_null_customer_is_rejected(valid_order):
    valid_order["customer_id"] = None
    assert "customer_id:NULL_OR_EMPTY" in validate_order(valid_order)


def test_invalid_quantity_is_rejected(valid_order):
    valid_order["quantity"] = 0
    assert "quantity:NOT_POSITIVE" in validate_order(valid_order)


def test_invalid_discount_is_rejected(valid_order):
    valid_order["discount_pct"] = 1.5
    assert "discount_pct:OUT_OF_RANGE" in validate_order(valid_order)


def test_duplicate_order_line_detected():
    rows = [{"order_id": 1, "line_id": 1}, {"order_id": 1, "line_id": 1}]
    assert (1, 1) in duplicate_keys(rows)


def test_referential_integrity_detects_missing_customer():
    rows = [{"order_id": 1, "line_id": 1, "customer_id": 9, "product_id": 2, "region_id": 1}]
    assert validate_references(rows, {1}, {2}, {1}) == [((1, 1), "UNKNOWN_CUSTOMER")]


def test_email_format():
    assert is_valid_email("a.user@example.com")
    assert not is_valid_email("not-an-email")
