import logging
from datetime import date
from typing import Dict, List
 
from account import Account
from exceptions import (AccountNotFoundError, CurrencyMismatchError, DuplicateAccountError,
                        InsufficientFundsError, InvalidTransactionError, UnsupportedCurrencyError,
                        ValidationError, BankError)
from interfaces import IBank, ITransactionLogger, IValidator
from transaction import Transaction
 
logger = logging.getLogger(__name__)
 
 
class Bank(IBank):
    """Банк. Залежності (валідатор, журнал) передаються ззовні — Dependency Injection."""
 
    def __init__(self, bank_name: str, mfo_code: str, allowed_currencies: List[str],
                 validator: IValidator, tx_logger: ITransactionLogger, commission_rate: float = 0.01) -> None:
        if not 0 <= commission_rate < 1:
            raise ValueError("commission_rate must be in [0, 1)")
        self._bank_name = bank_name
        self._mfo_code = mfo_code
        self._allowed_currencies = allowed_currencies
        self._validator = validator
        self._tx_logger = tx_logger
        self._commission_rate = commission_rate
        self._accounts: Dict[str, Account] = {}
        self._transactions: List[Transaction] = []
        self._collected_commission = 0.0
 
    def add_account(self, account: Account) -> None:
        if account.currency not in self._allowed_currencies:
            raise UnsupportedCurrencyError(f"Currency {account.currency} not supported by this bank")
        if account.iban in self._accounts:
            raise DuplicateAccountError(f"Account with IBAN {account.iban} already exists")
        self._accounts[account.iban] = account
        logger.info("Account added: %s (%s)", account.iban, account.owner_name)
 
    def get_account(self, iban: str) -> Account:
        if iban not in self._accounts:
            raise AccountNotFoundError(f"Account with IBAN {iban} not found")
        return self._accounts[iban]
 
    def _daily_total(self, iban: str) -> float:
        today = date.today()
        return sum(t.amount for t in self._transactions
                   if t.from_iban == iban and t.status == "completed" and t.date.date() == today)
 
    def _fail(self, transaction: Transaction, error: BankError) -> None:
        transaction.status = "failed"
        logger.error("Transaction failed (%s -> %s, %s): %s",
                     transaction.from_iban, transaction.to_iban, transaction.amount, error)
        self._tx_logger.add_record(transaction)
        raise error
 
    def process_transaction(self, transaction: Transaction) -> None:
        if transaction.status != "pending":
            raise InvalidTransactionError(f"Only pending transactions can be processed, got '{transaction.status}'")
 
        try:
            from_account = self.get_account(transaction.from_iban)
            to_account = self.get_account(transaction.to_iban)
        except AccountNotFoundError as e:
            self._fail(transaction, e)
            return
 
        if from_account is to_account:
            self._fail(transaction, InvalidTransactionError("Sender and receiver accounts must differ"))
        if not (transaction.currency == from_account.currency == to_account.currency):
            self._fail(transaction, CurrencyMismatchError(
                f"Currency mismatch: tx={transaction.currency}, from={from_account.currency}, to={to_account.currency}"))
 
        sender_ok = self._validator.validate(transaction.amount, from_account.is_active,
                                             from_account.iban, self._daily_total(from_account.iban))
        receiver_ok = self._validator.validate(transaction.amount, to_account.is_active, to_account.iban, 0.0)
        if not (sender_ok and receiver_ok):
            self._fail(transaction, ValidationError("Transaction did not pass validation"))
 
        commission = round(transaction.amount * self._commission_rate, 2)
        total = transaction.amount + commission
        if not from_account.withdraw(total):
            self._fail(transaction, InsufficientFundsError(
                f"Insufficient funds: need {total} (amount {transaction.amount} + commission {commission})"))
 
        if not to_account.deposit(transaction.amount):
            from_account.balance += total  # відкат
            self._fail(transaction, InvalidTransactionError("Deposit to receiver failed, transaction rolled back"))
 
        self._collected_commission += commission
        transaction.status = "completed"
        self._transactions.append(transaction)
        self._tx_logger.add_record(transaction)
        logger.info("Transaction completed: %s -> %s, %s %s (commission %s)", transaction.from_iban,
                    transaction.to_iban, transaction.amount, transaction.currency, commission)
 
    @property
    def bank_name(self) -> str:
        return self._bank_name
 
    @property
    def accounts(self) -> Dict[str, Account]:
        return self._accounts
 
    @property
    def transactions(self) -> List[Transaction]:
        return list(self._transactions)
 
    @property
    def collected_commission(self) -> float:
        return self._collected_commission