from datetime import datetime
from account import Account
from bank import Bank
from logger import Logger
from report import Report
from transaction import Transaction
from validator import Validator

# Ініціалізація валідатора, банку та логера
validator = Validator(min_transfer=10.0, max_transfer=50000.0)
bank = Bank("Національний Банк", "300001", ["USD", "EUR", "UAH"], 0.01)
logger = Logger("transactions.log")

# Створення банківських рахунків
account1 = Account("UA300000000000012345678901231", 10000.0, "Іван", "UAH")
account2 = Account("UA300000000000012345678901241", 5000.0, "Анна", "UAH")

# Додавання рахунків до банку
bank.add_account(account1)
bank.add_account(account2)

# Створення транзакції
transaction = Transaction(
    "UA300000000000012345678901231",
    "UA300000000000012345678901241",
    500.0,
    "pending",
    "UAH",
)

# Валідація та обробка транзакції
is_valid = validator.validate(
    transaction.amount,
    account1.is_active,
    transaction.to_iban,
    0.0,
)

if is_valid:
    try:
        bank.process_transaction(transaction)
        logger.add_record(transaction)
        print("Транзакцію успішно оброблено.")
    except ValueError as e:
        print(f"Помилка транзакції: {e}")
else:
    print("Валідація транзакції не пройшла.")

# Генерація звіту
report = Report("Щоденний звіт", list(bank.accounts.values()))
print(report.generate_summary())