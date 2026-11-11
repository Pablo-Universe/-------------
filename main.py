# [НОВИЙ ФАЙЛ] доданий під час рефакторингу
"""Composition root: тут створюються всі залежності та передаються у класи (DI)."""
import argparse
import logging
import sys
from pathlib import Path

from bank import Bank
from data_loader import JsonDataLoader
from exceptions import BankError, DataLoadError
from interfaces import IDataLoader, IReportGenerator, ITransactionLogger, IValidator
from logger import Logger
from logging_config import setup_logging
from report import Report
from validator import Validator

BASE = Path(__file__).parent
log = logging.getLogger("main")


def run(loader: IDataLoader, validator: IValidator, tx_logger: ITransactionLogger) -> IReportGenerator:
    bank = Bank("Національний Банк", "300001", ["USD", "EUR", "UAH"], validator, tx_logger, 0.01)

    for account in loader.load_accounts():
        try:
            bank.add_account(account)
        except BankError as e:
            log.warning("Account skipped: %s", e)

    ok = failed = 0
    for transaction in loader.load_transactions():
        try:
            bank.process_transaction(transaction)
            ok += 1
        except BankError as e:
            failed += 1
            print(f"Помилка транзакції: {e}")
    print(f"Оброблено успішно: {ok}, з помилками: {failed}, комісія банку: {bank.collected_commission:.2f}")
    return Report("Щоденний звіт", list(bank.accounts.values()))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Банківська система (Лаб 1)")
    p.add_argument("--accounts", default=str(BASE / "data" / "accounts.json"))
    p.add_argument("--transactions", default=str(BASE / "data" / "transactions.json"))
    p.add_argument("--tx-log", default=str(BASE / "transactions.log"))
    p.add_argument("--app-log", default=str(BASE / "app.log"))
    args = p.parse_args(argv)

    setup_logging(args.app_log)
    try:
        report = run(JsonDataLoader(args.accounts, args.transactions),
                     Validator(min_transfer=10.0, max_transfer=50000.0),
                     Logger(args.tx_log))
    except DataLoadError as e:
        log.error("Не вдалося завантажити дані: %s", e)
        return 1
    print(report.generate_summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())