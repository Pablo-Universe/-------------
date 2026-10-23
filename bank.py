from typing import Dict, List
from account import Account
from transaction import Transaction

class Bank:
    def __init__(self, bank_name: str, mfo_code: str, allowed_currencies: List[str], commission_rate: float = 0.01) -> None:
        self._bank_name: str = bank_name
        self._mfo_code: str = mfo_code
        self._allowed_currencies: List[str] = allowed_currencies
        self._accounts: Dict[str, Account] = {}
        self._transactions: List[Transaction] = []
        self._commission_rate: float = commission_rate

    def add_account(self, account: Account) -> None:
        if account.currency not in self._allowed_currencies:
            raise ValueError(f"Currency {account.currency} not supported by this bank")
        self._accounts[account.iban] = account

    def get_account(self, iban: str) -> Account:
        if iban not in self._accounts:
            raise ValueError(f"Account with IBAN {iban} not found")
        return self._accounts[iban]

    def process_transaction(self, transaction: Transaction) -> None:
        from_account = self.get_account(transaction.from_iban)
        to_account = self.get_account(transaction.to_iban)

        if from_account.withdraw(transaction.amount):
            commission = transaction.amount * self._commission_rate
            total_deduction = transaction.amount + commission
            
            if from_account.balance < total_deduction and not isinstance(from_account, Account): # Assuming additional logic needed
                 pass # Placeholder for complex logic
            
            from_account.balance -= commission
            to_account.deposit(transaction.amount)
            transaction.status = "completed"
            self._transactions.append(transaction)
        else:
            transaction.status = "failed"
            raise ValueError("Insufficient funds for transaction")

    @property
    def bank_name(self) -> str:
        return self._bank_name

    @property
    def accounts(self) -> Dict[str, Account]:
        return self._accounts