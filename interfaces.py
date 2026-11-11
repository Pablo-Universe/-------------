# [НОВИЙ ФАЙЛ] доданий під час рефакторингу
"""Інтерфейси (абстракції), від яких залежать конкретні класи (DIP)."""
from abc import ABC, abstractmethod
from typing import List

from account import Account
from transaction import Transaction


class IValidator(ABC):
    @abstractmethod
    def validate(self, amount: float, account_active: bool, iban: str, daily_total: float) -> bool:
        """Повертає True, якщо операція допустима."""


class ITransactionLogger(ABC):
    @abstractmethod
    def add_record(self, transaction: Transaction) -> None:
        """Зберігає запис про транзакцію."""


class IReportGenerator(ABC):
    @abstractmethod
    def generate_summary(self) -> str:
        """Формує текстовий звіт."""


class IDataLoader(ABC):
    @abstractmethod
    def load_accounts(self) -> List[Account]:
        """Читає рахунки з джерела даних."""

    @abstractmethod
    def load_transactions(self) -> List[Transaction]:
        """Читає транзакції з джерела даних."""


class IBank(ABC):
    @abstractmethod
    def add_account(self, account: Account) -> None: ...

    @abstractmethod
    def get_account(self, iban: str) -> Account: ...

    @abstractmethod
    def process_transaction(self, transaction: Transaction) -> None: ...