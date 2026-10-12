"""Tests written from docs/SYSTEM_DESIGN.md, Conventions, Data Model and Deterministic Tools, not from the code.

Every expected value here was worked out by hand from the design. Known limits
recorded in the design are not asserted here.
"""
import decimal  # stdlib decimal must load before the flat modules
import copy
import importlib.util
import json
from decimal import Decimal as D
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import conventions as c
from hours import build_hours
from plan import Plan
from reconcile import close_week, reconcile, resolve, review_list

# Loaded by path under either name, so a rename of the module does not break this file.
NUMBERS = next(p for p in (TOOLS / "business_numbers.py", TOOLS / "numbers.py")
               if p.exists())
spec = importlib.util.spec_from_file_location("lembur_numbers_design", NUMBERS)
numbers_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(numbers_tool)

WEEK = "2026-W41"
MINUTES_REF = "products.P01.minutes_per_unit"


def plan(change_log=None, **assumptions):
    book = {
        "products": [
            {"product_id": "P01", "name": "Keychain", "price_rm": "12.00",
             "material_cost_rm": "3.00", "packaging_cost_rm": "0.50",
             "minutes_per_unit": "20"},
            {"product_id": "P02", "name": "Bracelet", "price_rm": "18.00",
             "material_cost_rm": "9.00", "packaging_cost_rm": "1.00",
             "minutes_per_unit": "35"},
        ],
        "channels": [
            {"channel": "bazaar", "fee_percent": "0", "fee_per_order_rm": "0",
             "shipping_cost_per_order_rm": "0", "fulfilment_minutes_per_order": "0"},
            {"channel": "online", "fee_percent": "2.5", "fee_per_order_rm": "0.50",
             "shipping_cost_per_order_rm": "6.00", "fulfilment_minutes_per_order": "5"},
        ],
        "assumptions": [{"admin_hours_per_week": "2", "planned_margin_percent": "40",
                         "target_hourly_rate_rm": "10.00"}],
        "change_log": change_log or [],
    }
    book["assumptions"][0].update(assumptions)
    return Plan(book)


def txn(number, **changes):
    row = {"txn_id": "T%04d" % number, "date": "2026-10-06", "type": "income",
           "category": "sales", "description": "", "product_id": "P01",
           "quantity": "1", "amount_rm": "12.00", "channel": "online",
           "payment_method": "bank_transfer", "counterparty": "", "reference": "",
           "source_file": "", "reconciliation_status": "", "bank_reference": "",
           "notes": ""}
    row.update(changes)
    return row


def expense(number, **changes):
    values = {"type": "expense", "category": "materials", "product_id": "",
              "quantity": "", "channel": "", "amount_rm": "45.00",
              "counterparty": "Kedai"}
    values.update(changes)
    return txn(number, **values)


def bank(reference, **changes):
    line = {"date": "2026-10-06", "description": "", "type": "income",
            "amount_rm": "12.00", "bank_reference": reference}
    line.update(changes)
    return line


def statuses(rows):
    return [row["reconciliation_status"] for row in rows]


class ConventionTests(unittest.TestCase):
    """System design, Conventions."""

    def test_halves_round_away_from_zero(self):
        self.assertEqual(c.round_half_away(D("304.5")), 305)
        self.assertEqual(c.round_half_away(D("-304.5")), -305)
        self.assertEqual(c.round_half_away(D("-304.4")), -304)
        self.assertEqual(c.to_sen("0.005"), 1)
        self.assertEqual(c.to_sen("-0.005"), -1)

    def test_display(self):
        self.assertEqual(c.rm(-5), "-0.05")
        self.assertEqual(c.hours_display(1340), "22.3")
        self.assertEqual(c.hours_display(3), "0.1")
        self.assertEqual(c.hours_display(45), "0.8")

    def test_week_runs_monday_to_sunday(self):
        self.assertEqual(c.iso_week("2026-10-05"), WEEK)
        self.assertEqual(c.iso_week("2026-10-11"), WEEK)
        self.assertEqual(c.iso_week("2026-10-12"), "2026-W42")

    def test_weeks_at_a_year_end(self):
        self.assertEqual(c.iso_week("2026-12-31"), "2026-W53")
        self.assertEqual(c.iso_week("2027-01-03"), "2026-W53")
        self.assertEqual(c.iso_week("2027-01-04"), "2027-W01")
        self.assertEqual(c.iso_week("2024-12-30"), "2025-W01")
        self.assertEqual([d.isoformat() for d in c.week_bounds("2026-W53")],
                         ["2026-12-28", "2027-01-03"])


class ValueInForceTests(unittest.TestCase):
    """System design, Plan files."""

    def test_two_corrections(self):
        log = [{"changed_at": "2026-10-07", "field": MINUTES_REF, "old_value": "20",
                "new_value": "15", "reason": "", "source": "message.2026-10-07"},
               {"changed_at": "2026-10-09", "field": MINUTES_REF, "old_value": "15",
                "new_value": "18", "reason": "", "source": "message.2026-10-09"}]
        p = plan(log)
        p.products["P01"]["minutes_per_unit"] = "18"
        expected = {"2026-10-06": (D("20"), False), "2026-10-07": (D("15"), True),
                    "2026-10-08": (D("15"), True), "2026-10-09": (D("18"), True),
                    "2026-10-11": (D("18"), True)}
        for day, value in expected.items():
            with self.subTest(day=day):
                self.assertEqual(p.in_force(MINUTES_REF, day), value)

    def test_correction_updates_cell_and_log(self):
        p = plan()
        p.correct(MINUTES_REF, "15", "2026-10-07", "keychains take me 15 minutes")
        self.assertEqual(p.in_force(MINUTES_REF, "2026-10-06")[0], D("20"))
        self.assertEqual(p.in_force(MINUTES_REF, "2026-10-07")[0], D("15"))
        self.assertEqual(p.book["products"][0]["minutes_per_unit"], "15")
        self.assertEqual(p.change_log[0]["source"], "message.2026-10-07")

    def test_only_three_values_can_be_corrected(self):
        with self.assertRaises(ValueError):
            plan().correct("products.P01.price_rm", "15", "2026-10-07", "x")


class ReconciliationTests(unittest.TestCase):
    """System design, Reconciliation, steps 1 to 7."""

    def test_cash_is_declared_and_never_a_duplicate(self):
        rows = [txn(1, payment_method="cash"), txn(2, payment_method="cash")]
        reconcile(rows, [])
        self.assertEqual(statuses(rows), ["cash_declared", "cash_declared"])

    def test_duplicate_names_the_original(self):
        rows = [txn(1, reference="R1", counterparty="Aina"),
                txn(2, reference="R1", counterparty="Aina")]
        reconcile(rows, [bank("R1")])
        self.assertEqual(statuses(rows), ["matched", "duplicate"])
        self.assertIn("T0001", rows[1]["notes"])

    def test_amount_mismatch_uses_the_bank_amount_and_keeps_both(self):
        rows = [expense(1, reference="REF9")]
        reconcile(rows, [bank("REF9", type="expense", amount_rm="54.00")])
        self.assertEqual((rows[0]["reconciliation_status"], rows[0]["amount_rm"],
                          rows[0]["bank_reference"]), ("needs_review", "54.00", "REF9"))
        self.assertIn("45.00", rows[0]["notes"])
        self.assertIn("54.00", rows[0]["notes"])

    def test_copy_of_a_mismatched_receipt_in_the_same_run(self):
        rows = [expense(1, reference="REF9"), expense(2, reference="REF9")]
        reconcile(rows, [bank("REF9", type="expense", amount_rm="54.00")])
        self.assertEqual(statuses(rows), ["needs_review", "duplicate"])

    def test_reference_of_the_other_type_is_not_matched(self):
        rows = [txn(1, reference="X1")]
        reconcile(rows, [bank("X1", type="expense")])
        self.assertEqual(statuses(rows), ["unmatched"])

    def test_amount_match_window_is_one_day(self):
        for bank_date, expected in (("2026-10-05", "matched"), ("2026-10-07", "matched"),
                                    ("2026-10-08", "unmatched")):
            with self.subTest(bank_date=bank_date):
                rows = [txn(1)]
                reconcile(rows, [bank("B1", date=bank_date)])
                self.assertEqual(statuses(rows), [expected])

    def test_shared_candidate_goes_to_the_bookkeeper(self):
        rows = [txn(1, counterparty="A"), txn(2, counterparty="B")]
        lines = [bank("B1")]
        ambiguous = reconcile(rows, lines)
        self.assertEqual(sorted(a["txn_id"] for a in ambiguous), ["T0001", "T0002"])
        resolve(rows, lines, "T0001", "B1", "name on the transfer")
        resolve(rows, lines, "T0002", "", "cannot tell")
        self.assertEqual(statuses(rows), ["ambiguous_resolved", "needs_review"])
        self.assertTrue(all(row["notes"] for row in rows))

    def test_running_again_changes_nothing(self):
        rows = [
            txn(1, payment_method="cash"),
            txn(2, reference="R2", counterparty="Aina"),
            txn(3, reference="R2", counterparty="Aina"),
            expense(4, reference="R4"),
            txn(5, amount_rm="", notes="blurry", reconciliation_status="needs_review"),
            txn(6, amount_rm="30.00", counterparty="Chong"),
            txn(7, quantity=""),
        ]
        lines = [bank("R2"), bank("R4", type="expense", amount_rm="54.00"),
                 bank("B9", type="expense", amount_rm="20.00", description="POS LAJU")]
        reconcile(rows, lines)
        self.assertEqual(statuses(rows), [
            "cash_declared", "matched", "duplicate", "needs_review", "needs_review",
            "unmatched", "needs_review"])
        before = copy.deepcopy(rows)
        self.assertEqual(reconcile(rows, lines), [])
        self.assertEqual(rows, before)

        created = close_week(rows, lines)
        self.assertEqual(
            [(r["txn_id"], r["type"], r["category"], r["payment_method"],
              r["reconciliation_status"], r["bank_reference"]) for r in created],
            [("T0008", "expense", "", "bank_transfer", "unmatched", "B9")])
        before = copy.deepcopy(rows)
        self.assertEqual(reconcile(rows, lines), [])
        self.assertEqual(close_week(rows, lines), [])
        self.assertEqual(rows, before)
        self.assertEqual([r["txn_id"] for r in review_list(rows)],
                         ["T0003", "T0004", "T0005", "T0006", "T0007", "T0008"])

    def test_close_week_refuses_while_a_row_has_no_status(self):
        with self.assertRaises(ValueError):
            close_week([txn(1)], [])

    def test_document_arriving_after_step_seven_stays_unmatched(self):
        lines = [bank("B9", type="expense", amount_rm="20.00")]
        rows = []
        close_week(rows, lines)
        rows.append(expense(2, category="shipping", amount_rm="20.00"))
        reconcile(rows, lines)
        self.assertEqual(statuses(rows), ["unmatched", "unmatched"])


class HoursTests(unittest.TestCase):
    """System design, Hours."""

    EVENT = {"date": "2026-10-10", "start": "16:00", "end": "21:00"}

    def sales(self):
        return [
            txn(1, quantity="2"),
            txn(2, quantity="1", channel="bazaar", payment_method="cash"),
            txn(3, quantity="3"),
            txn(4, date="2026-10-08", quantity="2"),
            txn(5, date="2026-10-08", reconciliation_status="duplicate"),
            txn(6, date="2026-10-08", amount_rm=""),
            txn(7, date="2026-10-12", quantity="9"),
        ]

    def corrected_plan(self):
        p = plan()
        p.correct(MINUTES_REF, "15", "2026-10-07", "faster")
        return p

    def test_line_grain_correction_and_counted_rows(self):
        lines, warnings = build_hours(self.sales(), [], self.corrected_plan(), WEEK,
                                      events=[self.EVENT], payslip_day=True)
        self.assertEqual(warnings, [])
        fulfilment_ref = "channels.online.fulfilment_minutes_per_order"
        self.assertEqual(
            [(l["entry_id"], l["date"], l["activity"], l["product_id"], l["quantity"],
              l["minutes"], l["source"], l["assumption_ref"]) for l in lines],
            [("H0001", "2026-10-06", "production", "P01", "6", "120", "estimate",
              MINUTES_REF),
             ("H0002", "2026-10-06", "fulfilment", "P01", "2", "10", "estimate",
              fulfilment_ref),
             ("H0003", "2026-10-08", "production", "P01", "2", "30", "corrected",
              MINUTES_REF),
             ("H0004", "2026-10-08", "fulfilment", "P01", "1", "5", "estimate",
              fulfilment_ref),
             ("H0005", "2026-10-10", "event", "", "", "300", "stated",
              "message.2026-10-10"),
             ("H0006", "2026-10-11", "admin", "", "", "120", "estimate",
              "assumptions.admin_hours_per_week")])

    def test_two_channels_on_one_day_give_one_line_each(self):
        p = plan()
        p.channels["bazaar"]["fulfilment_minutes_per_order"] = "2"
        rows = [txn(1), txn(2, channel="bazaar"), txn(3, channel="bazaar")]
        lines, _ = build_hours(rows, [], p, WEEK)
        self.assertEqual(
            sorted((l["assumption_ref"], l["quantity"], l["minutes"]) for l in lines
                   if l["activity"] == "fulfilment"),
            [("channels.bazaar.fulfilment_minutes_per_order", "2", "4"),
             ("channels.online.fulfilment_minutes_per_order", "1", "5")])

    def test_admin_line_only_on_payslip_day(self):
        lines, _ = build_hours(self.sales(), [], plan(), WEEK)
        self.assertNotIn("admin", [l["activity"] for l in lines])

    def test_running_again_changes_nothing(self):
        p = self.corrected_plan()
        first, _ = build_hours(self.sales(), [], p, WEEK, events=[self.EVENT],
                               payslip_day=True)
        second, _ = build_hours(self.sales(), copy.deepcopy(first), p, WEEK,
                                events=[self.EVENT], payslip_day=True)
        self.assertEqual(second, first)

    def test_event_outside_the_week_writes_no_line(self):
        lines, warnings = build_hours([], [], plan(), WEEK, events=[
            {"date": "2026-10-12", "start": "16:00", "end": "21:00"}])
        self.assertEqual(lines, [])
        self.assertEqual(len(warnings), 1)


class NumbersTests(unittest.TestCase):
    """System design, Numbers."""

    def week(self):
        rows = [
            txn(1, amount_rm="12.30", reconciliation_status="matched"),
            txn(2, amount_rm="12.30", reconciliation_status="matched"),
            txn(3, quantity="2", amount_rm="24.00", channel="bazaar",
                payment_method="cash", reconciliation_status="cash_declared"),
            expense(4, amount_rm="20.00", reconciliation_status="matched"),
            txn(5, reconciliation_status="duplicate"),
            txn(6, amount_rm="", reconciliation_status="needs_review"),
            txn(7, amount_rm="99.00", date="2026-10-12",
                reconciliation_status="matched"),
        ]
        p = plan()
        lines, _ = build_hours(rows, [], p, WEEK, payslip_day=True)
        return rows, lines, p

    def test_totals_take_home_and_rate(self):
        rows, lines, p = self.week()
        out = numbers_tool.compute(rows, lines, p, WEEK)
        self.assertEqual(dict(out["category_totals_rm"]), {
            "sales": "48.60", "materials": "20.00", "packaging": "0.00",
            "platform_fees": "0.00", "shipping": "0.00", "other_expenses": "0.00"})
        self.assertEqual(out["take_home_rm"], "28.60")
        # production 4 x 20, fulfilment 2 x 5, admin 2 x 60
        self.assertEqual(dict(out["minutes"]), {
            "production": 80, "fulfilment": 10, "event": 0, "admin": 120, "total": 210})
        self.assertEqual(out["shared_minutes"], 120)
        # 2860 sen x 60 / 210 = 817.14 sen
        self.assertEqual(out["hourly_rate_rm"], "8.17")
        # 2860 / 4860 = 58.8 percent
        self.assertEqual(out["plan_versus_reality"]["margin_percent"], 59)

    def test_fee_is_rounded_on_each_row(self):
        rows, lines, p = self.week()
        product = numbers_tool.compute(rows, lines, p, WEEK)["products"][0]
        # each online row: 1230 x 2.5 percent = 30.75, rounded to 31 sen, plus 50
        # and 600. Two rows give 1362 sen.
        self.assertEqual((product["revenue_rm"], product["unit_costs_rm"],
                          product["channel_costs_rm"], product["profit_rm"],
                          product["direct_minutes"]),
                         ("48.60", "14.00", "13.62", "20.98", 90))
        # 2098 sen x 60 / 90 = 1398.67 sen
        self.assertEqual(product["profit_per_hour_rm"], "13.99")

    def test_fee_rounding_differs_from_rounding_the_sum(self):
        # three rows of RM1.10 at 2.5 percent: 2.75 sen each rounds to 3, so 9 sen.
        # Rounding the sum would give 8.25, so 8 sen.
        p = plan()
        p.channels["online"].update(fee_per_order_rm="0", shipping_cost_per_order_rm="0")
        rows = [txn(n, amount_rm="1.10", reconciliation_status="matched")
                for n in (1, 2, 3)]
        out = numbers_tool.compute(rows, [], p, WEEK)
        self.assertEqual(out["products"][0]["channel_costs_rm"], "0.09")

    def test_product_profits_are_not_forced_to_equal_take_home(self):
        rows, lines, p = self.week()
        out = numbers_tool.compute(rows, lines, p, WEEK)
        self.assertNotEqual(out["products"][0]["profit_rm"], out["take_home_rm"])
        self.assertEqual((out["products"][1]["profit_rm"],
                          out["products"][1]["profit_per_hour_rm"],
                          out["products"][1]["loses_money"]), ("0.00", None, False))

    def test_week_without_minutes_or_sales_shows_no_rate_or_margin(self):
        out = numbers_tool.compute([], [], plan(), WEEK)
        self.assertEqual((out["hourly_rate_rm"], out["take_home_rm"],
                          out["plan_versus_reality"]["margin_percent"]),
                         (None, "0.00", None))

    def test_negative_rate(self):
        line = {"entry_id": "H0001", "date": "2026-10-11", "person": "person_1",
                "activity": "admin", "product_id": "", "quantity": "", "minutes": "40",
                "source": "estimate",
                "assumption_ref": "assumptions.admin_hours_per_week"}
        out = numbers_tool.compute(
            [expense(1, amount_rm="10.00", reconciliation_status="matched")],
            [line], plan(), WEEK)
        self.assertEqual(out["hourly_rate_rm"], "-15.00")

    def test_sale_of_a_product_missing_from_the_plan_still_counts_in_take_home(self):
        out = numbers_tool.compute(
            [txn(1, product_id="P99", reconciliation_status="matched")], [], plan(), WEEK)
        self.assertEqual(out["take_home_rm"], "12.00")
        self.assertEqual(len(out["warnings"]), 1)

    def test_return_value_saves_as_json_and_repeats(self):
        rows, lines, p = self.week()
        out = numbers_tool.compute(rows, lines, p, WEEK)
        self.assertEqual(json.loads(json.dumps(out)), json.loads(json.dumps(
            numbers_tool.compute(rows, lines, p, WEEK))))


class DecidedRulesTests(unittest.TestCase):
    """Decided 10 October: the wider classification gate (4.3) and event dates (4.2)."""

    def test_numbers_refuses_a_counted_row_with_a_bad_category(self):
        for label, changes in (("unknown category", {"category": "snacks"}),
                               ("category and type disagree", {"category": "materials"})):
            with self.subTest(label):
                row = txn(1, reconciliation_status="needs_review", **changes)
                with self.assertRaises(ValueError):
                    numbers_tool.compute([row], [], plan(), WEEK)

    def test_rows_that_are_not_counted_never_block_numbers(self):
        for changes in ({"reconciliation_status": "duplicate"}, {"amount_rm": ""}):
            with self.subTest(changes=changes):
                row = txn(1, category="materials", **changes)
                out = numbers_tool.compute([row], [], plan(), WEEK)
                self.assertEqual(out["take_home_rm"], "0.00")

    def test_event_with_a_bad_date_goes_to_review(self):
        for event in ({"date": "10 Oct", "stated_hours": "3"}, {"stated_hours": "3"}):
            with self.subTest(event=event):
                lines, warnings = build_hours([], [], plan(), WEEK, events=[event])
                self.assertEqual(lines, [])
                self.assertEqual(len(warnings), 1)


if __name__ == "__main__":
    unittest.main()
