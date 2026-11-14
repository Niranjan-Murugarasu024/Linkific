import pytest


@pytest.fixture
def valid_order():
    return {
        "order_id": 10, "line_id": 1, "customer_id": 3, "product_id": 8,
        "region_id": 2, "order_date": "2026-11-10", "quantity": 2,
        "unit_price": 120.50, "discount_pct": 0.10,
        "status": "COMPLETED"
    }
