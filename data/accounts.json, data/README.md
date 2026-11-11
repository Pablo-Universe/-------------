# Лабораторна 1 — банківська система

Запуск:            `python main.py`
Тести:             `python -m unittest discover -v`
Свої дані:         `python main.py --accounts data/accounts.json --transactions data/transactions.json`

Архітектура: `interfaces.py` (IValidator, ITransactionLogger, IReportGenerator, IDataLoader, IBank) —
конкретні класи реалізують ці інтерфейси, а `Bank` отримує валідатор і журнал через конструктор (DI).
Складання об'єктів відбувається лише в `main.py`.