# [НОВИЙ ФАЙЛ] доданий під час рефакторингу
import json
import os
import tempfile
import unittest

from account import Account
from data_loader import JsonDataLoader
from exceptions import DataLoadError
from interfaces import IDataLoader, IReportGenerator
from report import Report


class DataLoaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, name, content):
        path = os.path.join(self.tmp.name, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content if isinstance(content, str) else json.dumps(content, ensure_ascii=False))
        return path

    def loader(self, accounts=None, transactions=None):
        return JsonDataLoader(self.write("a.json", accounts if accounts is not None else []),
                              self.write("t.json", transactions if transactions is not None else []))

    def test_implements_interface(self):
        self.assertIsInstance(self.loader(), IDataLoader)

    def test_load_accounts(self):
        accs = self.loader(accounts=[{"iban": "UA1", "balance": 10, "owner_name": "Іван", "credit_limit": 5}]).load_accounts()
        self.assertEqual(len(accs), 1)
        self.assertEqual((accs[0].iban, accs[0].balance, accs[0].currency, accs[0].credit_limit),
                         ("UA1", 10.0, "UAH", 5.0))

    def test_invalid_account_records_are_skipped(self):
        data = [{"iban": "UA1", "balance": 1, "owner_name": "ok"},
                {"balance": 1, "owner_name": "no iban"},
                {"iban": "UA2", "balance": "abc", "owner_name": "bad balance"},
                "not a dict"]
        with self.assertLogs("data_loader", level="WARNING") as cm:
            accs = self.loader(accounts=data).load_accounts()
        self.assertEqual([a.iban for a in accs], ["UA1"])
        self.assertEqual(len([m for m in cm.output if "Skipping" in m]), 3)

    def test_load_transactions_are_pending(self):
        txs = self.loader(transactions=[{"from_iban": "A", "to_iban": "B", "amount": 5}]).load_transactions()
        self.assertEqual(len(txs), 1)
        self.assertEqual(txs[0].status, "pending")

    def test_invalid_transaction_records_are_skipped(self):
        data = [{"from_iban": "A", "to_iban": "B"}, {"from_iban": "A", "to_iban": "B", "amount": -5}]
        with self.assertLogs("data_loader", level="WARNING"):
            self.assertEqual(self.loader(transactions=data).load_transactions(), [])

    def test_missing_file(self):
        with self.assertRaises(DataLoadError):
            JsonDataLoader("/no/such/a.json", "/no/such/t.json").load_accounts()

    def test_broken_json(self):
        loader = JsonDataLoader(self.write("a.json", "{not json"), self.write("t.json", "[]"))
        with self.assertRaises(DataLoadError):
            loader.load_accounts()

    def test_json_must_be_list(self):
        with self.assertRaises(DataLoadError):
            self.loader(accounts={"iban": "x"}).load_accounts()


class ReportTests(unittest.TestCase):
    def test_summary_with_currencies(self):
        r = Report("Т", [Account("1", 100, "Іван"), Account("2", 50.5, "Анна"), Account("3", 7, "Олег", currency="USD")])
        self.assertIsInstance(r, IReportGenerator)
        s = r.generate_summary()
        self.assertIn("Report: Т", s)
        self.assertIn("Owner: Іван, Balance: 100.00 UAH", s)
        self.assertIn("Total Balance (UAH): 150.50", s)
        self.assertIn("Total Balance (USD): 7.00", s)

    def test_empty_report(self):
        self.assertIn("No accounts", Report("Т", []).generate_summary())


if __name__ == "__main__":
    unittest.main()