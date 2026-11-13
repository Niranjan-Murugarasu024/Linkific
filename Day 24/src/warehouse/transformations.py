from __future__ import annotations

import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Any


def money(value: Decimal | str | float | int) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_measures(quantity: Any, unit_price: Any, discount_pct: Any, unit_cost: Any) -> dict[str, Decimal]:
    qty = Decimal(str(quantity))
    price = Decimal(str(unit_price))
    discount = Decimal(str(discount_pct))
    cost = Decimal(str(unit_cost))
    gross = money(qty * price)
    discount_amount = money(gross * discount)
    net = money(gross - discount_amount)
    total_cost = money(qty * cost)
    profit = money(net - total_cost)
    return {
        "gross_sales": gross,
        "discount_amount": discount_amount,
        "net_sales": net,
        "total_cost": total_cost,
        "profit": profit,
    }


def customer_record_hash(customer: dict[str, Any]) -> str:
    """Hash tracked attributes; source_updated_at is intentionally excluded."""
    tracked_fields = (
        "full_name", "email", "city", "state", "country", "region_code", "segment"
    )
    payload = {field: customer.get(field) for field in tracked_fields}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
