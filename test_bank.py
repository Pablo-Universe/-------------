# [НОВИЙ ФАЙЛ] доданий під час рефакторингу
import unittest
from unittest.mock import Mock

from account import Account
from bank import Bank
from exceptions import (AccountNotFoundError, CurrencyMismatchError, DuplicateAccountError,
                        InsufficientFundsError, InvalidTransactionError, UnsupportedCurrencyError,
                        ValidationError)
from interfaces import ITransactionLogger, IValidator
from transaction import Transaction
from validator import Validator

A = "UA300000000000012345678901231"
B = "UA300000000000012345678901241"
C = "UA300000000000012345678901251"


class FakeLogger(ITransactionLogger):
    """Тестова реалізація інтерфейсу — підставляється через DI."""

    def __init__(self):
        self.records = []

    def add_record(self, transaction):
        self.records.append(transaction)


def make_bank(validator=None, rate=0.01, balance_a=10000.0, **kw):
    fake = FakeLogger()
    bank = Bank("Test", "300001", ["UAH", "USD"], validator or Validator(min_transfer=1), fake, rate)
    bank.add_account(Account(A, balance_a, "Іван", **kw))
    bank.add_account(Account(B, 5000.0, "Анна"))
    return bank, fake


def tx(amount=500.0, frm=A, to=B, currency="UAH"):
    return Transaction(frm, to, amount, "pending", currency)


class BankAccountsTests(unittest.TestCase):
    def test_get_unknown_account(self):
        bank, _ = make_bank()
        with self.assertRaises(AccountNotFoundError):
            bank.get_account("UA000")

    def test_unsupported_currency(self):
        bank, _ = make_bank()
        with self.assertRaises(UnsupportedCurrencyError):
            bank.add_account(Account("UA9", 1, "X", currency="PLN"))

    def test_duplicate_account(self):
        bank, _ = make_bank()
        with self.assertRaises(DuplicateAccountError):
            bank.add_account(Account(A, 1, "Dup"))

    def test_invalid_commission_rate(self):
        with self.assertRaises(ValueError):
            Bank("B", "1", ["UAH"], Mock(spec=IValidator), FakeLogger(), commission_rate=1.5)


class BankProcessTests(unittest.TestCase):
    def test_successful_transfer(self):
        bank, fake = make_bank()
        t = tx(500)
        bank.process_transaction(t)
        self.assertEqual(t.status, "completed")
        self.assertAlmostEqual(bank.get_account(A).balance, 9495.0)
        self.assertAlmostEqual(bank.get_account(B).balance, 5500.0)
        self.assertAlmostEqual(bank.collected_commission, 5.0)
        self.assertEqual(fake.records, [t])
        self.assertEqual(bank.transactions, [t])

    def test_insufficient_funds(self):
        bank, fake = make_bank(balance_a=100.0)
        t = tx(500)
        with self.assertRaises(InsufficientFundsError):
            bank.process_transaction(t)
        self.assertEqual(t.status, "failed")
        self.assertEqual(bank.get_account(A).balance, 100.0)
        self.assertEqual(bank.get_account(B).balance, 5000.0)
        self.assertEqual(fake.records, [t])  # невдала спроба теж потрапляє в журнал

    def test_commission_is_taken_into_account(self):
        # 500 вистачає на суму, але не вистачає на суму + комісію (505)
        bank, _ = make_bank(balance_a=500.0)
        with self.assertRaises(InsufficientFundsError):
            bank.process_transaction(tx(500))
        self.assertEqual(bank.get_account(A).balance, 500.0)

    def test_credit_limit_allows_transfer(self):
        bank, _ = make_bank(balance_a=100.0, credit_limit=1000.0)
        bank.process_transaction(tx(500))
        self.assertAlmostEqual(bank.get_account(A).balance, 100 - 505)

    def test_unknown_receiver(self):
        bank, fake = make_bank()
        t = tx(to="UA399999999999999999999999999")
        with self.assertRaises(AccountNotFoundError):
            bank.process_transaction(t)
        self.assertEqual(t.status, "failed")
        self.assertEqual(len(fake.records), 1)

    def test_same_account(self):
        bank, _ = make_bank()
        with self.assertRaises(InvalidTransactionError):
            bank.process_transaction(tx(to=A))

    def test_currency_mismatch(self):
        bank, _ = make_bank()
        bank.add_account(Account(C, 10, "Олег", currency="USD"))
        with self.assertRaises(CurrencyMismatchError):
            bank.process_transaction(tx(to=C))
        with self.assertRaises(CurrencyMismatchError):
            bank.process_transaction(tx(currency="USD"))

    def test_only_pending_can_be_processed(self):
        bank, _ = make_bank()
        t = tx()
        bank.process_transaction(t)
        with self.assertRaises(InvalidTransactionError):
            bank.process_transaction(t)  # повторна обробка
        self.assertAlmostEqual(bank.get_account(A).balance, 9495.0)

    def test_validator_rejection_via_mock(self):
        validator = Mock(spec=IValidator)
        validator.validate.return_value = False
        bank, _ = make_bank(validator=validator)
        t = tx()
        with self.assertRaises(ValidationError):
            bank.process_transaction(t)
        self.assertEqual(t.status, "failed")
        self.assertEqual(bank.get_account(A).balance, 10000.0)
        validator.validate.assert_called()

    def test_inactive_receiver_does_not_lose_money(self):
        bank, _ = make_bank()
        bank.get_account(B).is_active = False
        with self.assertRaises(ValidationError):
            bank.process_transaction(tx())
        self.assertEqual(bank.get_account(A).balance, 10000.0)

    def test_daily_limit_across_transactions(self):
        bank, _ = make_bank(validator=Validator(min_transfer=1, max_daily_limit=1000))
        bank.process_transaction(tx(600))
        with self.assertRaises(ValidationError):
            bank.process_transaction(tx(600))
        bank.process_transaction(tx(400))  # рівно в ліміт


if __name__ == "__main__":
    unittest.main()