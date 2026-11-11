# Список змін у лабораторній роботі

## Нові файли
- `exceptions.py` — власні винятки
- `interfaces.py` — інтерфейси (IValidator, ITransactionLogger, IReportGenerator, IDataLoader, IBank)
- `logging_config.py` — налаштування логування
- `data_loader.py` — читання рахунків і транзакцій з JSON
- `main.py` — замінює `Лаб_1.py`, тут збираються залежності (DI)
- `tests/`
  - `__init__.py` (порожній)
  - `test_account_transaction.py`
  - `test_bank.py`
  - `test_logger.py`
  - `test_validator.py`
  - `test_data_loader_report.py`
  - `test_main.py`
- `data/accounts.json`, `data/transactions.json` — вхідні дані
- `README.md` — інструкція із запуску
- `CHANGES.md` — цей файл

## Змінені файли (з оригіналу)
- `account.py` — перевірка вхідних даних, логування
- `transaction.py` — перевірка статусу й суми, розширений `__str__`
- `validator.py` — реалізує `IValidator`, логування відмов
- `logger.py` — реалізує `ITransactionLogger`, обробка помилок запису
- `report.py` — реалізує `IReportGenerator`, підсумки по кожній валюті
- `bank.py` — DI, правильний розрахунок комісії, власні винятки

## Видалено / замінено
- `Лаб_1.py` → `main.py`