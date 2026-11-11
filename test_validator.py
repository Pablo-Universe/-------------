# [НОВИЙ ФАЙЛ] доданий під час рефакторингу
import unittest

from interfaces import IValidator
from validator import Validator

IBAN = "UA300000000000012345678901231"


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.v = Validator(min_transfer=10, max_transfer=1000, max_daily_limit=1500)

    def test_implements_interface(self):
        self.assertIsInstance(self.v, IValidator)

    def test_valid(self):
        self.assertTrue(self.v.validate(100, True, IBAN, 0))

    def test_inactive_account(self):
        self.assertFalse(self.v.validate(100, False, IBAN, 0))

    def test_amount_bounds(self):
        self.assertFalse(self.v.validate(9.99, True, IBAN, 0))
        self.assertFalse(self.v.validate(1000.01, True, IBAN, 0))
        self.assertTrue(self.v.validate(10, True, IBAN, 0))
        self.assertTrue(self.v.validate(1000, True, IBAN, 0))

    def test_iban_length_and_country(self):
        self.assertFalse(self.v.validate(100, True, IBAN[:-1], 0))
        self.assertFalse(self.v.validate(100, True, "PL" + IBAN[2:], 0))

    def test_daily_limit(self):
        self.assertTrue(self.v.validate(500, True, IBAN, 1000))
        self.assertFalse(self.v.validate(501, True, IBAN, 1000))

    def test_invalid_config(self):
        with self.assertRaises(ValueError):
            Validator(min_transfer=10, max_transfer=5)


if __name__ == "__main__":
    unittest.main()
    