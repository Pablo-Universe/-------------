from datetime import datetime
from typing import List
from transaction import Transaction


class Logger:

    def __init__(
        self,
        log_file_path: str,
        max_entries: int = 1000,
        auto_save: bool = True,
    ) -> None:
        self._history: List[Transaction] = []
        self._log_file_path: str = log_file_path
        self._max_entries: int = max_entries
        self._auto_save: bool = auto_save
        self._created_at: datetime = datetime.now()
        self._last_updated: datetime = datetime.now()

    def add_record(self, transaction: Transaction) -> None:
        if len(self._history) >= self._max_entries:
            self._history.pop(0)
        self._history.append(transaction)
        self._last_updated = datetime.now()
        if self._auto_save:
            self.save_to_file()

    def save_to_file(self) -> None:
        try:
            with open(self._log_file_path, "a") as f:
                for transaction in self._history:
                    f.write(f"{transaction}\n")
            self._history.clear()
        except IOError as e:
            print(f"Error saving logs to file: {e}")

    @property
    def history(self) -> List[Transaction]:
        return self._history

    @property
    def last_updated(self) -> datetime:
        return self._last_updated