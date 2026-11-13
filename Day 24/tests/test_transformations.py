from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warehouse.transformations import calculate_measures, customer_record_hash  # noqa: E402


class MeasureCalculationTests(unittest.TestCase):
    def test_sales_measures(self):
        result = calculate_measures("2", "100.00", "0.10", "60.00")
        self.assertEqual(result["gross_sales"], Decimal("200.00"))
        self.assertEqual(result["discount_amount"], Decimal("20.00"))
        self.assertEqual(result["net_sales"], Decimal("180.00"))
        self.assertEqual(result["total_cost"], Decimal("120.00"))
        self.assertEqual(result["profit"], Decimal("60.00"))

    def test_rounding_is_two_decimal_places(self):
        result = calculate_measures("3", "19.995", "0.05", "10.005")
        self.assertEqual(result["gross_sales"], Decimal("59.99"))
        self.assertEqual(result["total_cost"], Decimal("30.02"))


class CustomerHashTests(unittest.TestCase):
    def test_hash_is_deterministic(self):
        customer = {
            "full_name": "Test User", "email": "test@example.com", "city": "Coimbatore",
            "state": "Tamil Nadu", "country": "India", "region_code": "SOUTH",
            "segment": "Consumer", "updated_at": "2025-01-01",
        }
        self.assertEqual(customer_record_hash(customer), customer_record_hash(customer.copy()))

    def test_source_timestamp_does_not_create_scd_change(self):
        first = {
            "full_name": "Test User", "email": "test@example.com", "city": "Coimbatore",
            "state": "Tamil Nadu", "country": "India", "region_code": "SOUTH",
            "segment": "Consumer", "updated_at": "2025-01-01",
        }
        second = {**first, "updated_at": "2025-02-01"}
        self.assertEqual(customer_record_hash(first), customer_record_hash(second))

    def test_tracked_attribute_change_changes_hash(self):
        first = {
            "full_name": "Test User", "email": "test@example.com", "city": "Coimbatore",
            "state": "Tamil Nadu", "country": "India", "region_code": "SOUTH",
            "segment": "Consumer",
        }
        second = {**first, "city": "Chennai"}
        self.assertNotEqual(customer_record_hash(first), customer_record_hash(second))


if __name__ == "__main__":
    unittest.main(verbosity=2)
