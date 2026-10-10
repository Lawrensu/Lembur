"""The tool layer: docs/SYSTEM_DESIGN.md section 6.4.

Runs with no key and no network. The module is loaded from its file path,
which is also the proof that it loads alone.
"""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "app" / "tools.py"

SPEC = importlib.util.spec_from_file_location("lembur_app_tools", SOURCE)
tools = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tools)

WEEK = "2026-W41"


def sale(date="2026-10-05", name="Dana", amount="5.00", reference=""):
    return {"date": date, "type": "income", "category": "sales",
            "description": "Beaded keychain order", "product_id": "P01",
            "quantity": "1", "amount_rm": amount, "channel": "instagram",
            "payment_method": "bank_transfer", "counterparty": name,
            "reference": reference,
            "source_file": "receipts/2026-10/order_%s_%s.png" % (date, name.lower())}


BANK_CSV = (
    "date,description,type,amount_rm,bank_reference\n"
    "2026-10-05,Transfer from Dana,income,5.00,DEMO-IN-001\n"
    "2026-10-05,Bead restock,expense,18.00,DEMO-OUT-001\n"
)


class ToolLayerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name) / "workspace"
        (self.workspace / "plan").mkdir(parents=True)
        for name in ("products", "channels", "assumptions", "change_log"):
            shutil.copyfile(ROOT / "data" / "demo" / ("plan_" + name + ".csv"),
                            self.workspace / "plan" / ("plan_" + name + ".csv"))
        (self.workspace / "inbox").mkdir()
        (self.workspace / "receipts" / "2026-10").mkdir(parents=True)

    def call(self, agent, name, args, ask=None):
        return tools.run_tool(self.workspace, agent, name, args, ask=ask)

    def put(self, relative, body, binary=False):
        target = self.workspace / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if binary:
            target.write_bytes(body)
        else:
            target.write_text(body, encoding="utf-8")
        return target

    # every answer carries ok and never raises

    def test_every_answer_carries_ok(self):
        answers = [
            self.call("bookkeeper", "list_files", {"folder": "no_such_folder"}),
            self.call("bookkeeper", "read_file", {"path": "nope.txt"}),
            self.call("bookkeeper", "calendar", {"date": "not a date"}),
            self.call("nobody", "list_files", {"folder": "inbox"}),
            self.call("bookkeeper", "no_such_tool", {}),
            self.call("bookkeeper", "lembur", None),
            self.call("bookkeeper", "lembur", {"command": ""}),
        ]
        for answer in answers:
            self.assertIsInstance(answer, dict)
            self.assertIn("ok", answer)
            self.assertIs(answer["ok"], False)
            self.assertTrue(answer.get("error"))

    # lembur

    def test_lembur_add_transactions_runs_the_command(self):
        answer = self.call("bookkeeper", "lembur",
                           {"command": "add-transactions", "input": [sale()]})
        self.assertTrue(answer["ok"], answer)
        self.assertEqual(answer["result"]["transactions"][0]["txn_id"], "T0001")
        self.assertTrue((self.workspace / "ledger_transactions.csv").is_file())

    def test_lembur_failure_keeps_result_and_names_the_message(self):
        answer = self.call("bookkeeper", "lembur", {
            "command": "classify",
            "options": {"txn-id": "T9999", "category": "materials", "reason": "test"}})
        self.assertFalse(answer["ok"])
        self.assertIn("not found", answer["error"])
        self.assertIn("error", answer["result"])

    def test_lembur_refuses_input_with_input_file(self):
        self.put("inbox/statement.csv", BANK_CSV)
        answer = self.call("bookkeeper", "lembur", {
            "command": "add-bank-lines", "input": [{"date": "2026-10-05"}],
            "input_file": "inbox/statement.csv"})
        self.assertFalse(answer["ok"])
        self.assertIn("not both", answer["error"])

    def test_lembur_input_file_reads_a_bank_statement_csv(self):
        self.put("inbox/statement.csv", BANK_CSV)
        answer = self.call("bookkeeper", "lembur",
                           {"command": "add-bank-lines",
                            "input_file": "inbox/statement.csv"})
        self.assertTrue(answer["ok"], answer)
        self.assertEqual(len(answer["result"]["bank_lines"]), 2)
        self.assertEqual(answer["result"]["bank_lines"][0]["bank_reference"], "DEMO-IN-001")

    def test_lembur_input_file_must_stay_inside_the_workspace(self):
        answer = self.call("bookkeeper", "lembur",
                           {"command": "add-bank-lines",
                            "input_file": "../statement.csv"})
        self.assertFalse(answer["ok"])
        self.assertIn("leaves the workspace", answer["error"])

    def test_lembur_options_are_placed_with_their_dashes(self):
        self.call("bookkeeper", "lembur",
                  {"command": "add-transactions", "input": [sale()]})
        answer = self.call("bookkeeper", "lembur",
                           {"command": "review", "options": {"week": WEEK}})
        self.assertTrue(answer["ok"], answer)
        self.assertIn("transactions", answer["result"])

    def test_lembur_boolean_option_becomes_a_bare_flag(self):
        answer = self.call("payroll", "lembur",
                           {"command": "hours",
                            "options": {"week": WEEK, "payslip-day": False}})
        self.assertTrue(answer["ok"], answer)
        self.assertIn("hours", answer["result"])

    # which agent may use what

    def test_the_allow_list_is_checked_on_every_call(self):
        refused = [
            ("payroll", "read_document", {"path": "inbox/a.txt"}),
            ("growth_coach", "calendar", {"date": "2026-10-05"}),
            ("auditor", "move_file", {"from": "inbox/a.txt", "to": "receipts/a.txt"}),
            ("bookkeeper", "lembur", {"command": "numbers",
                                      "options": {"week": WEEK}}),
            ("growth_coach", "lembur", {"command": "numbers",
                                        "options": {"week": WEEK}}),
            ("auditor", "lembur", {"command": "add-transactions", "input": []}),
            ("payroll", "lembur", {"command": "add-bank-lines", "input": []}),
        ]
        for agent, name, args in refused:
            answer = self.call(agent, name, args)
            self.assertFalse(answer["ok"], (agent, name))
            self.assertIn("may not", answer["error"])

    def test_allowed_tools_are_accepted(self):
        allowed = [
            ("bookkeeper", "list_files", {"folder": "inbox"}),
            ("payroll", "list_files", {"folder": "inbox"}),
            ("growth_coach", "list_files", {"folder": "inbox"}),
            ("auditor", "list_files", {"folder": "inbox"}),
            ("bookkeeper", "calendar", {"date": "2026-10-05"}),
            ("payroll", "calendar", {"date": "2026-10-05"}),
        ]
        for agent, name, args in allowed:
            self.assertTrue(self.call(agent, name, args)["ok"], (agent, name))

    # paths stay inside the workspace

    def test_a_path_that_leaves_the_workspace_is_refused(self):
        escapes = [
            ("read_file", {"path": "../secret.txt"}),
            ("read_file", {"path": "inbox/../../secret.txt"}),
            ("write_file", {"path": "../secret.txt", "text": "x"}),
            ("list_files", {"folder": ".."}),
            ("read_document", {"path": "../secret.txt"}),
            ("move_file", {"from": "../secret.txt", "to": "inbox/x.txt"}),
            ("move_file", {"from": "inbox/a.txt", "to": "../x.txt"}),
        ]
        for name, args in escapes:
            answer = self.call("bookkeeper", name, args)
            self.assertFalse(answer["ok"], name)
            self.assertIn("leaves the workspace", answer["error"])

    def test_an_absolute_path_is_refused(self):
        answer = self.call("bookkeeper", "read_file", {"path": str(ROOT / "README.md")})
        self.assertFalse(answer["ok"])

    # files

    def test_write_file_writes_and_appends(self):
        self.assertTrue(self.call("auditor", "write_file",
                                  {"path": "audit/report.md", "text": "one"})["ok"])
        self.assertTrue(self.call("auditor", "write_file",
                                  {"path": "audit/report.md", "text": "+two",
                                   "append": True})["ok"])
        self.assertEqual(self.call("auditor", "read_file",
                                   {"path": "audit/report.md"})["text"], "one+two")

    def test_write_file_refuses_what_only_the_command_may_change(self):
        protected = [
            "ledger_transactions.csv", "ledger_bank_lines.csv", "ledger_hours.csv",
            "plan/plan_products.csv", "plan/plan_channels.csv",
            "plan/plan_assumptions.csv", "plan/plan_change_log.csv",
            "audit/%s/numbers.json" % WEEK, "payslips/%s.html" % WEEK,
            "payslips/%s.pdf" % WEEK,
        ]
        for path in protected:
            answer = self.call("bookkeeper", "write_file", {"path": path, "text": "x"})
            self.assertFalse(answer["ok"], path)
            self.assertIn("lembur", answer["error"])
        self.assertFalse((self.workspace / "ledger_transactions.csv").exists())

    def test_write_file_still_writes_anything_else(self):
        answer = self.call("bookkeeper", "write_file",
                           {"path": "audit/%s/intake_log.md" % WEEK, "text": "log"})
        self.assertTrue(answer["ok"], answer)

    def test_list_files_is_in_file_name_order(self):
        for name in ("b.png", "a.png", "c.png"):
            self.put("inbox/" + name, "x")
        self.put("inbox/.gitkeep", "")
        answer = self.call("bookkeeper", "list_files", {"folder": "inbox"})
        self.assertEqual(answer["files"], [".gitkeep", "a.png", "b.png", "c.png"])

    def test_read_file_returns_text(self):
        self.put("receipts/2026-10/message_2026-10-05.txt", "hello")
        answer = self.call("bookkeeper", "read_file",
                           {"path": "receipts/2026-10/message_2026-10-05.txt"})
        self.assertTrue(answer["ok"])
        self.assertEqual(answer["text"], "hello")

    def test_move_file_moves_and_refuses_a_missing_source(self):
        self.put("inbox/order.png", "x")
        answer = self.call("bookkeeper", "move_file",
                           {"from": "inbox/order.png",
                            "to": "receipts/2026-10/order.png"})
        self.assertTrue(answer["ok"], answer)
        self.assertTrue((self.workspace / "receipts" / "2026-10" / "order.png").is_file())
        self.assertFalse(self.call("bookkeeper", "move_file",
                                   {"from": "inbox/gone.png",
                                    "to": "receipts/gone.png"})["ok"])

    # documents

    def test_read_document_returns_a_text_file_as_it_is(self):
        self.put("inbox/note.txt", "as written")
        answer = self.call("bookkeeper", "read_document", {"path": "inbox/note.txt"})
        self.assertTrue(answer["ok"])
        self.assertEqual(answer["text"], "as written")

    def test_read_document_sends_an_image_to_the_read_model(self):
        self.put("inbox/order.png", b"\x89PNG", binary=True)
        calls = []

        def scripted(role, messages, images=None):
            calls.append((role, messages, images))
            return "DEMO-IN-010"

        answer = self.call("bookkeeper", "read_document",
                           {"path": "inbox/order.png"}, ask=scripted)
        self.assertTrue(answer["ok"], answer)
        self.assertEqual(answer["text"], "DEMO-IN-010")
        role, messages, images = calls[0]
        self.assertEqual(role, "read")
        self.assertEqual(images, [str(self.workspace / "inbox" / "order.png")])
        self.assertTrue(messages and messages[0]["role"] == "user")

    def test_read_document_reads_only_the_inbox_and_receipts(self):
        self.put("plan/plan_products.csv", "product_id\n")
        answer = self.call("bookkeeper", "read_document",
                           {"path": "plan/plan_products.csv"})
        self.assertFalse(answer["ok"])
        self.assertIn("inbox", answer["error"])

    def test_read_document_without_a_scripted_model_does_not_raise(self):
        self.put("inbox/order.png", b"\x89PNG", binary=True)
        answer = self.call("bookkeeper", "read_document", {"path": "inbox/order.png"})
        self.assertIsInstance(answer, dict)
        self.assertIn("ok", answer)

    # calendar

    def test_calendar_gives_the_week_and_the_payslip_day(self):
        answer = self.call("bookkeeper", "calendar", {"date": "2026-10-05"})
        self.assertTrue(answer["ok"], answer)
        self.assertEqual(answer["week"], WEEK)
        self.assertEqual(answer["week_start"], "2026-10-05")
        self.assertEqual(answer["payslip_day"], "2026-10-11")
        self.assertIs(answer["is_payslip_day"], False)

    def test_calendar_knows_sunday_is_payslip_day(self):
        answer = self.call("bookkeeper", "calendar", {"date": "2026-10-11"})
        self.assertEqual(answer["week"], WEEK)
        self.assertIs(answer["is_payslip_day"], True)

    # the module itself

    def test_the_module_needs_no_key_and_no_network(self):
        self.assertFalse((SOURCE.parent / "model.py").exists()
                         and "LEMBUR_GATEWAY_KEY" in SOURCE.read_text(encoding="utf-8"))
        self.assertNotIn("urllib", SOURCE.read_text(encoding="utf-8"))

    def test_the_entry_point_it_runs_is_the_documented_one(self):
        self.assertEqual(tools.ENTRY_POINT, ROOT / "tools" / "lembur.py")
        self.assertTrue(tools.ENTRY_POINT.is_file())


if __name__ == "__main__":
    unittest.main()
