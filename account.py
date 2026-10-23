# Клас 2: Банківський рахунок


class Account:

    def __init__(self, iban: str, balance: float, owner_name: str, currency: str = "UAH", account_type: str = "debit", is_active: bool = True, credit_limit: float = 0.0,) -> None:
        self.iban: str = iban
        self.balance: float = balance
        self.owner_name: str = owner_name
        self.currency: str = currency
        self.account_type: str = account_type
        self.is_active: bool = is_active
        self.credit_limit: float = credit_limit

    def withdraw(self, amount: float) -> bool:
        if not self.is_active or amount <= 0:
            return False
        if amount > (self.balance + self.credit_limit):
            return False
        self.balance -= amount
        return True

    def deposit(self, amount: float) -> bool:
        if self.is_active and amount > 0:
            self.balance += amount
            return True
        return False