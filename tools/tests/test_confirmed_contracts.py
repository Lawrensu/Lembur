"""Regression tests for confirmed design sections 4.1, 4.2 and 4.3.

Load the business numbers module by path. Its name avoids shadowing
Python's standard library numbers module.
"""
import decimal
import importlib.util
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

from hours import build_hours
from plan import Plan
from reconcile import close_week, reconcile

spec = importlib.util.spec_from_file_location("lembur_numbers_test", TOOLS / "business_numbers.py")
numbers_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(numbers_tool)


def plan_fixture():
    return Plan({
        "products": [
            {"product_id": "P01", "name": "Keychain", "price_rm": "10.00",
             "material_cost_rm": "1.00", "packaging_cost_rm": "1.00",
             "minutes_per_unit": "20"},
            {"product_id": "P02", "name": "Bracelet", "price_rm": "10.00",
             "material_cost_rm": "1.00", "packaging_cost_rm": "1.00",
             "minutes_per_unit": "35"},
        ],
        "channels": [{"channel": "online", "fee_percent": "0",
                      "fee_per_order_rm": "0", "shipping_cost_per_order_rm": "0",
                      "fulfilment_minutes_per_order": "5"}],
        "assumptions": [{"admin_hours_per_week": "2", "planned_margin_percent": "20",
                         "target_hourly_rate_rm": "10.00"}],
        "change_log": [],
    })


def sale(number=1, **changes):
    row = {"txn_id": "T%04d" % number, "date": "2026-10-05", "type": "income",
           "category": "sales", "product_id": "P01", "quantity": "3",
           "amount_rm": "10.00", "channel": "online", "payment_method": "cash",
           "reconciliation_status": "cash_declared", "bank_reference": "",
           "counterparty": "demo", "reference": "", "notes": ""}
    row.update(changes)
    return row


def historic_line(day, entry_id):
    return {"entry_id": entry_id, "date": day, "person": "person_1",
            "activity": "event", "product_id": "", "quantity": "", "minutes": "60",
            "source": "stated", "assumption_ref": "message." + day}


class EventTests(unittest.TestCase):
    def build(self, event):
        return build_hours([], [], plan_fixture(), "2026-W41", events=[event])

    def test_clock_times_are_computed(self):
        lines, warnings = self.build({"date": "2026-10-05", "start": "16:00", "end": "21:00"})
        self.assertEqual(warnings, [])
        self.assertEqual(lines[0]["minutes"], "300")

    def test_stated_hours_are_computed(self):
        lines, warnings = self.build({"date": "2026-10-05", "stated_hours": "1.5 hours"})
        self.assertEqual(warnings, [])
        self.assertEqual(lines[0]["minutes"], "90")

    def test_unreadable_and_nonincreasing_times_need_review(self):
        inputs = [{"start": "21:00", "end": "16:00"},
                  {"start": "16:00", "end": "16:00"},
                  {"start": "24:00", "end": "25:00"},
                  {"stated_hours": "unclear"}, {}, {"minutes": 300}]
        for values in inputs:
            with self.subTest(values=values):
                lines, warnings = self.build({"date": "2026-10-05", **values})
                self.assertEqual(lines, [])
                self.assertEqual(len(warnings), 1)
                self.assertIn("2026-10-05", warnings[0])
                self.assertIn("message.2026-10-05", warnings[0])

    def test_repeated_event_not_added_twice(self):
        event = {"date": "2026-10-05", "start": "16:00", "end": "21:00"}
        first, _ = self.build(event)
        second, _ = build_hours([], first, plan_fixture(), "2026-W41", events=[event])
        self.assertEqual(first, second)


class HoursIdTests(unittest.TestCase):
    def test_only_open_week_ids_change_without_collisions(self):
        previous = historic_line("2026-09-30", "H0001")
        later = historic_line("2026-10-12", "H0003")
        original = [previous.copy(), later.copy()]
        first, _ = build_hours([sale()], original, plan_fixture(), "2026-W41", payslip_day=True)
        outside = [line for line in first if line["date"] in (previous["date"], later["date"])]
        self.assertEqual(outside, [previous, later])
        ids = [line["entry_id"] for line in first]
        self.assertEqual(len(ids), len(set(ids)))
        second, _ = build_hours([sale()], first, plan_fixture(), "2026-W41", payslip_day=True)
        self.assertEqual(first, second)
        self.assertEqual(original, [previous, later])

    def test_worked_example(self):
        transactions = [sale(i) for i in range(1, 11)]
        transactions[-1].update(product_id="P02", quantity="6")
        transactions[0]["quantity"] = "6"
        transactions.append(sale(11, type="expense", category="materials", amount_rm="32.00"))
        lines, warnings = build_hours(transactions, [], plan_fixture(), "2026-W41",
                                      events=[{"date": "2026-10-10", "stated_hours": "6"}],
                                      payslip_day=True)
        self.assertEqual(warnings, [])
        result = numbers_tool.compute(transactions, lines, plan_fixture(), "2026-W41")
        self.assertEqual(result["minutes"]["total"], 1340)
        self.assertEqual(result["hours"]["total"], "22.3")
        self.assertEqual(result["take_home_rm"], "68.00")
        self.assertEqual(result["hourly_rate_rm"], "3.04")


class CategoryTests(unittest.TestCase):
    def test_leftover_expense_requires_classification(self):
        bank = [{"date": "2026-10-05", "description": "demo supplier", "type": "expense",
                 "amount_rm": "1.00", "bank_reference": "B1"},
                {"date": "2026-10-05", "description": "demo sale", "type": "income",
                 "amount_rm": "2.00", "bank_reference": "B2"}]
        transactions = []
        created = close_week(transactions, bank)
        self.assertEqual([row["category"] for row in created], ["", "sales"])
        with self.assertRaisesRegex(ValueError, "classification"):
            numbers_tool.compute(transactions, [], plan_fixture(), "2026-W41")
        created[0]["category"] = "materials"
        self.assertEqual(numbers_tool.compute(transactions, [], plan_fixture(), "2026-W41")
                         ["take_home_rm"], "1.00")
        self.assertEqual(close_week(transactions, bank), [])

    def test_any_counted_empty_category_blocks(self):
        row = sale(category="", date="2026-09-30")
        with self.assertRaisesRegex(ValueError, "classification"):
            numbers_tool.compute([row], [], plan_fixture(), "2026-W41")
        for changes in ({"reconciliation_status": "duplicate"}, {"amount_rm": ""}):
            numbers_tool.compute([{**row, **changes}], [], plan_fixture(), "2026-W41")

    def test_defensive_checks_for_new_and_retry_rows(self):
        for status in ("", "unmatched"):
            for changes in ({"quantity": ""}, {"type": "expense"},
                            {"category": "unknown"}, {"payment_method": "unknown"}):
                row = sale(reconciliation_status=status, **changes)
                reconcile([row], [])
                self.assertEqual(row["reconciliation_status"], "needs_review")
                self.assertTrue(row["notes"])


if __name__ == "__main__":
    unittest.main()
