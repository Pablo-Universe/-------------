import logging
 
from interfaces import IValidator
 
logger = logging.getLogger(__name__)
 
 
class Validator(IValidator):
 
    def __init__(self, min_transfer: float = 1.0, max_transfer: float = 100000.0,
                 require_active_account: bool = True, valid_iban_length: int = 29,
                 country_code: str = "UA", max_daily_limit: float = 500000.0) -> None:
        if min_transfer > max_transfer:
            raise ValueError("min_transfer cannot exceed max_transfer")
        self._min_transfer = min_transfer
        self._max_transfer = max_transfer
        self._require_active_account = require_active_account
        self._valid_iban_length = valid_iban_length
        self._country_code = country_code
        self._max_daily_limit = max_daily_limit
 
    @property
    def min_transfer(self) -> float:
        return self._min_transfer
 
    @property
    def max_transfer(self) -> float:
        return self._max_transfer
 
    def validate(self, amount: float, account_active: bool, iban: str, daily_total: float) -> bool:
        if self._require_active_account and not account_active:
            logger.warning("Validation failed: account %s is inactive", iban)
            return False
        if amount < self._min_transfer or amount > self._max_transfer:
            logger.warning("Validation failed: amount %s outside [%s, %s]", amount, self._min_transfer, self._max_transfer)
            return False
        if len(iban) != self._valid_iban_length or not iban.startswith(self._country_code):
            logger.warning("Validation failed: invalid IBAN %r", iban)
            return False
        if daily_total + amount > self._max_daily_limit:
            logger.warning("Validation failed: daily limit %s exceeded for %s", self._max_daily_limit, iban)
            return False
        return True