import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import schema  # noqa: E402
import sheets  # noqa: E402

def blank(sheet):
    return {name: "" for name in schema.LEDGER_SHEETS[sheet]}


def sample_book():
    sale = blank("transactions")
    sale.update(
        txn_id="T0001", date="2026-10-05", type="income", category="sales",
        description="Kuih tray", product_id="P01", quantity="3",
        amount_rm="45.5", channel="whatsapp", payment_method="cash",
    )
    expense = blank("transactions")
    expense.update(
        txn_id="T0002", date="2026-10-06", type="expense", category="materials",
        description="Flour", amount_rm="12", payment_method="bank_transfer",
        notes="receipt, blurry",
    )
    bank = blank("bank_lines")
    bank.update(
        date="2026-10-06", description="TRANSFER OUT", type="expense",
        amount_rm="12.00", bank_reference="B001",
    )
    hours = blank("hours")
    hours.update(
        entry_id="H0001", date="2026-10-05", person="person_1",
        activity="production", product_id="P01", quantity="3", minutes="90",
        source="derived", assumption_ref="products.P01.minutes_per_unit",
    )
    return {"transactions": [sale, expense], "bank_lines": [bank], "hours": [hours]}


class FormatTests(unittest.TestCase):
    def test_csv_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "ledger")
            sheets.save_book(path, schema.LEDGER_SHEETS, sample_book(), fmt="csv")
            loaded = sheets.load_book(path, schema.LEDGER_SHEETS, fmt="csv")
        self.assertEqual(len(loaded["transactions"]), 2)

    def test_other_formats_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "ledger")
            for fmt in ("xlsx", "auto", "ods"):
                with self.subTest(fmt=fmt):
                    with self.assertRaises(ValueError):
                        sheets.load_book(path, schema.LEDGER_SHEETS, fmt)
                    with self.assertRaises(ValueError):
                        sheets.save_book(path, schema.LEDGER_SHEETS, {}, fmt)
            self.assertEqual(os.listdir(tmp), [])


class CsvTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "workspace", "ledger")

    def test_round_trip(self):
        book = sample_book()
        sheets.save_book(self.path, schema.LEDGER_SHEETS, book, "csv")
        loaded = sheets.load_book(self.path, schema.LEDGER_SHEETS, "csv")
        self.assertEqual(list(loaded), list(schema.LEDGER_SHEETS))
        for sheet, columns in schema.LEDGER_SHEETS.items():
            for row in loaded[sheet]:
                self.assertEqual(list(row), columns)
        self.assertEqual(loaded["transactions"][0]["product_id"], "P01")
        self.assertEqual(loaded["transactions"][0]["notes"], "")
        self.assertEqual(loaded["transactions"][1]["notes"], "receipt, blurry")
        self.assertEqual(loaded["hours"], book["hours"])

    def test_file_name_and_money_two_decimals(self):
        sheets.save_book(self.path, schema.LEDGER_SHEETS, sample_book(), "csv")
        csv_file = os.path.join(self.tmp.name, "workspace", "ledger_transactions.csv")
        self.assertTrue(os.path.isfile(csv_file))
        with open(csv_file, encoding="utf-8", newline="") as handle:
            lines = handle.read().splitlines()
        self.assertEqual(lines[0].split(",")[:2], ["txn_id", "date"])
        self.assertIn(",45.50,", lines[1])
        self.assertIn(",12.00,", lines[2])
        loaded = sheets.load_book(self.path, schema.LEDGER_SHEETS, "csv")
        self.assertEqual(loaded["transactions"][0]["amount_rm"], "45.50")

    def test_missing_file(self):
        loaded = sheets.load_book(self.path, schema.LEDGER_SHEETS, "csv")
        self.assertEqual(loaded, {sheet: [] for sheet in schema.LEDGER_SHEETS})

    def test_empty_rows_skipped(self):
        book = sample_book()
        book["transactions"].insert(1, blank("transactions"))
        sheets.save_book(self.path, schema.LEDGER_SHEETS, book, "csv")
        loaded = sheets.load_book(self.path, schema.LEDGER_SHEETS, "csv")
        self.assertEqual(len(loaded["transactions"]), 2)

    def test_missing_sheet_in_book_gets_header_only(self):
        sheets.save_book(self.path, schema.LEDGER_SHEETS, {}, "csv")
        loaded = sheets.load_book(self.path, schema.LEDGER_SHEETS, "csv")
        self.assertEqual(loaded, {sheet: [] for sheet in schema.LEDGER_SHEETS})
        csv_file = os.path.join(self.tmp.name, "workspace", "ledger_hours.csv")
        with open(csv_file, encoding="utf-8", newline="") as handle:
            self.assertEqual(handle.read().strip(), ",".join(schema.LEDGER_SHEETS["hours"]))

    def test_extra_and_missing_columns(self):
        csv_file = os.path.join(self.tmp.name, "ledger_bank_lines.csv")
        with open(csv_file, "w", encoding="utf-8-sig", newline="") as handle:
            handle.write("bank_reference,junk,amount_rm,date\r\nB9, x ,5,2026-10-01\r\n")
        path = os.path.join(self.tmp.name, "ledger")
        loaded = sheets.load_book(path, {"bank_lines": schema.LEDGER_SHEETS["bank_lines"]}, "csv")
        self.assertEqual(
            loaded["bank_lines"],
            [{"date": "2026-10-01", "description": "", "type": "",
              "amount_rm": "5", "bank_reference": "B9"}],
        )

    def test_empty_money_stays_empty(self):
        book = sample_book()
        book["transactions"][0]["amount_rm"] = ""
        sheets.save_book(self.path, schema.LEDGER_SHEETS, book, "csv")
        loaded = sheets.load_book(self.path, schema.LEDGER_SHEETS, "csv")
        self.assertEqual(loaded["transactions"][0]["amount_rm"], "")


if __name__ == "__main__":
    unittest.main()
