from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from account import Account
from interfaces import IReportGenerator


class Report(IReportGenerator):

    def __init__(self, title: str, accounts: List[Account]) -> None:
        self._title = title
        self._accounts = accounts
        self._generated_at = datetime.now()

    def generate_summary(self) -> str:
        lines: List[str] = [
            f"Report: {self._title}",
            f"Generated at: {self._generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "------------------------------",
        ]
        totals: Dict[str, float] = defaultdict(float)
        for account in self._accounts:
            lines.append(f"Owner: {account.owner_name}, Balance: {account.balance:.2f} {account.currency}")
            totals[account.currency] += account.balance

        lines.append("------------------------------")
        if not totals:
            lines.append("No accounts")
        for currency in sorted(totals):
            lines.append(f"Total Balance ({currency}): {totals[currency]:.2f}")
        return "\n".join(lines)

    @property
    def title(self) -> str:
        return self._title

    @property
    def generated_at(self) -> datetime:
        return self._generated_at