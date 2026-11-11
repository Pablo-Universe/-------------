# [НОВИЙ ФАЙЛ] доданий під час рефакторингу
import os
import tempfile
import unittest

from interfaces import ITransactionLogger
from logger import Logger
from transaction import Transaction


def tx(amount=1.0):
    return Transaction("A", "B", amount, "completed")


class LoggerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "sub", "tx.log")
        self.addCleanup(self.tmp.cleanup)

    def read(self):
        with open(self.path, encoding="utf-8") as f:
            return f.read().splitlines()

    def test_implements_interface(self):
        self.assertIsInstance(Logger(self.path), ITransactionLogger)

    def test_auto_save_writes_and_clears_buffer(self):
        log = Logger(self.path)
        log.add_record(tx(10))
        self.assertEqual(len(self.read()), 1)
        self.assertEqual(log.history, [])

    def test_appends_not_duplicates(self):
        log = Logger(self.path)
        log.add_record(tx(1.0))
        log.add_record(tx(2.0))
        lines = self.read()
        self.assertEqual(len(lines), 2)
        self.assertIn("1.0", lines[0])
        self.assertIn("2.0", lines[1])

    def test_manual_save(self):
        log = Logger(self.path, auto_save=False)
        log.add_record(tx())
        self.assertEqual(len(log.history), 1)
        self.assertFalse(os.path.exists(self.path))
        self.assertTrue(log.save_to_file())
        self.assertEqual(len(self.read()), 1)

    def test_max_entries_drops_oldest(self):
        log = Logger(self.path, max_entries=2, auto_save=False)
        for a in (1, 2, 3):
            log.add_record(tx(a))
        self.assertEqual([t.amount for t in log.history], [2, 3])

    def test_write_error_keeps_buffer(self):
        log = Logger(self.tmp.name, auto_save=False)  # шлях — це тека, відкрити як файл неможливо
        log.add_record(tx())
        with self.assertLogs("logger", level="ERROR"):
            self.assertFalse(log.save_to_file())
        self.assertEqual(len(log.history), 1)

    def test_invalid_max_entries(self):
        with self.assertRaises(ValueError):
            Logger(self.path, max_entries=0)


if __name__ == "__main__":
    unittest.main()