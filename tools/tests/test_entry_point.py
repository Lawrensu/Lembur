"""Entry point acceptance and safety tests from design section 4."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import business_numbers
from plan import Plan
from schema import LEDGER_SHEETS, PLAN_SHEETS
import sheets

WEEK = "2026-W41"


def sale(date="2026-10-05", name="Dana", product="P01", amount="5.00",
         channel="instagram", reference="", source=None, payment="bank_transfer"):
    filename = "order_%s_%s.png" % (date, name.lower())
    return {"date": date, "type": "income", "category": "sales",
            "description": "1 Beaded " + ("keychain" if product == "P01" else "bracelet"),
            "product_id": product, "quantity": "1", "amount_rm": amount,
            "channel": channel, "payment_method": payment, "counterparty": name,
            "reference": reference,
            "source_file": source or "receipts/2026-10/" + filename}


def expense(date, filename, category, amount, supplier, reference, description,
            payment="bank_transfer"):
    return {"date": date, "type": "expense", "category": category,
            "amount_rm": amount, "counterparty": supplier, "reference": reference,
            "description": description, "payment_method": payment,
            "source_file": "receipts/2026-10/" + filename}


def bank(reference="REF-1", date="2026-10-05", amount="5.00", kind="income"):
    return {"date": date, "description": "Transfer from Dana", "type": kind,
            "amount_rm": amount, "bank_reference": reference}


class EntryPointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name) / "workspace"
        (self.workspace / "plan").mkdir(parents=True)
        for name in PLAN_SHEETS:
            shutil.copyfile(ROOT / "data" / "demo" / ("plan_" + name + ".csv"),
                            self.workspace / "plan" / ("plan_" + name + ".csv"))

    def call(self, command, *args, rows=None, code=0):
        argv = [sys.executable, "-B", str(ROOT / "tools" / "lembur.py"),
                command, "--workspace", str(self.workspace), *args]
        if rows is not None:
            argv.extend(["--input", "-"])
        result = subprocess.run(argv, cwd=ROOT, input=None if rows is None else json.dumps(rows),
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertNotIn("Traceback", result.stdout)
        return json.loads(result.stdout)

    def ledger(self):
        return sheets.load_book(self.workspace / "ledger", LEDGER_SHEETS, fmt="csv")

    def snapshot(self):
        return {str(path.relative_to(self.workspace)): path.read_bytes()
                for path in self.workspace.rglob("*") if path.is_file()}

    def issue(self, suffix):
        folder = self.workspace / "payslips"
        folder.mkdir(exist_ok=True)
        (folder / (WEEK + suffix)).write_text("Issued", encoding="utf-8")

    def test_nightly_replay_matches_answer_key(self):
        days = {
            "2026-10-05": [sale(), sale(name="Mira"),
                expense("2026-10-05", "receipt_beads.png", "materials", "18.00",
                        "Demo Bead Nook", "DEMO-OUT-001", "Small bead restock"),
                expense("2026-10-05", "receipt_beads_copy.png", "materials", "18.00",
                        "Demo Bead Nook", "DEMO-OUT-001", "Small bead restock")],
            "2026-10-06": [sale("2026-10-06", "Farah", reference="DEMO-IN-003"),
                sale("2026-10-06", "Hana", "P02", "18.00", reference="DEMO-IN-005"),
                sale("2026-10-06", "Nisa", reference="DEMO-IN-004")],
            "2026-10-07": [sale("2026-10-07", "Iman", reference="DEMO-IN-006"),
                expense("2026-10-07", "receipt_pouches.png", "packaging", "6.00",
                        "Demo Pouch Corner", "DEMO-OUT-002", "Small pouch restock")],
            "2026-10-08": [sale("2026-10-08", "Lina", reference="DEMO-IN-007"),
                sale("2026-10-08", "Rina", "P02", "18.00", "telegram", "DEMO-IN-008"),
                expense("2026-10-08", "receipt_thread_blurred.png", "materials", "",
                        "Demo Thread Stop", "", "Thread refill; total unreadable", "cash")],
            "2026-10-09": [sale("2026-10-09", "Suri", reference="DEMO-IN-009"),
                expense("2026-10-09", "receipt_shipping.png", "shipping", "36.00",
                        "Demo Parcel Desk", "DEMO-OUT-003",
                        "Courier settlement for nine weekly parcels")],
            "2026-10-10": [sale("2026-10-10", name, product, amount, "bazaar",
                                source="receipts/2026-10/message_2026-10-10.txt", payment="cash")
                for name, product, amount in [("Aina", "P01", "5.00"),
                    ("Bella", "P01", "5.00"), ("Citra", "P01", "5.00"),
                    ("Dina", "P02", "18.00")]],
            "2026-10-11": [sale("2026-10-11", "Zahra", reference="DEMO-IN-010")],
        }
        for day, rows in days.items():
            self.call("add-transactions", rows=rows)
            if day == "2026-10-07":
                correction = self.call("correct-plan", "--field", "products.P01.minutes_per_unit",
                    "--new-value", "15", "--changed-at", day,
                    "--reason", "I timed myself today, keychains take 15 minutes not 20")
                self.assertEqual(correction["correction"]["old_value"], "20")
            if day == "2026-10-11":
                self.assertEqual(self.ledger()["transactions"][-1]["amount_rm"], "5.00")
                with (ROOT / "data" / "demo" / "inbox" /
                      "bank_statement_2026-W41_SYNTHETIC.csv").open(encoding="utf-8-sig", newline="") as handle:
                    lines = list(csv.DictReader(handle))
                self.call("add-bank-lines", rows=lines)
            else:
                self.assertEqual(self.ledger()["bank_lines"], [])
            result = self.call("reconcile")
            if day == "2026-10-11":
                self.assertEqual([row["txn_id"] for row in result["ambiguous"]], ["T0001", "T0002"])
                for txn_id, reference, name in [("T0001", "DEMO-IN-001", "Dana"),
                                                ("T0002", "DEMO-IN-002", "Mira")]:
                    self.call("resolve", "--txn-id", txn_id, "--bank-reference", reference,
                              "--reason", "Counterparty %s matches the bank description" % name)
                created = self.call("close-week", "--week", WEEK)
                self.assertEqual([row["txn_id"] for row in created["transactions"]], ["T0020"])
                gate = self.call("numbers", "--week", WEEK, code=1)
                self.assertEqual(gate["txn_ids"], ["T0020"])
                self.call("classify", "--txn-id", "T0020", "--category", "materials",
                          "--reason", "Bank description names the bead materials supplier")
            events = [{"date": day, "start": "10:00", "end": "18:00"}] \
                if day == "2026-10-10" else None
            args = ["--week", WEEK] + (["--payslip-day"] if day == "2026-10-11" else [])
            self.call("hours", *args, rows=events)
            self.call("numbers", "--week", WEEK)
        expected = sheets.load_book(ROOT / "data" / "answer_key" / "ledger", LEDGER_SHEETS, fmt="csv")
        actual = self.ledger()
        columns = ["txn_id", "reconciliation_status", "amount_rm", "bank_reference"]
        self.assertEqual([[row[key] for key in columns] for row in actual["transactions"]],
                         [[row[key] for key in columns] for row in expected["transactions"]])
        self.assertEqual(actual["bank_lines"], expected["bank_lines"])
        self.assertEqual(actual["hours"], expected["hours"])
        saved = json.loads((self.workspace / "audit" / WEEK / "numbers.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["take_home_rm"], "39.50")
        self.assertEqual(saved["minutes"]["total"], 938)
        self.assertEqual(saved["hourly_rate_rm"], "2.53")
        self.assertEqual({row["product_id"]: row["profit_rm"] for row in saved["products"]},
                         {"P01": "-10.50", "P02": "32.00"})
        plan = Plan(sheets.load_book(self.workspace / "plan" / "plan", PLAN_SHEETS, fmt="csv"))
        self.assertEqual(saved, business_numbers.compute(actual["transactions"], actual["hours"], plan, WEEK))
        before = self.snapshot()
        self.assertEqual(self.call("numbers-check", "--week", WEEK), {"equal": True, "differing_keys": []})
        self.assertEqual(before, self.snapshot())
        review = self.call("review", "--week", WEEK)
        self.assertEqual([row["txn_id"] for row in review["transactions"]],
                         ["T0004", "T0012", "T0019", "T0020"])

    def test_classify_all_gate_cases_and_require_type_agreement_and_reason(self):
        for category in ("", "unknown", "materials"):
            with self.subTest(category=category):
                row = sale(name="Customer" + (category or "empty"))
                row["category"] = category
                added = self.call("add-transactions", rows=[row])
                txn_id = added["transactions"][0]["txn_id"]
                gate = self.call("numbers", "--week", WEEK, code=1)
                self.assertIn(txn_id, gate["txn_ids"])
                before = self.snapshot()
                self.call("classify", "--txn-id", txn_id, "--category", "packaging", "--reason", "Wrong", code=1)
                self.call("classify", "--txn-id", txn_id, "--category", "sales", "--reason", "", code=1)
                self.assertEqual(before, self.snapshot())
                result = self.call("classify", "--txn-id", txn_id, "--category", "sales", "--reason", "Sale evidence")
                self.assertEqual(result["transaction"]["category"], "sales")
                self.assertIn("Sale evidence", result["transaction"]["notes"])
        self.call("numbers", "--week", WEEK)

    def test_classify_expense_and_reject_unblocked_or_noncounted_row(self):
        row = expense("2026-10-05", "receipt.png", "sales", "3.00", "Supplier", "", "Materials")
        txn_id = self.call("add-transactions", rows=[row])["transactions"][0]["txn_id"]
        self.call("classify", "--txn-id", txn_id, "--category", "materials", "--reason", "Receipt says materials")
        self.call("classify", "--txn-id", txn_id, "--category", "materials", "--reason", "Again", code=1)
        row = {"category": "unknown", "amount_rm": ""}
        txn_id = self.call("add-transactions", rows=[row])["transactions"][0]["txn_id"]
        self.call("classify", "--txn-id", txn_id, "--category", "sales", "--reason", "Unknown amount", code=1)

    def test_issued_html_and_pdf_lock_only_named_commands(self):
        for suffix in (".html", ".pdf"):
            with self.subTest(suffix=suffix):
                for old in (self.workspace / "payslips").glob("*"):
                    old.unlink()
                self.issue(suffix)
                before = self.snapshot()
                for command in ("hours", "numbers", "close-week"):
                    result = self.call(command, "--week", WEEK, code=1)
                    self.assertEqual(result["week"], WEEK)
                    self.assertIn("issued", result["error"])
                self.assertEqual(before, self.snapshot())
                result = self.call("add-transactions", rows=[sale(name="Late" + suffix[1:])])
                self.assertEqual(result["transactions"][0]["reconciliation_status"], "unmatched")
                self.call("reconcile")
                self.assertEqual(self.ledger()["transactions"][-1]["reconciliation_status"], "unmatched")

    def test_other_issued_week_does_not_lock_open_week(self):
        self.issue(".html")
        self.call("hours", "--week", "2026-W42")
        self.call("numbers", "--week", "2026-W42")
        self.call("close-week", "--week", "2026-W42")

    def test_intake_accepts_incomplete_and_needs_review_rows(self):
        result = self.call("add-transactions", rows=[{}, {"description": "Unreadable receipt",
                    "reconciliation_status": "needs_review", "notes": "Blurred"}])
        self.assertEqual([row["txn_id"] for row in result["transactions"]], ["T0001", "T0002"])
        self.assertEqual(result["transactions"][0]["amount_rm"], "")
        self.assertEqual(result["transactions"][1]["reconciliation_status"], "needs_review")
        self.call("reconcile")
        self.assertEqual(self.ledger()["transactions"][0]["reconciliation_status"], "needs_review")

    def test_intake_refuses_supplied_ids_bank_matches_and_settled_statuses_atomically(self):
        for forbidden in [{"txn_id": ""}, {"txn_id": "T0999"}, {"bank_reference": ""},
                          {"bank_reference": "REF"}, {"reconciliation_status": "matched"},
                          {"reconciliation_status": "cash_declared"}, {"reconciliation_status": "duplicate"}]:
            with self.subTest(forbidden=forbidden):
                before = self.snapshot()
                self.call("add-transactions", rows=[sale(), forbidden], code=1)
                self.assertEqual(before, self.snapshot())

    def test_intake_retries_refuse_existing_sources_but_same_new_message_is_allowed(self):
        source = "receipts/2026-10/message_2026-10-10.txt"
        rows = [sale(name=name, source=source, payment="cash") for name in ("Aina", "Bella")]
        self.call("add-transactions", rows=rows)
        self.call("reconcile")
        before = self.snapshot()
        result = self.call("add-transactions", rows=[sale(name="New"), *rows], code=1)
        self.assertEqual(result["source_files"], [source])
        self.assertEqual(before, self.snapshot())
        result = self.call("add-transactions", rows=[sale(name="New")])
        self.assertEqual(result["transactions"][0]["txn_id"], "T0003")

    def test_bank_intake_skips_identical_and_refuses_conflicts_atomically(self):
        self.call("add-bank-lines", rows=[bank()])
        before = self.snapshot()
        result = self.call("add-bank-lines", rows=[bank()])
        self.assertEqual(result, {"bank_lines": [], "skipped": ["REF-1"]})
        self.assertEqual(before, self.snapshot())
        result = self.call("add-bank-lines", rows=[bank("NEW"), bank(amount="6.00")], code=1)
        self.assertEqual(result["bank_references"], ["REF-1"])
        self.assertEqual(before, self.snapshot())
        result = self.call("add-bank-lines", rows=[bank("NEW"), bank("NEW")])
        self.assertEqual(len(result["bank_lines"]), 1)
        self.assertEqual(result["skipped"], ["NEW"])
        before = self.snapshot()
        self.call("add-bank-lines", rows=[bank("OTHER"), bank("OTHER", amount="7.00")], code=1)
        self.assertEqual(before, self.snapshot())

    def test_close_week_only_converts_unused_lines_inside_week_and_reserves_ids(self):
        self.call("add-transactions", rows=[sale(reference="USED"), sale("2026-10-12", "Next")])
        self.call("add-bank-lines", rows=[bank("USED"), bank("LEFT", kind="expense"),
                                        bank("NEXT", "2026-10-12", kind="expense")])
        self.call("reconcile")
        result = self.call("close-week", "--week", WEEK)
        self.assertEqual([row["bank_reference"] for row in result["transactions"]], ["LEFT"])
        self.assertEqual(result["transactions"][0]["txn_id"], "T0003")
        self.assertEqual(result["transactions"][0]["category"], "")
        self.assertEqual(self.call("close-week", "--week", WEEK)["transactions"], [])
        result = self.call("add-transactions", rows=[sale("2026-10-13", "Another")])
        self.assertEqual(result["transactions"][0]["txn_id"], "T0004")

    def test_late_document_after_bank_close_stays_unmatched(self):
        self.call("add-bank-lines", rows=[bank("LATE", kind="expense")])
        self.call("close-week", "--week", WEEK)
        row = expense("2026-10-05", "late.png", "materials", "5.00", "Supplier", "LATE", "Materials")
        result = self.call("add-transactions", rows=[row])
        self.assertEqual(result["transactions"][0]["reconciliation_status"], "unmatched")
        self.call("reconcile")
        self.assertEqual([row["reconciliation_status"] for row in self.ledger()["transactions"]],
                         ["unmatched", "unmatched"])

    def test_late_document_without_reference_or_source_is_not_rematched(self):
        self.call("add-bank-lines", rows=[bank("OLD", kind="expense")])
        self.call("close-week", "--week", WEEK)
        self.call("add-bank-lines", rows=[bank("UNRELATED", kind="expense")])
        row = expense("2026-10-05", "late.png", "materials", "5.00", "Supplier", "", "Materials")
        del row["source_file"]
        added = self.call("add-transactions", rows=[row])
        self.assertEqual(added["transactions"][0]["reconciliation_status"], "unmatched")
        self.call("reconcile")
        row = self.ledger()["transactions"][-1]
        self.assertEqual(row["reconciliation_status"], "unmatched")
        self.assertEqual(row["bank_reference"], "")

    def test_cash_reference_collision_is_not_a_late_bank_document(self):
        self.call("add-bank-lines", rows=[bank("COLLISION", kind="expense")])
        self.call("close-week", "--week", WEEK)
        row = expense("2026-10-12", "cash.png", "materials", "5.00", "Supplier",
                      "COLLISION", "Materials", payment="cash")
        self.call("add-transactions", rows=[row])
        self.call("reconcile")
        self.assertEqual(self.ledger()["transactions"][-1]["reconciliation_status"], "cash_declared")

    def test_numbers_check_rejects_changed_json_types(self):
        self.call("numbers", "--week", WEEK)
        path = self.workspace / "audit" / WEEK / "numbers.json"
        saved = json.loads(path.read_text(encoding="utf-8"))
        saved["minutes"]["total"] = False
        saved["products"][0]["loses_money"] = 0
        path.write_text(json.dumps(saved), encoding="utf-8")
        before = self.snapshot()
        result = self.call("numbers-check", "--week", WEEK, code=1)
        self.assertEqual(result["differing_keys"], ["minutes", "products"])
        self.assertEqual(before, self.snapshot())

    def test_hours_input_optional_and_event_warnings_are_not_repeated(self):
        self.call("hours", "--week", WEEK)
        events = [{"date": "2026-10-10", "start": "10:00", "end": "18:00", "stated_hours": "8"},
                  {"message_date": "2026-10-10", "stated_hours": "8"},
                  {"date": "2026-10-10", "minutes": 480}]
        first = self.call("hours", "--week", WEEK, rows=events)
        self.assertEqual(len(first["warnings"]), 3)
        self.assertEqual(first["hours"], [])
        self.assertIn("both clock times", first["warnings"][0])
        path = self.workspace / "audit" / WEEK / "review_items.md"
        before = path.read_bytes()
        self.call("hours", "--week", WEEK, rows=events)
        self.assertEqual(before, path.read_bytes())
        review = self.call("review", "--week", WEEK)
        self.assertEqual(review["review_items"], ["* " + item for item in first["warnings"]])

    def test_hours_and_numbers_append_all_product_and_channel_warnings_once(self):
        rows = [sale(name="UnknownProduct", product="P99"), sale(name="UnknownChannel", channel="missing")]
        self.call("add-transactions", rows=rows)
        hours = self.call("hours", "--week", WEEK)
        numbers = self.call("numbers", "--week", WEEK)
        expected = list(dict.fromkeys(["* " + warning for warning in hours["warnings"] + numbers["warnings"]]))
        path = self.workspace / "audit" / WEEK / "review_items.md"
        self.assertEqual(path.read_text(encoding="utf-8").splitlines(), expected)
        before = path.read_bytes()
        self.call("hours", "--week", WEEK)
        self.call("numbers", "--week", WEEK)
        self.assertEqual(before, path.read_bytes())
        before = self.snapshot()
        self.call("numbers-check", "--week", WEEK)
        self.assertEqual(before, self.snapshot())

    def test_numbers_check_reports_changed_and_missing_keys_without_writes(self):
        self.call("numbers", "--week", WEEK)
        path = self.workspace / "audit" / WEEK / "numbers.json"
        saved = json.loads(path.read_text(encoding="utf-8"))
        saved["take_home_rm"] = "wrong"
        del saved["hours"]
        saved["extra"] = "unexpected"
        path.write_text(json.dumps(saved), encoding="utf-8")
        before = self.snapshot()
        result = self.call("numbers-check", "--week", WEEK, code=1)
        self.assertEqual(result, {"equal": False, "differing_keys": ["extra", "hours", "take_home_rm"]})
        self.assertEqual(before, self.snapshot())

    def test_bad_arguments_and_json_return_failure_without_traceback(self):
        self.call("not-a-command", code=1)
        self.call("hours", code=1)
        self.call("hours", "--week", "2026-W99", code=1)
        self.call("add-transactions", rows={"not": "an array"}, code=1)
        self.call("add-transactions", rows=[{"invented_field": "value"}], code=1)
        self.call("resolve", "--txn-id", "T9999", "--bank-reference", "", "--reason", "Unknown", code=1)

    def payslip_input(self, value=None):
        path = Path(self.temp.name) / "payslip_text.json"
        if value is None:
            value = {"debate_summary": "Payroll < Growth & review",
                     "ruling": "Keep the student's time <safe>",
                     "raise_plan": [{"text": "Raise <price>", "draft_file": "approvals/2026-W41/price.txt"},
                                    {"text": "Focus & simplify", "draft_file": "approvals/2026-W41/mix.txt"}]}
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_payslip_fills_saved_figures_and_all_four_design_blocks(self):
        row = sale(name="Needs <review>", product="P99")
        row["description"] = "Needs <review>"
        self.call("add-transactions", rows=[row])
        self.call("reconcile")
        self.call("numbers", "--week", WEEK)
        review_path = self.workspace / "audit" / WEEK / "review_items.md"
        review_path.write_text("* Check <receipt> & message\n* Check second source\n", encoding="utf-8")
        numbers_path = self.workspace / "audit" / WEEK / "numbers.json"
        saved = json.loads(numbers_path.read_text(encoding="utf-8"))
        saved["take_home_rm"] = "123.45"
        saved["products"][0]["name"] = "Keychain <special> & safe"
        saved["products"][0]["loses_money"] = True
        numbers_path.write_text(json.dumps(saved), encoding="utf-8")
        before = self.snapshot()
        input_path = self.payslip_input()
        result = self.call("payslip", "--week", WEEK, "--input", str(input_path),
                           "--template", str(ROOT / "tools" / "tests" / "payslip_template.html"))
        path = self.workspace / "payslips" / (WEEK + ".html")
        self.assertEqual(result, {"payslip": str(path)})
        rendered = path.read_text(encoding="utf-8")
        self.assertIn("Take home RM123.45", rendered)
        self.assertIn('<span id="rate"></span>', rendered)
        self.assertIn('class="loss-true"', rendered)
        self.assertIn('class="loss-false"', rendered)
        self.assertEqual(rendered.count("<article "), 2)
        self.assertIn("Keychain &lt;special&gt; &amp; safe", rendered)
        self.assertIn("Payroll &lt; Growth &amp; review", rendered)
        self.assertIn("&lt;safe&gt;", rendered)
        self.assertIn("T0001 2026-10-05 unmatched", rendered)
        self.assertIn("Needs &lt;review&gt;", rendered)
        self.assertIn("* Check &lt;receipt&gt; &amp; message", rendered)
        self.assertIn("* Check second source", rendered)
        self.assertIn("Raise &lt;price&gt;", rendered)
        self.assertIn('href="approvals/2026-W41/price.txt"', rendered)
        self.assertIn("Focus &amp; simplify", rendered)
        self.assertNotIn("{{", rendered)
        self.assertNotIn("<!-- each", rendered)
        self.assertNotIn("None", rendered)
        after = self.snapshot()
        after.pop(str(Path("payslips") / (WEEK + ".html")))
        self.assertEqual(before, after)
        for command in ("payslip", "hours", "numbers", "close-week"):
            args = ["--week", WEEK]
            if command == "payslip":
                args += ["--input", str(input_path), "--template",
                         str(ROOT / "tools" / "tests" / "payslip_template.html")]
            self.call(command, *args, code=1)
        self.assertEqual(path.read_text(encoding="utf-8"), rendered)

    def test_payslip_empty_blocks_are_removed_and_global_dotted_values_fill(self):
        self.call("numbers", "--week", WEEK)
        path = Path(self.temp.name) / "minimal.html"
        path.write_text("{{category_totals_rm.sales}}|{{hours.total}}|{{hourly_rate_rm}}"
                        "<!-- each products --><b>{{product_id}} {{profit_per_hour_rm}} {{loses_money}}</b><!-- end products -->"
                        "<!-- each review_rows -->{{txn_id}}<!-- end review_rows -->"
                        "<!-- each review_items -->{{text}}<!-- end review_items -->"
                        "<!-- each raise_plan -->{{text}} {{draft_file}}<!-- end raise_plan -->", encoding="utf-8")
        input_path = self.payslip_input({"debate_summary": "", "ruling": "", "raise_plan": []})
        self.call("payslip", "--week", WEEK, "--input", str(input_path), "--template", str(path))
        output = (self.workspace / "payslips" / (WEEK + ".html")).read_text(encoding="utf-8")
        self.assertEqual(output, "0.00|0.0|<b>P01  false</b><b>P02  false</b>")

    def test_payslip_unknown_names_are_reported_before_writing_even_in_empty_blocks(self):
        self.call("numbers", "--week", WEEK)
        input_path = self.payslip_input()
        template = Path(self.temp.name) / "unknown.html"
        template.write_text("{{missing}}<!-- each review_rows -->{{not_a_field}}<!-- end review_rows -->"
                            "<!-- each invented -->{{anything}}<!-- end invented -->", encoding="utf-8")
        before = self.snapshot()
        result = self.call("payslip", "--week", WEEK, "--input", str(input_path),
                           "--template", str(template), code=1)
        self.assertEqual(result["names"], ["invented", "missing", "not_a_field"])
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.workspace / "payslips").exists())

    def test_payslip_refuses_non_design_block_fields(self):
        self.call("numbers", "--week", WEEK)
        input_path = self.payslip_input()
        template = Path(self.temp.name) / "wrong_fields.html"
        template.write_text("<!-- each products -->{{direct_minutes}}<!-- end products -->"
                            "<!-- each raise_plan -->{{recommendation}} {{draft_path}}<!-- end raise_plan -->",
                            encoding="utf-8")
        before = self.snapshot()
        result = self.call("payslip", "--week", WEEK, "--input", str(input_path),
                           "--template", str(template), code=1)
        self.assertEqual(result["names"], ["direct_minutes", "draft_path", "recommendation"])
        self.assertEqual(before, self.snapshot())

    def test_payslip_requires_numbers_file(self):
        before = self.snapshot()
        result = self.call("payslip", "--week", WEEK, "--input", str(self.payslip_input()),
                           "--template", str(ROOT / "tools" / "tests" / "payslip_template.html"), code=1)
        self.assertIn("saved numbers file is missing", result["error"])
        self.assertEqual(result["path"], str(self.workspace / "audit" / WEEK / "numbers.json"))
        self.assertEqual(before, self.snapshot())

    def test_payslip_refuses_pdf_issued_week_before_any_writes(self):
        self.issue(".pdf")
        before = self.snapshot()
        result = self.call("payslip", "--week", WEEK, "--input", str(self.payslip_input()), code=1)
        self.assertIn("issued", result["error"])
        self.assertEqual(before, self.snapshot())

    def test_payslip_default_template_path_and_missing_template_are_read_only(self):
        self.call("numbers", "--week", WEEK)
        input_path = self.payslip_input()
        result = subprocess.run([sys.executable, "-B", str(ROOT / "tools" / "lembur.py"),
            "payslip", "--workspace", str(self.workspace), "--week", WEEK,
            "--input", str(input_path)], cwd=self.temp.name, text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")
        self.assertIn("payslip_template.html", json.loads(result.stdout)["error"])
        self.assertFalse((self.workspace / "payslips").exists())

    def test_payslip_bad_input_or_unclosed_block_never_writes(self):
        self.call("numbers", "--week", WEEK)
        template = ROOT / "tools" / "tests" / "payslip_template.html"
        before = self.snapshot()
        for value in ({}, {"debate_summary": 1, "ruling": "", "raise_plan": []},
                      {"debate_summary": "", "ruling": "", "raise_plan": [{"text": "Missing draft"}]}):
            self.call("payslip", "--week", WEEK, "--input", str(self.payslip_input(value)),
                      "--template", str(template), code=1)
            self.assertEqual(before, self.snapshot())
        broken = Path(self.temp.name) / "broken.html"
        broken.write_text("<!-- each products -->{{name}}", encoding="utf-8")
        self.call("payslip", "--week", WEEK, "--input", str(self.payslip_input()),
                  "--template", str(broken), code=1)
        self.assertEqual(before, self.snapshot())

    def test_correct_plan_refuses_invalid_or_negative_values_before_writing(self):
        before = self.snapshot()
        for value in ("unreadable", "", "-1", "-0.5", "NaN", "sNaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                result = self.call("correct-plan", "--field", "products.P01.minutes_per_unit",
                                   "--new-value=" + value, "--changed-at", "2026-10-07",
                                   "--reason", "Timed production", code=1)
                self.assertIn("number", result["error"])
                self.assertEqual(before, self.snapshot())

    def test_correct_plan_refuses_equal_values_and_retries_without_new_log_rows(self):
        before = self.snapshot()
        self.call("correct-plan", "--field", "products.P01.minutes_per_unit",
                  "--new-value", "20.0", "--changed-at", "2026-10-07",
                  "--reason", "No change", code=1)
        self.assertEqual(before, self.snapshot())
        self.call("correct-plan", "--field", "products.P01.minutes_per_unit",
                  "--new-value", "15", "--changed-at", "2026-10-07", "--reason", "Timed production")
        after = self.snapshot()
        for value in ("15", "15.00"):
            result = self.call("correct-plan", "--field", "products.P01.minutes_per_unit",
                               "--new-value", value, "--changed-at", "2026-10-07",
                               "--reason", "Timed production", code=1)
            self.assertIn("already", result["error"])
            self.assertEqual(after, self.snapshot())
        book = sheets.load_book(self.workspace / "plan" / "plan", PLAN_SHEETS, fmt="csv")
        self.assertEqual(len(book["change_log"]), 1)
        self.assertEqual(book["products"][0]["minutes_per_unit"], "15")

    def test_correct_plan_accepts_zero_and_fractional_nonnegative_values(self):
        for field, value in (("channels.instagram.fulfilment_minutes_per_order", "0"),
                             ("assumptions.admin_hours_per_week", "0.5")):
            result = self.call("correct-plan", "--field", field, "--new-value", value,
                               "--changed-at", "2026-10-07", "--reason", "Timed work")
            self.assertEqual(result["correction"]["new_value"], value)

    def test_piped_json_preserves_unicode_with_restricted_console_encoding(self):
        label = "\u4e2d\U0001f600\u2192"
        row = sale()
        for key in ("description", "counterparty", "reference", "source_file", "notes"):
            row[key] = label
        argv = [sys.executable, "-B", str(ROOT / "tools" / "lembur.py"),
                "add-transactions", "--workspace", str(self.workspace), "--input", "-"]
        for encoding in ("cp1252", "ascii"):
            with self.subTest(encoding=encoding):
                env = dict(os.environ, PYTHONIOENCODING=encoding + ":strict", PYTHONUTF8="0")
                result = subprocess.run(argv, cwd=ROOT, input=json.dumps([row]).encode("ascii"),
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
                expected_code = 0 if encoding == "cp1252" else 1
                self.assertEqual(result.returncode, expected_code, result.stderr)
                self.assertEqual(result.stderr, b"")
                output = json.loads(result.stdout.decode("ascii"))
                if expected_code == 0:
                    for key in ("description", "counterparty", "reference", "source_file", "notes"):
                        self.assertEqual(output["transactions"][0][key], label)
                        self.assertEqual(self.ledger()["transactions"][0][key], label)
                else:
                    self.assertEqual(output["source_files"], [label])
        self.assertEqual(len(self.ledger()["transactions"]), 1)

    def test_input_file_and_csv_are_pinned(self):
        path = Path(self.temp.name) / "rows.json"
        path.write_text(json.dumps([sale()]), encoding="utf-8")
        self.call("add-transactions", "--input", str(path))
        self.assertTrue((self.workspace / "ledger_transactions.csv").exists())
        self.assertFalse(list(self.workspace.rglob("*.xlsx")))


if __name__ == "__main__":
    unittest.main()
