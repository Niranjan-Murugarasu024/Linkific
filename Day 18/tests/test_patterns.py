"""Unit tests for regex validators and text extractors."""
import unittest
from src.validators import (
    validate_email, validate_phone, validate_pincode, validate_name,
    validate_time, validate_password,
)
from src.extractors import extract_emails, extract_order_ids, valid_ip_addresses

class TestValidators(unittest.TestCase):
    def test_valid_email(self):
        self.assertTrue(validate_email("test.user+tag@gmail.com"))

    def test_invalid_email(self):
        self.assertFalse(validate_email("testgmail.com"))

    def test_valid_indian_phone(self):
        self.assertTrue(validate_phone("+91 9876543210"))
        self.assertTrue(validate_phone("9876543210"))

    def test_invalid_indian_phone(self):
        self.assertFalse(validate_phone("1234567890"))

    def test_pincode(self):
        self.assertTrue(validate_pincode("641001"))
        self.assertFalse(validate_pincode("012345"))

    def test_name(self):
        self.assertTrue(validate_name("Mary Jane"))
        self.assertFalse(validate_name("John123"))

    def test_time(self):
        self.assertTrue(validate_time("23:59"))
        self.assertFalse(validate_time("25:90"))

    def test_password(self):
        self.assertTrue(validate_password("Python123"))
        self.assertFalse(validate_password("short"))

class TestExtractors(unittest.TestCase):
    def test_email_extraction(self):
        self.assertEqual(extract_emails("Contact a@test.com"), ["a@test.com"])

    def test_order_id_extraction(self):
        self.assertEqual(extract_order_ids("Order ORD-123456 paid"), ["ORD-123456"])

    def test_ip_candidate_validation(self):
        self.assertEqual(valid_ip_addresses("IPs 192.168.1.1 and 999.1.1.1"), ["192.168.1.1"])

if __name__ == "__main__":
    unittest.main()
