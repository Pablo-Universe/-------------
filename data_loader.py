# [НОВИЙ ФАЙЛ] доданий під час рефакторингу
import json
import logging
from pathlib import Path
from typing import Any, List

from account import Account
from exceptions import DataLoadError
from interfaces import IDataLoader
from transaction import Transaction

logger = logging.getLogger(__name__)


class JsonDataLoader(IDataLoader):
    """Читає рахунки та транзакції з JSON-файлів."""

    def __init__(self, accounts_path: str, transactions_path: str) -> None:
        self._accounts_path = Path(accounts_path)
        self._transactions_path = Path(transactions_path)

    @staticmethod
    def _read_list(path: Path) -> List[Any]:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as e:
            raise DataLoadError(f"File not found: {path}") from e
        except json.JSONDecodeError as e:
            raise DataLoadError(f"Invalid JSON in {path}: {e}") from e
        except OSError as e:
            raise DataLoadError(f"Cannot read {path}: {e}") from e
        if not isinstance(data, list):
            raise DataLoadError(f"{path} must contain a JSON list")
        return data

    def load_accounts(self) -> List[Account]:
        accounts: List[Account] = []
        for i, rec in enumerate(self._read_list(self._accounts_path), start=1):
            try:
                accounts.append(Account(
                    iban=rec["iban"], balance=float(rec["balance"]), owner_name=rec["owner_name"],
                    currency=rec.get("currency", "UAH"), account_type=rec.get("account_type", "debit"),
                    is_active=bool(rec.get("is_active", True)), credit_limit=float(rec.get("credit_limit", 0.0))))
            except (KeyError, TypeError, ValueError, AttributeError) as e:
                logger.warning("Skipping invalid account record #%d in %s: %r", i, self._accounts_path, e)
        logger.info("Loaded %d account(s) from %s", len(accounts), self._accounts_path)
        return accounts

    def load_transactions(self) -> List[Transaction]:
        transactions: List[Transaction] = []
        for i, rec in enumerate(self._read_list(self._transactions_path), start=1):
            try:
                transactions.append(Transaction(
                    from_iban=rec["from_iban"], to_iban=rec["to_iban"], amount=float(rec["amount"]),
                    status="pending", currency=rec.get("currency", "UAH"),
                    tx_type=rec.get("tx_type", "transfer"), description=rec.get("description", "")))
            except (KeyError, TypeError, ValueError, AttributeError) as e:
                logger.warning("Skipping invalid transaction record #%d in %s: %r", i, self._transactions_path, e)
        logger.info("Loaded %d transaction(s) from %s", len(transactions), self._transactions_path)
        return transactions