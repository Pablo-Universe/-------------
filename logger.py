import logging
from datetime import datetime
from pathlib import Path
from typing import List

from interfaces import ITransactionLogger
from transaction import Transaction

_log = logging.getLogger(__name__)


class Logger(ITransactionLogger):
    """Журнал транзакцій: буфер у пам'яті + запис у файл."""

    def __init__(self, log_file_path: str, max_entries: int = 1000, auto_save: bool = True) -> None:
        if max_entries <= 0:
            raise ValueError("max_entries must be positive")
        self._history: List[Transaction] = []
        self._log_file_path = log_file_path
        self._max_entries = max_entries
        self._auto_save = auto_save
        self._created_at = datetime.now()
        self._last_updated = datetime.now()

    def add_record(self, transaction: Transaction) -> None:
        if len(self._history) >= self._max_entries:
            dropped = self._history.pop(0)
            _log.warning("History is full, dropping oldest record: %s", dropped)
        self._history.append(transaction)
        self._last_updated = datetime.now()
        if self._auto_save:
            self.save_to_file()

    def save_to_file(self) -> bool:
        """Дописує буфер у файл. При помилці буфер зберігається. Повертає True/False."""
        try:
            Path(self._log_file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self._log_file_path, "a", encoding="utf-8") as f:
                for transaction in self._history:
                    f.write(f"{transaction}\n")
        except OSError as e:
            _log.error("Error saving logs to file %s: %s", self._log_file_path, e)
            return False
        self._history.clear()
        return True

    @property
    def history(self) -> List[Transaction]:
        return self._history

    @property
    def last_updated(self) -> datetime:
        return self._last_updated