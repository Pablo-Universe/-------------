from datetime import datetime
from typing import List
from account import Account


class Report:

    def __init__(self, title: str, accounts: List[Account]) -> None:
        self._title: str = title
        self._accounts: List[Account] = accounts
        self._generated_at: datetime = datetime.now()

    def generate_summary(self) -> str:
        report_lines: List[str] = [
            f"Report: {self._title}",
            f"Generated at: {self._generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "------------------------------",
        ]
        for account in self._accounts:
            report_lines.append(
                f"Owner: {account.owner_name}, Balance: {account.balance} {account.currency}"
            )

        total_balance: float = sum(
            account.balance
            for account in self._accounts
            if account.currency == "UAH"
        )
        report_lines.append("------------------------------")
        report_lines.append(f"Total Balance (UAH): {total_balance}")

        return "\n".join(report_lines)

    @property
    def title(self) -> str:
        return self._title

    @property
    def generated_at(self) -> datetime:
        return self._generated_at