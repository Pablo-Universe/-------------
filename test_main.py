# [НОВИЙ ФАЙЛ] доданий під час рефакторингу
import contextlib
import io
import json
import os
import tempfile
import unittest

import main as app


class MainIntegrationTests(unittest.TestCase):
    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            acc, trx = os.path.join(d, "a.json"), os.path.join(d, "t.json")
            with open(acc, "w") as f:
                json.dump([{"iban": "UA300000000000012345678901231", "balance": 1000, "owner_name": "A"},
                           {"iban": "UA300000000000012345678901241", "balance": 0, "owner_name": "B"}], f)
            with open(trx, "w") as f:
                json.dump([{"from_iban": "UA300000000000012345678901231",
                            "to_iban": "UA300000000000012345678901241", "amount": 100}], f)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = app.main(["--accounts", acc, "--transactions", trx,
                                 "--tx-log", os.path.join(d, "tx.log"), "--app-log", os.path.join(d, "app.log")])
            self.assertEqual(code, 0)
            self.assertIn("Total Balance (UAH): 999.00", out.getvalue())  # 1000 - 1 комісія банку
            self.assertTrue(os.path.getsize(os.path.join(d, "tx.log")) > 0)

    def test_missing_data_file_returns_error_code(self):
        with tempfile.TemporaryDirectory() as d:
            code = app.main(["--accounts", "/no/file.json", "--transactions", "/no/file2.json",
                             "--tx-log", os.path.join(d, "tx.log"), "--app-log", os.path.join(d, "app.log")])
            self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()