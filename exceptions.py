# [НОВИЙ ФАЙЛ] доданий під час рефакторингу
"""Власні винятки банківської системи."""


class BankError(Exception):
    """Базовий виняток для всіх помилок банку."""


class AccountNotFoundError(BankError):
    """Рахунок з таким IBAN не знайдено."""


class DuplicateAccountError(BankError):
    """Рахунок з таким IBAN уже існує."""


class UnsupportedCurrencyError(BankError):
    """Валюта не підтримується банком."""


class CurrencyMismatchError(BankError):
    """Валюта транзакції не збігається з валютою рахунків."""


class InsufficientFundsError(BankError):
    """Недостатньо коштів (з урахуванням комісії)."""


class ValidationError(BankError):
    """Транзакція не пройшла валідацію."""


class InvalidTransactionError(BankError):
    """Транзакція некоректна (наприклад, повторна обробка)."""


class DataLoadError(BankError):
    """Помилка читання вхідних даних з файлу."""