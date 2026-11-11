# [НОВИЙ ФАЙЛ] доданий під час рефакторингу
import unittest

from account import Account
from transaction import Transaction


class AccountTests(unittest.TestCase):
    def setUp(self):
        self.acc = Account("UA1", 100.0, "Іван")

    def test_deposit_ok(self):
        self.assertTrue(self.acc.deposit(50))
        self.assertEqual(self.acc.balance, 150)

    def test_deposit_invalid_amount(self):
        self.assertFalse(self.acc.deposit(0))
        self.assertFalse(self.acc.deposit(-5))
        self.assertEqual(self.acc.balance, 100)

    def test_withdraw_ok(self):
        self.assertTrue(self.acc.withdraw(100))
        self.assertEqual(self.acc.balance, 0)

    def test_withdraw_too_much(self):
        self.assertFalse(self.acc.withdraw(100.01))
        self.assertEqual(self.acc.balance, 100)

    def test_withdraw_uses_credit_limit(self):
        acc = Account("UA2", 100.0, "Анна", credit_limit=50)
        self.assertTrue(acc.withdraw(150))
        self.assertEqual(acc.balance, -50)
        self.assertFalse(acc.withdraw(1))

    def test_inactive_account_blocks_operations(self):
        acc = Account("UA3", 100.0, "Олег", is_active=False)
        self.assertFalse(acc.deposit(10))
        self.assertFalse(acc.withdraw(10))

    def test_invalid_constructor_args(self):
        with self.assertRaises(ValueError):
            Account("", 0, "X")
        with self.assertRaises(ValueError):
            Account("UA", 0, "")
        with self.assertRaises(ValueError):
            Account("UA", 0, "X", credit_limit=-1)


class TransactionTests(unittest.TestCase):
    def test_default_values(self):
        t = Transaction("A", "B", 10, "pending")
        self.assertEqual((t.currency, t.tx_type, t.description), ("UAH", "transfer", ""))

    def test_status_setter_validates(self):
        t = Transaction("A", "B", 10, "pending")
        t.status = "completed"
        self.assertEqual(t.status, "completed")
        with self.assertRaises(ValueError):
            t.status = "unknown"

    def test_constructor_validates_status_and_amount(self):
        with self.assertRaises(ValueError):
            Transaction("A", "B", 10, "weird")
        with self.assertRaises(ValueError):
            Transaction("A", "B", 0, "pending")

    def test_str_contains_key_info(self):
        s = str(Transaction("A", "B", 10, "pending"))
        for part in ("transfer", "10", "UAH", "pending", "A -> B"):
            self.assertIn(part, s)


if __name__ == "__main__":
    unittest.main()