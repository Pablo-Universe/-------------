from datetime import datetime


class Transaction:

    def __init__(self, from_iban: str, to_iban: str, amount: float, status: str, currency: str = "UAH", tx_type: str = "transfer", description: str = "",) -> None:
        self._from_iban: str = from_iban
        self._to_iban: str = to_iban
        self._amount: float = amount
        self._status: str = status
        self._date: datetime = datetime.now()
        self._currency: str = currency
        self._tx_type: str = tx_type
        self._description: str = description

    @property
    def from_iban(self) -> str:
        return self._from_iban

    @property
    def to_iban(self) -> str:
        return self._to_iban

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        allowed_statuses = ["pending", "completed", "failed"]
        if value not in allowed_statuses:
            raise ValueError(f"Invalid status. Allowed statuses are: {allowed_statuses}")
        self._status = value

    @property
    def date(self) -> datetime:
        return self._date

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def tx_type(self) -> str:
        return self._tx_type

    @property
    def description(self) -> str:
        return self._description

    def __str__(self) -> str:
        return f"Transaction({self.tx_type}, {self.amount} {self.currency}, Status: {self.status})"