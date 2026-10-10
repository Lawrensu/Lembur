"""Tests for app/tools.py, the tool layer: run_tool(workspace, agent, name, args, ask=None).

These tests are written from docs/SYSTEM_DESIGN.md section 6.4 (with sections
2, 3.1, 4 and 6.3 where it points to them). The builder of app/tools.py makes
them pass and does not edit this file. If a test seems wrong, tell Law.

Where the design is silent, nothing is asserted. No network and no key are
needed: the model is replaced by a scripted function that records its calls.

Set LEMBUR_TOOLS_PATH to load another file than app/tools.py. If the file does
not exist, every test here is skipped.
"""
import csv
from decimal import Decimal
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS_PATH = Path(os.environ.get("LEMBUR_TOOLS_PATH") or ROOT / "app" / "tools.py")
DEMO = ROOT / "data" / "demo"
WEEK = "2026-W41"
IMAGE = DEMO / "inbox" / "order_2026-10-05_dana.png"

TOOLS = None
STATE_DIR = None
STATES = {}


def setUpModule():
    global TOOLS, STATE_DIR
    if not TOOLS_PATH.is_file():
        raise unittest.SkipTest("%s does not exist yet; the tool layer is not built" % TOOLS_PATH)
    spec = importlib.util.spec_from_file_location("lembur_tool_layer_under_test", TOOLS_PATH)
    TOOLS = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(TOOLS)
    STATE_DIR = tempfile.TemporaryDirectory()


def tearDownModule():
    if STATE_DIR is not None:
        STATE_DIR.cleanup()


# ---------------------------------------------------------------- fixtures

def make_layout(workspace):
    """The folder layout of design section 3.1, with the four plan files."""
    for folder in ("inbox", "plan", "receipts/2026-10", "boardroom/2026-W41",
                   "audit/2026-W41", "audit/2026-W42", "payslips",
                   "approvals/2026-W41/approved"):
        (workspace / folder).mkdir(parents=True, exist_ok=True)
    for name in ("products", "channels", "assumptions", "change_log"):
        shutil.copyfile(DEMO / ("plan_%s.csv" % name), workspace / "plan" / ("plan_%s.csv" % name))
    return workspace


def cli(workspace, command, *args, rows=None):
    """Run a lembur command directly, as the existing tool tests do."""
    argv = [sys.executable, "-B", str(ROOT / "tools" / "lembur.py"), command,
            "--workspace", str(workspace), *args]
    if rows is not None:
        argv.extend(["--input", "-"])
    done = subprocess.run(argv, cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
                          input=None if rows is None else json.dumps(rows))
    return done.returncode, json.loads(done.stdout)


def cash_sale(**changes):
    row = {"date": "2026-10-05", "type": "income", "category": "sales",
           "description": "1 Beaded keychain", "product_id": "P01", "quantity": "1",
           "amount_rm": "5.00", "channel": "bazaar", "payment_method": "cash",
           "counterparty": "Aina",
           "source_file": "receipts/2026-10/message_2026-10-05.txt"}
    row.update(changes)
    return row


def transfer_sale():
    return cash_sale(payment_method="bank_transfer", channel="instagram",
                     counterparty="Dana", source_file="receipts/2026-10/order_dana.png")


def bank_line(reference, date="2026-10-05", description="Transfer"):
    return {"date": date, "description": description, "type": "income",
            "amount_rm": "5.00", "bank_reference": reference}


def _state_empty(ws):
    pass


def _state_cash_row(ws):
    assert cli(ws, "add-transactions", rows=[cash_sale()])[0] == 0


def _state_blank_category_row(ws):
    assert cli(ws, "add-transactions", rows=[cash_sale(category="")])[0] == 0


def _state_bank_line(ws):
    assert cli(ws, "add-bank-lines", rows=[bank_line("REF-X", "2026-10-06")])[0] == 0


def _state_ambiguous(ws):
    assert cli(ws, "add-transactions", rows=[transfer_sale()])[0] == 0
    assert cli(ws, "add-bank-lines", rows=[bank_line("REF-A", description="Transfer from Dana"),
                                           bank_line("REF-B", description="Transfer from Mira")])[0] == 0
    assert cli(ws, "reconcile")[0] == 0


def _state_numbers_saved(ws):
    _state_cash_row(ws)
    assert cli(ws, "numbers", "--week", WEEK)[0] == 0


STATE_BUILDERS = {"empty": _state_empty, "cash_row": _state_cash_row,
                  "blank_category_row": _state_blank_category_row,
                  "bank_line": _state_bank_line, "ambiguous": _state_ambiguous,
                  "numbers_saved": _state_numbers_saved}

PAYSLIP_INPUT = {"debate_summary": "Payroll and the Growth coach agreed.",
                 "ruling": "Upheld.", "raise_plan": []}

# command -> (state it needs, options, input, does a successful run change the workspace)
SCENARIOS = {
    "add-transactions": ("empty", {}, [cash_sale()], True),
    "add-bank-lines": ("empty", {}, [bank_line("REF-1")], True),
    "reconcile": ("cash_row", {}, None, True),
    "resolve": ("ambiguous", {"txn-id": "T0001", "bank-reference": "REF-A",
                              "reason": "Counterparty Dana matches the bank description"}, None, True),
    "classify": ("blank_category_row", {"txn-id": "T0001", "category": "sales",
                                        "reason": "The document shows a sale"}, None, True),
    "close-week": ("bank_line", {"week": WEEK}, None, True),
    "correct-plan": ("empty", {"field": "products.P01.minutes_per_unit", "new-value": "15",
                               "changed-at": "2026-10-07", "reason": "I timed myself"}, None, True),
    "hours": ("cash_row", {"week": WEEK}, None, True),
    "numbers": ("cash_row", {"week": WEEK}, None, True),
    "numbers-check": ("numbers_saved", {"week": WEEK}, None, False),
    "review": ("empty", {"week": WEEK}, None, False),
    "payslip": ("numbers_saved", {"week": WEEK}, PAYSLIP_INPUT, True),
}

# design section 6.4, "Which agent may use what"
ALLOWED_COMMANDS = {
    "bookkeeper": {"add-transactions", "add-bank-lines", "reconcile", "resolve",
                   "classify", "close-week", "review"},
    "payroll": {"correct-plan", "hours", "numbers", "review", "payslip"},
    "growth_coach": {"review"},
    "auditor": {"numbers-check", "review"},
}
AGENTS = tuple(ALLOWED_COMMANDS)


class Asker:
    """A scripted model: records every call and returns a fixed answer."""

    def __init__(self, answer="SCRIPTED READING OF THE IMAGE"):
        self.answer = answer
        self.calls = []

    def __call__(self, role, messages, images=None):
        self.calls.append({"role": role, "messages": messages, "images": images})
        return self.answer


class ToolTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ws = make_layout(self.root / "workspace")
        self.outside = self.root / "outside"
        self.outside.mkdir()
        self.ask = Asker()
        self.copies = 0

    # -- calling
    def run_tool(self, agent, name, args, workspace=None):
        return TOOLS.run_tool(workspace or self.ws, agent, name, args, ask=self.ask)

    def lembur(self, agent, command, options=None, input=None, workspace=None):
        args = {"command": command}
        if options is not None:
            args["options"] = options
        if input is not None:
            args["input"] = input
        return self.run_tool(agent, "lembur", args, workspace)

    # -- workspace helpers
    def state(self, name):
        """A fresh copy of a workspace in a known state, built once per run by the command line."""
        if name not in STATES:
            template = make_layout(Path(STATE_DIR.name) / name)
            STATE_BUILDERS[name](template)
            STATES[name] = template
        self.copies += 1
        return Path(shutil.copytree(STATES[name], self.root / ("state_%s_%d" % (name, self.copies))))

    def put(self, relative, content, binary=False):
        path = self.ws / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if binary else content.encode("utf-8"))
        return path

    @staticmethod
    def snapshot(folder, skip=()):
        found = {}
        for path in sorted(folder.rglob("*")):
            relative = path.relative_to(folder).as_posix()
            if relative.split("/")[0] in skip:
                continue
            found[relative] = path.read_bytes() if path.is_file() else None
        return found

    def outside_snapshot(self):
        return self.snapshot(self.root, skip=("workspace",))

    def rows(self, relative, workspace=None):
        path = (workspace or self.ws) / relative
        if not path.is_file():
            return []
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    # -- assertions
    def assertRefused(self, result, note=""):
        self.assertIsInstance(result, dict, note)
        self.assertIs(result.get("ok"), False, "%s should be refused, got %r" % (note, result))
        self.assertIsInstance(result.get("error"), str, note)
        self.assertTrue(result["error"].strip(), note)

    def assertWorks(self, result, note=""):
        self.assertIsInstance(result, dict, note)
        self.assertIs(result.get("ok"), True, "%s should work, got %r" % (note, result))


# ---------------------------------------------------------------- the return value

class ReturnValueTests(ToolTestCase):
    def test_every_call_returns_a_dict_holding_ok_as_a_boolean(self):
        self.put("inbox/a.txt", "hello")
        calls = [
            ("bookkeeper", "calendar", {"date": "2026-10-05"}),
            ("bookkeeper", "list_files", {"folder": "inbox"}),
            ("bookkeeper", "read_file", {"path": "inbox/a.txt"}),
            ("bookkeeper", "read_file", {"path": "inbox/missing.txt"}),
            ("bookkeeper", "write_file", {"path": "audit/2026-W41/x.md", "text": "x"}),
            ("bookkeeper", "lembur", {"command": "review", "options": {"week": WEEK}}),
            ("bookkeeper", "lembur", {"command": "review"}),
            ("bookkeeper", "no_such_tool", {}),
            ("nobody", "calendar", {"date": "2026-10-05"}),
            ("bookkeeper", "read_file", {}),
            ("auditor", "move_file", {"from": "inbox/a.txt", "to": "receipts/2026-10/a.txt"}),
        ]
        for agent, name, args in calls:
            with self.subTest(agent=agent, name=name, args=args):
                result = self.run_tool(agent, name, args)
                self.assertIsInstance(result, dict)
                self.assertIn("ok", result)
                self.assertIsInstance(result["ok"], bool)

    def test_unknown_tool_name_is_ok_false_with_an_error_text(self):
        for name in ("no_such_tool", "delete_file", "", "LEMBUR"):
            with self.subTest(name=name):
                self.assertRefused(self.run_tool("bookkeeper", name, {}), name)

    def test_unknown_agent_name_is_ok_false(self):
        self.put("inbox/a.txt", "hello")
        for agent in ("janitor", "", "root", None):
            with self.subTest(agent=agent):
                self.assertRefused(self.run_tool(agent, "calendar", {"date": "2026-10-05"}), agent)
                self.assertRefused(self.run_tool(agent, "read_file", {"path": "inbox/a.txt"}), agent)

    def test_missing_or_wrong_args_are_ok_false_and_change_nothing(self):
        self.put("inbox/a.txt", "hello")
        before = self.snapshot(self.ws)
        calls = [
            ("read_file", {}), ("read_file", {"path": 5}), ("read_file", {"file": "inbox/a.txt"}),
            ("write_file", {"path": "audit/2026-W41/x.md"}), ("write_file", {"text": "x"}),
            ("write_file", {}),
            ("list_files", {}), ("calendar", {}),
            ("calendar", {"date": "not a date"}), ("calendar", {"date": "2026-02-30"}),
            ("move_file", {"from": "inbox/a.txt"}), ("move_file", {"to": "receipts/2026-10/a.txt"}),
            ("read_document", {}),
            ("lembur", {}), ("lembur", {"command": 5}), ("lembur", {"options": {"week": WEEK}}),
            ("read_file", None), ("read_file", "inbox/a.txt"), ("read_file", []),
        ]
        for name, args in calls:
            with self.subTest(name=name, args=args):
                self.assertRefused(self.run_tool("bookkeeper", name, args), name)
        self.assertEqual(before, self.snapshot(self.ws))

    def test_a_file_that_does_not_exist_is_ok_false(self):
        for agent in AGENTS:
            with self.subTest(agent=agent):
                self.assertRefused(self.run_tool(agent, "read_file", {"path": "inbox/missing.txt"}))

    def test_only_reading_an_image_asks_the_model(self):
        self.put("inbox/a.txt", "hello")
        self.run_tool("bookkeeper", "read_file", {"path": "inbox/a.txt"})
        self.run_tool("bookkeeper", "read_document", {"path": "inbox/a.txt"})
        self.run_tool("bookkeeper", "list_files", {"folder": "inbox"})
        self.run_tool("bookkeeper", "calendar", {"date": "2026-10-05"})
        self.run_tool("bookkeeper", "lembur", {"command": "review", "options": {"week": WEEK}})
        self.assertEqual(self.ask.calls, [])


# ---------------------------------------------------------------- calendar

class CalendarTests(ToolTestCase):
    def calendar(self, date, agent="bookkeeper"):
        result = self.run_tool(agent, "calendar", {"date": date})
        self.assertWorks(result, date)
        return result

    def test_calendar_monday_gives_week_start_payslip_day_and_not_payslip_day(self):
        result = self.calendar("2026-10-05")
        self.assertEqual(result["week"], "2026-W41")
        self.assertEqual(result["week_start"], "2026-10-05")
        self.assertEqual(result["payslip_day"], "2026-10-11")
        self.assertIs(result["is_payslip_day"], False)

    def test_calendar_sunday_is_payslip_day(self):
        result = self.calendar("2026-10-11")
        self.assertEqual(result["week"], "2026-W41")
        self.assertEqual(result["week_start"], "2026-10-05")
        self.assertEqual(result["payslip_day"], "2026-10-11")
        self.assertIs(result["is_payslip_day"], True)

    def test_calendar_midweek_date_is_in_the_same_week_and_not_payslip_day(self):
        result = self.calendar("2026-10-07")
        self.assertEqual(result["week"], "2026-W41")
        self.assertEqual(result["week_start"], "2026-10-05")
        self.assertEqual(result["payslip_day"], "2026-10-11")
        self.assertIs(result["is_payslip_day"], False)

    def test_calendar_next_monday_starts_the_next_week(self):
        result = self.calendar("2026-10-12")
        self.assertEqual(result["week"], "2026-W42")
        self.assertEqual(result["week_start"], "2026-10-12")
        self.assertEqual(result["payslip_day"], "2026-10-18")

    def test_calendar_uses_iso_weeks_across_the_new_year(self):
        result = self.calendar("2027-01-01")
        self.assertEqual(result["week"], "2026-W53")
        self.assertEqual(result["week_start"], "2026-12-28")
        self.assertEqual(result["payslip_day"], "2027-01-03")
        self.assertIs(result["is_payslip_day"], False)


# ---------------------------------------------------------------- files

class FileToolTests(ToolTestCase):
    def test_write_file_then_read_file_returns_the_text_for_every_agent(self):
        paths = {"bookkeeper": "audit/2026-W41/intake_log.md",
                 "payroll": "boardroom/2026-W41/payroll.md",
                 "growth_coach": "boardroom/2026-W41/growth.md",
                 "auditor": "audit/2026-W41/audit_report.md"}
        for agent, path in paths.items():
            with self.subTest(agent=agent):
                text = "report by %s: 42 words" % agent
                self.assertWorks(self.run_tool(agent, "write_file", {"path": path, "text": text}))
                result = self.run_tool(agent, "read_file", {"path": path})
                self.assertWorks(result)
                self.assertEqual(result["text"], text)

    def test_write_file_append_true_adds_to_the_end_of_the_file(self):
        path = "boardroom/2026-W41/payroll.md"
        self.assertWorks(self.run_tool("payroll", "write_file", {"path": path, "text": "first"}))
        self.assertWorks(self.run_tool("payroll", "write_file",
                                       {"path": path, "text": " second", "append": True}))
        self.assertWorks(self.run_tool("payroll", "write_file",
                                       {"path": path, "text": " third", "append": True}))
        self.assertEqual(self.run_tool("payroll", "read_file", {"path": path})["text"],
                         "first second third")

    def test_list_files_returns_files_in_file_name_order(self):
        for name in ("c.txt", "a.txt", "e.txt", "b.txt", "d.txt"):
            self.put("inbox/" + name, name)
        for agent in AGENTS:
            with self.subTest(agent=agent):
                result = self.run_tool(agent, "list_files", {"folder": "inbox"})
                self.assertWorks(result)
                files = result["files"]
                self.assertIsInstance(files, list)
                self.assertTrue(all(isinstance(item, str) for item in files), files)
                self.assertEqual([item.replace("\\", "/").split("/")[-1] for item in files],
                                 ["a.txt", "b.txt", "c.txt", "d.txt", "e.txt"])
                self.assertEqual(files, sorted(files))

    def test_move_file_by_the_bookkeeper_moves_an_inbox_file_into_the_month_folder(self):
        data = b"receipt bytes \x00\x01"
        self.put("inbox/receipt_a.png", data, binary=True)
        result = self.run_tool("bookkeeper", "move_file",
                               {"from": "inbox/receipt_a.png", "to": "receipts/2026-10/receipt_a.png"})
        self.assertWorks(result)
        self.assertFalse((self.ws / "inbox" / "receipt_a.png").exists())
        moved = [path for path in (self.ws / "receipts" / "2026-10").rglob("*") if path.is_file()]
        self.assertEqual([path.read_bytes() for path in moved], [data])


# ---------------------------------------------------------------- paths that leave the workspace

class WorkspaceBoundaryTests(ToolTestCase):
    def setUp(self):
        super().setUp()
        (self.outside / "secret.txt").write_text("SECRET OUTSIDE", encoding="utf-8")
        shutil.copyfile(IMAGE, self.outside / "secret.png")
        self.put("inbox/a.txt", "inside text")

    def leaving_paths(self, name):
        return ["../outside/" + name, "inbox/../../outside/" + name, str(self.outside / name)]

    def test_read_file_refuses_a_path_that_leaves_the_workspace(self):
        for agent in AGENTS:
            for path in self.leaving_paths("secret.txt"):
                with self.subTest(agent=agent, path=path):
                    result = self.run_tool(agent, "read_file", {"path": path})
                    self.assertRefused(result)
                    self.assertNotIn("SECRET OUTSIDE", repr(result))

    def test_write_file_refuses_a_path_that_leaves_the_workspace(self):
        before_outside, before_inside = self.outside_snapshot(), self.snapshot(self.ws)
        for agent in AGENTS:
            for append in (False, True):
                for path in self.leaving_paths("new.txt") + ["../new_in_parent.txt",
                                                             self.ws.parent.joinpath("new_in_parent.txt").as_posix(),
                                                             str(self.outside / "secret.txt")]:
                    with self.subTest(agent=agent, path=path, append=append):
                        args = {"path": path, "text": "WRITTEN"}
                        if append:
                            args["append"] = True
                        self.assertRefused(self.run_tool(agent, "write_file", args))
        self.assertEqual(before_outside, self.outside_snapshot())
        self.assertEqual(before_inside, self.snapshot(self.ws))

    def test_list_files_refuses_a_folder_that_leaves_the_workspace(self):
        for agent in AGENTS:
            for folder in ("../outside", "inbox/../../outside", str(self.outside), ".."):
                with self.subTest(agent=agent, folder=folder):
                    result = self.run_tool(agent, "list_files", {"folder": folder})
                    self.assertRefused(result)
                    self.assertNotIn("secret.txt", repr(result))

    def test_move_file_refuses_a_path_that_leaves_the_workspace(self):
        before_outside, before_inside = self.outside_snapshot(), self.snapshot(self.ws)
        for source in self.leaving_paths("secret.txt"):
            with self.subTest(source=source):
                self.assertRefused(self.run_tool("bookkeeper", "move_file",
                                                 {"from": source, "to": "receipts/2026-10/secret.txt"}))
        for target in self.leaving_paths("moved.txt"):
            with self.subTest(target=target):
                self.assertRefused(self.run_tool("bookkeeper", "move_file",
                                                 {"from": "inbox/a.txt", "to": target}))
        self.assertEqual(before_outside, self.outside_snapshot())
        self.assertEqual(before_inside, self.snapshot(self.ws))

    def test_read_document_refuses_a_path_that_leaves_the_workspace(self):
        for name in ("secret.txt", "secret.png"):
            for path in self.leaving_paths(name):
                with self.subTest(path=path):
                    result = self.run_tool("bookkeeper", "read_document", {"path": path})
                    self.assertRefused(result)
                    self.assertNotIn("SECRET OUTSIDE", repr(result))
        self.assertEqual(self.ask.calls, [])


# ---------------------------------------------------------------- files that only lembur may change

PROTECTED = ["ledger_transactions.csv", "ledger_bank_lines.csv", "ledger_hours.csv",
             "plan/plan_products.csv", "plan/plan_channels.csv", "plan/plan_assumptions.csv",
             "plan/plan_change_log.csv", "audit/2026-W41/numbers.json", "audit/2026-W42/numbers.json",
             "payslips/2026-W41.html"]


class ProtectedFileTests(ToolTestCase):
    def test_write_file_refuses_the_ledger_plan_numbers_and_payslip_files_and_leaves_them_unchanged(self):
        for relative in PROTECTED:
            if not (self.ws / relative).exists():
                self.put(relative, "SENTINEL\n")
        before = self.snapshot(self.ws)
        for agent in AGENTS:
            for relative in PROTECTED:
                for append in (False, True):
                    with self.subTest(agent=agent, path=relative, append=append):
                        args = {"path": relative, "text": "OVERWRITTEN"}
                        if append:
                            args["append"] = True
                        self.assertRefused(self.run_tool(agent, "write_file", args))
        self.assertEqual(before, self.snapshot(self.ws))

    def test_write_file_does_not_create_a_protected_file_that_is_absent(self):
        before = self.snapshot(self.ws)
        for relative in PROTECTED:
            if (self.ws / relative).exists():
                continue
            with self.subTest(path=relative):
                self.assertRefused(self.run_tool("payroll", "write_file",
                                                 {"path": relative, "text": "{}"}))
                self.assertFalse((self.ws / relative).exists())
        self.assertEqual(before, self.snapshot(self.ws))

    def test_write_file_refuses_a_protected_file_written_with_another_spelling_of_the_path(self):
        for relative in ("ledger_transactions.csv", "ledger_hours.csv"):
            self.put(relative, "SENTINEL\n")
        self.put("audit/2026-W41/numbers.json", "SENTINEL\n")
        before = self.snapshot(self.ws)
        spellings = ["./ledger_transactions.csv", "plan/../ledger_transactions.csv",
                     "inbox/../ledger_hours.csv", "audit/2026-W41/../2026-W41/numbers.json",
                     "audit/./2026-W41/numbers.json", "payslips/../payslips/2026-W41.html"]
        for spelling in spellings:
            with self.subTest(path=spelling):
                self.assertRefused(self.run_tool("payroll", "write_file",
                                                 {"path": spelling, "text": "OVERWRITTEN"}))
        self.assertEqual(before, self.snapshot(self.ws))


# ---------------------------------------------------------------- read_document

class ReadDocumentTests(ToolTestCase):
    def test_read_document_returns_a_text_or_csv_file_as_it_is_and_does_not_ask_the_model(self):
        files = {"inbox/note.txt": "Sold 3 keychains at the bazaar.\nThanks!\n",
                 "inbox/bank.csv": "date,description\n2026-10-05,Transfer\n",
                 "receipts/2026-10/message_2026-10-05.txt": "Bazaar 4 to 9, sold 2\n"}
        for relative, content in files.items():
            self.put(relative, content)
        for relative, content in files.items():
            with self.subTest(path=relative):
                result = self.run_tool("bookkeeper", "read_document", {"path": relative})
                self.assertWorks(result)
                self.assertEqual(result["text"], content)
        self.assertEqual(self.ask.calls, [])

    def test_read_document_on_a_text_file_works_when_ask_is_left_out(self):
        self.put("inbox/note.txt", "plain words")
        result = TOOLS.run_tool(self.ws, "bookkeeper", "read_document", {"path": "inbox/note.txt"})
        self.assertWorks(result)
        self.assertEqual(result["text"], "plain words")

    def _image_in_inbox(self, folder="inbox"):
        target = self.ws / folder / "order_2026-10-05_dana.png"
        shutil.copyfile(IMAGE, target)
        return target

    def test_read_document_on_an_image_calls_ask_once_with_role_read_and_the_image_path(self):
        target = self._image_in_inbox()
        self.assertWorks(self.run_tool("bookkeeper", "read_document",
                                       {"path": "inbox/order_2026-10-05_dana.png"}))
        self.assertEqual(len(self.ask.calls), 1)
        call = self.ask.calls[0]
        self.assertEqual(call["role"], "read")
        images = call["images"]
        self.assertIsInstance(images, list)
        self.assertEqual(len(images), 1)
        path = Path(images[0])
        if not path.is_absolute():
            path = self.ws / path
        self.assertTrue(path.exists(), "image path %r does not point at a file" % (images[0],))
        self.assertTrue(os.path.samefile(path, target), images[0])

    def test_read_document_on_an_image_returns_the_scripted_answer_as_text(self):
        self.ask.answer = "Receipt: 18.00 Demo Bead Nook"
        self._image_in_inbox()
        result = self.run_tool("bookkeeper", "read_document", {"path": "inbox/order_2026-10-05_dana.png"})
        self.assertWorks(result)
        self.assertEqual(result["text"], "Receipt: 18.00 Demo Bead Nook")

    def test_read_document_on_an_image_in_receipts_also_asks_the_read_model(self):
        self._image_in_inbox("receipts/2026-10")
        result = self.run_tool("bookkeeper", "read_document",
                               {"path": "receipts/2026-10/order_2026-10-05_dana.png"})
        self.assertWorks(result)
        self.assertEqual(result["text"], self.ask.answer)
        self.assertEqual([call["role"] for call in self.ask.calls], ["read"])

    def test_read_document_gives_ask_messages_as_dicts_with_role_and_content_text(self):
        self._image_in_inbox()
        self.run_tool("bookkeeper", "read_document", {"path": "inbox/order_2026-10-05_dana.png"})
        messages = self.ask.calls[0]["messages"]
        self.assertIsInstance(messages, list)
        for message in messages:
            self.assertIsInstance(message, dict)
            self.assertIsInstance(message.get("role"), str)
            self.assertIsInstance(message.get("content"), str)


# ---------------------------------------------------------------- the allow list

class AllowListTests(ToolTestCase):
    def prepare_files(self):
        self.put("inbox/a.txt", "hello")

    def test_each_agent_may_use_the_tools_on_its_list(self):
        self.prepare_files()
        on_list = {
            "bookkeeper": [("read_document", {"path": "inbox/a.txt"}),
                           ("list_files", {"folder": "inbox"}),
                           ("read_file", {"path": "inbox/a.txt"}),
                           ("write_file", {"path": "audit/2026-W41/intake_log.md", "text": "x"}),
                           ("move_file", {"from": "inbox/a.txt", "to": "receipts/2026-10/a.txt"}),
                           ("calendar", {"date": "2026-10-05"})],
            "payroll": [("list_files", {"folder": "inbox"}), ("read_file", {"path": "inbox/a.txt"}),
                        ("write_file", {"path": "boardroom/2026-W41/payroll.md", "text": "x"}),
                        ("calendar", {"date": "2026-10-05"})],
            "growth_coach": [("list_files", {"folder": "inbox"}), ("read_file", {"path": "inbox/a.txt"}),
                             ("write_file", {"path": "boardroom/2026-W41/growth.md", "text": "x"})],
            "auditor": [("list_files", {"folder": "inbox"}), ("read_file", {"path": "inbox/a.txt"}),
                        ("write_file", {"path": "audit/2026-W41/audit_report.md", "text": "x"})],
        }
        for agent, calls in on_list.items():
            for name, args in calls:
                with self.subTest(agent=agent, name=name):
                    self.prepare_files()
                    self.assertWorks(self.run_tool(agent, name, args))

    def fresh_workspace(self):
        workspace = self.state("empty")
        (workspace / "inbox" / "a.txt").write_text("hello", encoding="utf-8")
        return workspace

    def refused_tool(self, name, args, refused, control="bookkeeper"):
        """Each refused agent gets ok false and no change; the same call by the bookkeeper works."""
        for agent in refused:
            with self.subTest(agent=agent, name=name):
                workspace = self.fresh_workspace()
                before = self.snapshot(workspace)
                result = self.run_tool(agent, name, args, workspace)
                self.assertRefused(result)
                self.assertNotIn("text", result)
                self.assertEqual(before, self.snapshot(workspace))
        self.assertWorks(self.run_tool(control, name, args, self.fresh_workspace()), "control " + control)
        self.assertEqual(self.ask.calls, [])

    def test_move_file_is_for_the_bookkeeper_only(self):
        self.refused_tool("move_file", {"from": "inbox/a.txt", "to": "receipts/2026-10/a.txt"},
                          ["payroll", "growth_coach", "auditor"])

    def test_read_document_is_for_the_bookkeeper_only(self):
        self.refused_tool("read_document", {"path": "inbox/a.txt"},
                          ["payroll", "growth_coach", "auditor"])

    def test_calendar_is_for_the_bookkeeper_and_payroll_only(self):
        self.refused_tool("calendar", {"date": "2026-10-05"}, ["growth_coach", "auditor"])
        self.assertWorks(self.run_tool("payroll", "calendar", {"date": "2026-10-05"}))

    # -- commands

    def run_scenario(self, agent, command, workspace):
        state, options, input, _ = SCENARIOS[command]
        return self.lembur(agent, command, options, input, workspace)

    def check_commands_refused(self, command, refused_agents, control):
        """A refused command changes nothing and returns ok false; the control agent's run works."""
        state, options, input, changes = SCENARIOS[command]
        workspace = self.state(state)
        before = self.snapshot(workspace)
        for agent in refused_agents:
            with self.subTest(command=command, agent=agent):
                result = self.run_scenario(agent, command, workspace)
                self.assertRefused(result, "%s by %s" % (command, agent))
                self.assertEqual(before, self.snapshot(workspace),
                                 "%s by %s changed the workspace" % (command, agent))
        with self.subTest(command=command, agent=control):
            result = self.run_scenario(control, command, workspace)
            self.assertWorks(result, "control %s by %s" % (command, control))
            if changes:
                self.assertNotEqual(before, self.snapshot(workspace), "the scenario for %s changes nothing" % command)

    def refused_for(self, agent):
        return [command for command in SCENARIOS if command not in ALLOWED_COMMANDS[agent]]

    def control_for(self, command):
        return next(agent for agent in AGENTS if command in ALLOWED_COMMANDS[agent])

    def test_bookkeeper_may_run_the_seven_commands_on_its_list(self):
        for command in sorted(ALLOWED_COMMANDS["bookkeeper"]):
            with self.subTest(command=command):
                self.assertWorks(self.run_scenario("bookkeeper", command, self.state(SCENARIOS[command][0])), command)

    def test_bookkeeper_may_not_run_numbers_hours_payslip_correct_plan_or_numbers_check(self):
        for command in ("numbers", "hours", "payslip", "correct-plan", "numbers-check"):
            self.check_commands_refused(command, ["bookkeeper"], self.control_for(command))

    def test_payroll_may_run_the_five_commands_on_its_list(self):
        for command in sorted(ALLOWED_COMMANDS["payroll"]):
            with self.subTest(command=command):
                self.assertWorks(self.run_scenario("payroll", command, self.state(SCENARIOS[command][0])), command)

    def test_payroll_may_not_run_the_bookkeeper_commands_or_numbers_check(self):
        for command in ("add-transactions", "add-bank-lines", "reconcile", "resolve",
                        "classify", "close-week", "numbers-check"):
            self.check_commands_refused(command, ["payroll"], self.control_for(command))

    def test_growth_coach_may_run_review_and_no_other_command(self):
        self.assertWorks(self.run_scenario("growth_coach", "review", self.state("empty")))
        for command in self.refused_for("growth_coach"):
            self.check_commands_refused(command, ["growth_coach"], self.control_for(command))

    def test_auditor_may_run_numbers_check_and_review_and_no_other_command(self):
        for command in sorted(ALLOWED_COMMANDS["auditor"]):
            with self.subTest(command=command):
                self.assertWorks(self.run_scenario("auditor", command, self.state(SCENARIOS[command][0])), command)
        for command in self.refused_for("auditor"):
            self.check_commands_refused(command, ["auditor"], self.control_for(command))

    def test_auditor_cannot_add_transactions_classify_correct_the_plan_or_save_numbers(self):
        for command in ("add-transactions", "classify", "correct-plan", "numbers"):
            self.check_commands_refused(command, ["auditor"], self.control_for(command))


# ---------------------------------------------------------------- the lembur tool

class LemburToolTests(ToolTestCase):
    def test_lembur_add_transactions_writes_the_ledger_and_returns_the_command_json(self):
        twin = make_layout(self.root / "twin")
        code, printed = cli(twin, "add-transactions", rows=[cash_sale()])
        self.assertEqual(code, 0)
        result = self.lembur("bookkeeper", "add-transactions", input=[cash_sale()])
        self.assertWorks(result)
        self.assertEqual(result["result"], printed)
        rows = self.rows("ledger_transactions.csv")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["category"], "sales")
        self.assertEqual(rows[0]["amount_rm"], "5.00")

    def test_lembur_reconcile_with_empty_options_then_review_with_a_week_option_work(self):
        twin = make_layout(self.root / "twin")
        for command, args, rows in (("add-transactions", (), [cash_sale()]), ("reconcile", (), None)):
            cli(twin, command, *args, rows=rows)
        _, printed_review = cli(twin, "review", "--week", WEEK)
        self.assertWorks(self.lembur("bookkeeper", "add-transactions", input=[cash_sale()]))
        reconciled = self.lembur("bookkeeper", "reconcile", options={})
        self.assertWorks(reconciled)
        self.assertIn("result", reconciled)
        self.assertEqual(self.rows("ledger_transactions.csv")[0]["reconciliation_status"], "cash_declared")
        review = self.lembur("bookkeeper", "review", options={"week": WEEK})
        self.assertWorks(review)
        self.assertEqual(review["result"], printed_review)

    def test_lembur_option_set_to_true_becomes_the_flag(self):
        with_flag = self.state("cash_row")
        self.assertWorks(self.lembur("payroll", "hours", {"week": WEEK, "payslip-day": True},
                                     workspace=with_flag))
        admin = [row for row in self.rows("ledger_hours.csv", with_flag) if row["activity"] == "admin"]
        self.assertEqual([row["date"] for row in admin], ["2026-10-11"])
        without_flag = self.state("cash_row")
        self.assertWorks(self.lembur("payroll", "hours", {"week": WEEK}, workspace=without_flag))
        self.assertEqual([row for row in self.rows("ledger_hours.csv", without_flag)
                          if row["activity"] == "admin"], [])

    def test_lembur_payslip_takes_an_object_as_input_and_runs_from_the_repository_root(self):
        workspace = self.state("numbers_saved")
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        previous = os.getcwd()
        os.chdir(elsewhere)
        self.addCleanup(os.chdir, previous)
        result = self.lembur("payroll", "payslip", {"week": WEEK}, PAYSLIP_INPUT, workspace)
        self.assertWorks(result)
        self.assertTrue((workspace / "payslips" / "2026-W41.html").is_file())
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_lembur_failure_comes_back_as_data_with_the_command_json_in_result(self):
        twin = make_layout(self.root / "twin")
        row = cash_sale(txn_id="T0001")
        code, printed = cli(twin, "add-transactions", rows=[row])
        self.assertEqual(code, 1)
        result = self.lembur("bookkeeper", "add-transactions", input=[row])
        self.assertIs(result["ok"], False)
        self.assertIsInstance(result["error"], str)
        self.assertTrue(result["error"].strip())
        self.assertEqual(result["error"], printed["error"])
        self.assertIsInstance(result["result"], dict)
        self.assertEqual(result["result"], printed)
        self.assertEqual(self.rows("ledger_transactions.csv"), [])

    def test_lembur_unknown_command_is_ok_false(self):
        before = self.snapshot(self.ws)
        for command in ("explode", "add_transactions", "", "tools/lembur.py", "--help"):
            for agent in AGENTS:
                with self.subTest(command=command, agent=agent):
                    self.assertRefused(self.lembur(agent, command, {}))
        self.assertEqual(before, self.snapshot(self.ws))

    def test_lembur_workspace_in_options_cannot_send_a_write_to_another_folder(self):
        # Either ok false or the other folder stays empty; both are safe.
        other = self.root / "other"
        other.mkdir()
        for value in (str(other), other.as_posix()):
            with self.subTest(value=value):
                self.lembur("bookkeeper", "add-transactions", {"workspace": value}, [cash_sale()])
                self.assertEqual(list(other.iterdir()), [], "a write reached the other folder")


class InputFileTests(ToolTestCase):
    STATEMENT = DEMO / "inbox" / "bank_statement_2026-W41_SYNTHETIC.csv"

    def add_bank_lines_from(self, path, workspace=None, agent="bookkeeper"):
        return self.run_tool(agent, "lembur", {"command": "add-bank-lines", "input_file": path}, workspace)

    def test_lembur_input_file_csv_in_the_workspace_becomes_the_rows_of_the_command(self):
        shutil.copyfile(self.STATEMENT, self.ws / "inbox" / "statement.csv")
        with self.STATEMENT.open(encoding="utf-8-sig", newline="") as handle:
            statement = list(csv.DictReader(handle))
        self.assertGreater(len(statement), 1)
        self.assertWorks(self.add_bank_lines_from("inbox/statement.csv"))
        stored = self.rows("ledger_bank_lines.csv")
        self.assertEqual(len(stored), len(statement))
        self.assertEqual([(Decimal(row["amount_rm"]), row["bank_reference"]) for row in stored],
                         [(Decimal(row["amount_rm"]), row["bank_reference"]) for row in statement])

    def test_lembur_input_file_with_a_utf8_byte_order_mark_still_works(self):
        self.put("inbox/bom.csv", "\ufeffdate,description,type,amount_rm,bank_reference\r\n"
                 "2026-10-05,Transfer from Dana,income,5.00,REF-BOM-1\r\n"
                 "2026-10-06,Transfer from Mira,income,18.00,REF-BOM-2\r\n")
        self.assertWorks(self.add_bank_lines_from("inbox/bom.csv"))
        stored = self.rows("ledger_bank_lines.csv")
        self.assertEqual([(row["date"], row["bank_reference"]) for row in stored],
                         [("2026-10-05", "REF-BOM-1"), ("2026-10-06", "REF-BOM-2")])

    def test_lembur_input_file_outside_the_workspace_is_refused_and_nothing_is_written(self):
        shutil.copyfile(self.STATEMENT, self.outside / "statement.csv")
        before_outside, before_inside = self.outside_snapshot(), self.snapshot(self.ws)
        for path in ("../outside/statement.csv", "inbox/../../outside/statement.csv",
                     str(self.outside / "statement.csv")):
            with self.subTest(path=path):
                self.assertRefused(self.add_bank_lines_from(path))
        self.assertEqual(before_outside, self.outside_snapshot())
        self.assertEqual(before_inside, self.snapshot(self.ws))
        self.assertFalse((self.ws / "ledger_bank_lines.csv").exists())

    def test_lembur_input_and_input_file_together_are_refused(self):
        shutil.copyfile(self.STATEMENT, self.ws / "inbox" / "statement.csv")
        before = self.snapshot(self.ws)
        result = self.run_tool("bookkeeper", "lembur", {
            "command": "add-bank-lines", "input": [bank_line("REF-1")],
            "input_file": "inbox/statement.csv"})
        self.assertRefused(result)
        self.assertEqual(before, self.snapshot(self.ws))
        self.assertFalse((self.ws / "ledger_bank_lines.csv").exists())

    def test_lembur_input_file_that_does_not_exist_is_ok_false(self):
        before = self.snapshot(self.ws)
        self.assertRefused(self.add_bank_lines_from("inbox/missing.csv"))
        self.assertEqual(before, self.snapshot(self.ws))


if __name__ == "__main__":
    unittest.main()
