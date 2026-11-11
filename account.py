# Клас 2: Банківський рахунок
import logging
 
logger = logging.getLogger(__name__)
 
 
class Account:
 
    def __init__(self, iban: str, balance: float, owner_name: str, currency: str = "UAH",
                 account_type: str = "debit", is_active: bool = True, credit_limit: float = 0.0) -> None:
        if not iban or not isinstance(iban, str):
            raise ValueError("IBAN must be a non-empty string")
        if not owner_name:
            raise ValueError("Owner name must not be empty")
        if credit_limit < 0:
            raise ValueError("Credit limit cannot be negative")
        self.iban: str = iban
        self.balance: float = balance
        self.owner_name: str = owner_name
        self.currency: str = currency
        self.account_type: str = account_type
        self.is_active: bool = is_active
        self.credit_limit: float = credit_limit
 
    def withdraw(self, amount: float) -> bool:
        if not self.is_active or amount <= 0:
            logger.debug("Withdraw rejected on %s (active=%s, amount=%s)", self.iban, self.is_active, amount)
            return False
        if amount > (self.balance + self.credit_limit):
            logger.debug("Withdraw rejected on %s: insufficient funds", self.iban)
            return False
        self.balance -= amount
        return True
 
    def deposit(self, amount: float) -> bool:
        if self.is_active and amount > 0:
            self.balance += amount
            return True
        logger.debug("Deposit rejected on %s (active=%s, amount=%s)", self.iban, self.is_active, amount)
        return False