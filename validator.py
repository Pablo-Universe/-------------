from typing import Any


class BaseValidator:

    def validate(self, data: Any) -> bool:
        raise NotImplementedError("Subclasses must implement validate method")


class Validator(BaseValidator):

    def __init__(
        self,
        min_transfer: float = 1.0,
        max_transfer: float = 100000.0,
        require_active_account: bool = True,
        valid_iban_length: int = 29,
        country_code: str = "UA",
        max_daily_limit: float = 500000.0,
    ) -> None:
        self._min_transfer: float = min_transfer
        self._max_transfer: float = max_transfer
        self._require_active_account: bool = require_active_account
        self._valid_iban_length: int = valid_iban_length
        self._country_code: str = country_code
        self._max_daily_limit: float = max_daily_limit

    @property
    def min_transfer(self) -> float:
        return self._min_transfer

    @property
    def max_transfer(self) -> float:
        return self._max_transfer

    def validate(
        self,
        amount: float,
        account_active: bool,
        iban: str,
        daily_total: float,
    ) -> bool:
        if self._require_active_account and not account_active:
            return False
        if amount < self._min_transfer or amount > self._max_transfer:
            return False
        if len(iban) != self._valid_iban_length or not iban.startswith(
            self._country_code
        ):
            return False
        if daily_total + amount > self._max_daily_limit:
            return False
        return True