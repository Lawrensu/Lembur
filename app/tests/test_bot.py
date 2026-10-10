"""Offline contract tests for the package 3 Telegram front door."""

from concurrent.futures import Future
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

from app.bot import Bot


PLAN_FILES = {
    "plan_products.csv": (
        "product_id,name,price_rm,material_cost_rm,packaging_cost_rm,minutes_per_unit\n"
        "P01,Keychain,5.00,2.50,0.50,20\n"
    ),
    "plan_channels.csv": (
        "channel,fee_percent,fee_per_order_rm,shipping_cost_per_order_rm,"
        "fulfilment_minutes_per_order\ntelegram,0,0.00,0.00,3\n"
    ),
    "plan_assumptions.csv": (
        "admin_hours_per_week,planned_margin_percent,target_hourly_rate_rm\n"
        "2,40,12.00\n"
    ),
    "plan_change_log.csv": "changed_at,field,old_value,new_value,reason,source\n",
}
DAY = "2026-10-11"
WEEK = "2026-W41"
TIMESTAMP = int(datetime(2026, 10, 5, 12, 34, 56, tzinfo=timezone.utc).timestamp())
WAIT = 5


def message(text=None, chat_id=101, message_id=71, **fields):
    result = {"chat": {"id": chat_id}, "date": TIMESTAMP, "message_id": message_id}
    if text is not None:
        result["text"] = text
    result.update(fields)
    return result


def night_summary(**changes):
    result = {
        "week": WEEK,
        "payslip_day": False,
        "steps": [{"step": 5, "name": "Numbers", "agent": "payroll",
                   "status": "done", "note": "Saved figures."}],
        "figures": {"hourly_rate_rm": "03.1000", "take_home_rm": "019.3700",
                    "hours_total": "006.2500"},
        "payslip": "",
        "drafts": [],
        "review": [],
        "failed": {},
    }
    result.update(changes)
    return result


class FakeTelegram:
    def __init__(self):
        self.messages = []
        self.documents = []
        self.files = {}
        self.get_calls = []
        self.download_calls = []
        self.lock = threading.Lock()

    def add_file(self, file_id, content=b"synthetic receipt"):
        file_path = "telegram-files/" + file_id
        self.files[file_id] = (file_path, content)

    def send_message(self, chat_id, text):
        if not isinstance(text, str):
            raise AssertionError("Telegram replies must be text")
        with self.lock:
            self.messages.append((chat_id, text))

    def send_document(self, chat_id, path):
        path = Path(path)
        content = path.read_bytes()
        with self.lock:
            self.documents.append((chat_id, path, content))

    def get_file(self, file_id):
        with self.lock:
            self.get_calls.append(file_id)
            return {"file_path": self.files[file_id][0]}

    def download_file(self, file_path):
        with self.lock:
            self.download_calls.append(file_path)
            for stored_path, content in self.files.values():
                if stored_path == file_path:
                    return content
        raise AssertionError("Unexpected fake download")


class UnprintableError(Exception):
    def __str__(self):
        raise AssertionError("The bot must not stringify an exception")


class BotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        demo = self.root / "data" / "demo"
        demo.mkdir(parents=True)
        for name, content in PLAN_FILES.items():
            (demo / name).write_text(content, encoding="utf-8")
        self.telegram = FakeTelegram()
        self.current_day = DAY
        self.today = Mock(side_effect=lambda: self.current_day)
        self.summary = night_summary()
        self.runs = []
        self.run_night = Mock(side_effect=self.record_run)
        self.bots = []
        for target in ("urllib.request.urlopen", "socket.create_connection", "socket.socket.connect"):
            guard = patch(target, side_effect=AssertionError("Network is forbidden"))
            blocked = guard.start()
            self.addCleanup(guard.stop)
            self.addCleanup(blocked.assert_not_called)
        guard = patch("subprocess.run", side_effect=AssertionError("Unexpected subprocess"))
        blocked = guard.start()
        self.addCleanup(guard.stop)
        self.addCleanup(blocked.assert_not_called)
        self.addCleanup(self.close_bots)
        self.bot = self.new_bot()

    def close_bots(self):
        for bot in self.bots:
            bot.close()

    def new_bot(self, runner=None):
        bot = Bot(self.telegram, run_night=self.run_night if runner is None else runner,
                  repo_root=self.root, today=self.today)
        self.bots.append(bot)
        return bot

    def record_run(self, workspace, date, message):
        # This signature deliberately does not accept the runner's optional ask.
        self.runs.append((Path(workspace), date, message))
        return deepcopy(self.summary)

    def workspace(self, chat_id=101):
        return self.root / "workspaces" / str(chat_id)

    def initialize(self, chat_id=101):
        if not self.workspace(chat_id).exists():
            self.bot.handle_message(message("payslip", chat_id=chat_id))
            self.telegram.messages[:] = [item for item in self.telegram.messages if item[0] != chat_id]
            self.telegram.documents[:] = [item for item in self.telegram.documents if item[0] != chat_id]
        workspace = Path(self.bot._workspace(chat_id))
        self.assertEqual(workspace.resolve(), self.workspace(chat_id).resolve())
        return workspace

    def put(self, relative, content="synthetic fixture", chat_id=101):
        path = self.initialize(chat_id) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def replies(self, chat_id=101):
        return "\n".join(text for target, text in self.telegram.messages if target == chat_id)

    def clear_output(self):
        self.telegram.messages.clear()
        self.telegram.documents.clear()

    def protected_snapshot(self, chat_id=101):
        workspace = self.initialize(chat_id)
        for name in ("ledger_transactions.csv", "ledger_bank_lines.csv", "ledger_hours.csv"):
            path = workspace / name
            if not path.exists():
                path.write_text("unchanged synthetic ledger\n", encoding="utf-8")
        paths = list((workspace / "plan").glob("*.csv")) + list(workspace.glob("ledger_*.csv"))
        return {path: path.read_bytes() for path in paths}

    def assert_unchanged(self, snapshot):
        for path, content in snapshot.items():
            self.assertEqual(path.read_bytes(), content, str(path))

    def assert_generic_failure(self, marker="private-error-marker"):
        self.assertTrue(self.replies().strip())
        self.assertNotIn(marker, self.replies())
        self.assertNotIn(str(self.root), self.replies())
        self.assertNotIn("Traceback", self.replies())
        self.assertNotIn("Your board meeting is ready", self.replies())
        self.assertEqual(self.telegram.documents, [])

    def symlink(self, link, target, directory=False):
        link.parent.mkdir(parents=True, exist_ok=True)
        try:
            link.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest("Symlink privileges unavailable: " + type(error).__name__)
        if not link.is_symlink():
            self.skipTest("This filesystem does not expose a real symbolic link.")

    def test_first_message_copies_exactly_the_four_baseline_plan_files(self):
        (self.root / "data" / "demo" / "messages.md").write_text("not a plan", encoding="utf-8")
        self.bot.handle_message(message("Sold two keychains."))
        workspace = self.workspace()
        self.assertTrue(workspace.is_dir())
        self.assertTrue((workspace / "inbox").is_dir())
        self.assertEqual({path.name for path in (workspace / "plan").iterdir()}, set(PLAN_FILES))
        for name in PLAN_FILES:
            self.assertEqual((workspace / "plan" / name).read_bytes(),
                             (self.root / "data" / "demo" / name).read_bytes())
        self.assertEqual(self.runs, [(workspace, DAY, "Sold two keychains.")])

    def test_existing_workspace_corrections_survive_messages_and_bot_recreation(self):
        self.bot.handle_message(message("First night."))
        corrected = self.put("plan/plan_products.csv", "corrected minutes: 35\n")
        changes = self.put("plan/plan_change_log.csv", "student correction\n")
        self.bot.handle_message(message("Second night."))
        self.new_bot().handle_message(message("Third night."))
        self.assertEqual(corrected.read_text(encoding="utf-8"), "corrected minutes: 35\n")
        self.assertEqual(changes.read_text(encoding="utf-8"), "student correction\n")
        self.assertEqual(len(self.runs), 3)

    def test_existing_workspace_is_not_reseeded_when_a_plan_file_is_absent(self):
        self.initialize()
        missing = self.workspace() / "plan" / "plan_change_log.csv"
        missing.unlink()
        self.bot.handle_message(message("Keep my existing workspace."))
        self.assertFalse(missing.exists())

    def test_chat_workspaces_and_replies_are_isolated(self):
        self.bot.handle_message(message("First student's message.", chat_id=101))
        correction = self.put("plan/plan_products.csv", "first student's correction\n")
        self.bot.handle_message(message("Second student's message.", chat_id=-202))
        self.assertEqual([run[0] for run in self.runs], [self.workspace(101), self.workspace(-202)])
        self.assertEqual(correction.read_text(encoding="utf-8"), "first student's correction\n")
        self.assertEqual((self.workspace(-202) / "plan" / "plan_products.csv").read_text(
            encoding="utf-8"), PLAN_FILES["plan_products.csv"])
        self.assertTrue(self.replies(101))
        self.assertTrue(self.replies(-202))

    def test_noncommands_are_passed_to_runner_without_date_prefix_or_start_special_cases(self):
        texts = ["/start", "2026-10-05 Sold two keychains.", "Payslip", "REVIEW",
                 "Approve 2", "approve two", "payslip please", "review today"]
        for text in texts:
            with self.subTest(text=text):
                self.bot.handle_message(message(text))
                self.assertEqual(self.runs[-1], (self.workspace(), DAY, text))
        self.assertEqual(len(self.runs), len(texts))

    def test_today_is_evaluated_for_each_handled_message_not_telegram_date(self):
        self.bot.handle_message(message("First night."))
        self.current_day = "2026-10-12"
        self.bot.handle_message(message("2026-10-05 Second night."))
        self.assertEqual([run[1] for run in self.runs], [DAY, "2026-10-12"])
        self.assertGreaterEqual(self.today.call_count, 2)

    def test_document_is_saved_with_original_name_and_acknowledged_without_runner(self):
        self.telegram.add_file("receipt", b"receipt bytes")
        self.bot.handle_message(message(document={"file_id": "receipt", "file_name": "receipt.csv"}))
        path = self.workspace() / "inbox" / "receipt.csv"
        self.assertEqual(path.read_bytes(), b"receipt bytes")
        self.assertEqual(self.telegram.get_calls, ["receipt"])
        self.assertEqual(self.telegram.download_calls, ["telegram-files/receipt"])
        self.assertTrue(self.replies())
        self.run_night.assert_not_called()

    def test_document_without_original_name_gets_a_generated_name_without_running(self):
        self.telegram.add_file("unnamed", b"unnamed document")
        self.bot.handle_message(message(document={"file_id": "unnamed"}))
        files = list((self.workspace() / "inbox").iterdir())
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].name)
        self.assertEqual(files[0].read_bytes(), b"unnamed document")
        self.assertTrue(self.replies())
        self.run_night.assert_not_called()

    def test_blank_upload_caption_only_acknowledges_saved_document(self):
        self.telegram.add_file("blank-caption", b"saved document")
        self.bot.handle_message(message(document={"file_id": "blank-caption", "file_name": "receipt.csv"},
                                        caption=" \n\t "))
        self.assertEqual((self.workspace() / "inbox" / "receipt.csv").read_bytes(), b"saved document")
        self.assertTrue(self.replies())
        self.run_night.assert_not_called()

    def test_document_basename_handles_both_path_separators_and_windows_characters(self):
        names = ["../../receipt.csv", "C:\\private\\receipt.csv", "folder\\nested/receipt.csv",
                 'receipt<>:"|?*.csv']
        for index, original in enumerate(names):
            with self.subTest(name=original):
                chat_id = 300 + index
                self.telegram.add_file("upload-" + str(index), b"safe content")
                self.bot.handle_message(message(chat_id=chat_id, document={
                    "file_id": "upload-" + str(index), "file_name": original}))
                files = list((self.workspace(chat_id) / "inbox").iterdir())
                expected = re.sub(r'[<>:"/\\|?*]', "_", re.split(r"[/\\]", original)[-1])
                self.assertEqual([path.name for path in files], [expected])
                self.assertEqual(files[0].read_bytes(), b"safe content")
        self.run_night.assert_not_called()

    def test_duplicate_document_names_get_suffixes_without_overwriting(self):
        for file_id, content in (("original", b"first"), ("copy", b"second"), ("third", b"third")):
            self.telegram.add_file(file_id, content)
            self.bot.handle_message(message(document={"file_id": file_id, "file_name": "receipt.csv"}))
        files = list((self.workspace() / "inbox").iterdir())
        self.assertEqual(len(files), 3)
        self.assertEqual((self.workspace() / "inbox" / "receipt.csv").read_bytes(), b"first")
        self.assertEqual({path.read_bytes() for path in files}, {b"first", b"second", b"third"})
        self.assertTrue(all(path.suffix == ".csv" and path.stem.startswith("receipt") for path in files))
        self.run_night.assert_not_called()

    def test_document_caption_runs_only_after_download_is_saved(self):
        self.telegram.add_file("captioned", b"saved before caption")
        observed = []

        def runner(workspace, date, message):
            observed.append(((Path(workspace) / "inbox" / "receipt.csv").read_bytes(), date, message))
            return night_summary()

        run = Mock(side_effect=runner)
        self.new_bot(run).handle_message(message(document={"file_id": "captioned", "file_name": "receipt.csv"},
                                                caption="Sold two today."))
        run.assert_called_once()
        self.assertEqual(observed, [(b"saved before caption", DAY, "Sold two today.")])
        self.assertIn("partial", self.replies().lower())

    def test_fixed_caption_is_processed_after_save_without_runner(self):
        payslip = self.put("payslips/" + WEEK + ".html")
        self.telegram.add_file("captioned", b"caption upload")
        self.bot.handle_message(message(document={"file_id": "captioned", "file_name": "receipt.csv"},
                                        caption="  payslip  "))
        self.assertEqual((self.workspace() / "inbox" / "receipt.csv").read_bytes(), b"caption upload")
        self.assertEqual([item[1] for item in self.telegram.documents], [payslip])
        self.run_night.assert_not_called()

    def test_photo_uses_largest_variant_and_incoming_timestamp_and_message_id(self):
        self.telegram.add_file("small", b"thumbnail")
        self.telegram.add_file("large", b"full photo")
        photos = [{"file_id": "small", "width": 90, "height": 90, "file_size": 9},
                  {"file_id": "large", "width": 1200, "height": 900, "file_size": 9000}]
        for message_id in (71, 72):
            self.bot.handle_message(message(message_id=message_id, photo=photos))
        files = list((self.workspace() / "inbox").iterdir())
        self.assertEqual(len(files), 2)
        self.assertEqual(self.telegram.get_calls, ["large", "large"])
        for message_id in (71, 72):
            candidates = [path for path in files if str(message_id) in path.stem]
            self.assertEqual(len(candidates), 1)
            digits = re.sub(r"\D", "", candidates[0].stem)
            self.assertIn("20261005", digits)
            self.assertTrue("123456" in digits or "203456" in digits)
            self.assertEqual(candidates[0].read_bytes(), b"full photo")
        self.run_night.assert_not_called()
        self.assertTrue(self.replies())

    def test_photo_caption_sees_saved_photo_and_runs_once(self):
        self.telegram.add_file("photo", b"photo bytes")
        observed = []

        def runner(workspace, date, message):
            files = list((Path(workspace) / "inbox").iterdir())
            observed.append(([path.read_bytes() for path in files], date, message))
            return night_summary()

        run = Mock(side_effect=runner)
        self.new_bot(run).handle_message(message(photo=[{"file_id": "photo", "width": 900,
                                                        "height": 900, "file_size": 100}],
                                                caption="Event lasted two hours."))
        run.assert_called_once()
        self.assertEqual(observed, [([b"photo bytes"], DAY, "Event lasted two hours.")])
        self.assertIn("partial", self.replies().lower())

    def test_same_document_name_is_independent_between_chats(self):
        for chat_id, file_id, content in ((101, "first", b"first chat"), (202, "second", b"second chat")):
            self.telegram.add_file(file_id, content)
            self.bot.handle_message(message(chat_id=chat_id, document={"file_id": file_id,
                                                                      "file_name": "receipt.csv"}))
            self.assertEqual((self.workspace(chat_id) / "inbox" / "receipt.csv").read_bytes(), content)
        self.assertEqual((self.workspace(101) / "inbox" / "receipt.csv").read_bytes(), b"first chat")
        self.run_night.assert_not_called()

    def test_malformed_uploads_do_not_run_captions_or_save_files(self):
        uploads = [{"document": {}}, {"document": {"file_id": "", "file_name": "receipt.csv"}},
                   {"document": {"file_id": None, "file_name": "receipt.csv"}},
                   {"document": {"file_id": "unused", "file_name": ".."}},
                   {"document": "not a document"}, {"photo": [{}]}]
        for upload in uploads:
            with self.subTest(upload=upload):
                self.clear_output()
                self.bot.handle_message(message(caption="Do not run this caption.", **upload))
                self.assert_generic_failure()
                self.assertEqual(list((self.workspace() / "inbox").iterdir()), [])
        self.run_night.assert_not_called()

    def test_invalid_download_results_do_not_run_caption(self):
        for metadata, content in (({}, b"unused"), ({"file_path": ""}, b"unused"),
                                  ({"file_path": "remote"}, "not bytes")):
            with self.subTest(metadata=metadata, content=content):
                self.clear_output()
                with patch.object(self.telegram, "get_file", return_value=metadata), \
                        patch.object(self.telegram, "download_file", return_value=content):
                    self.bot.handle_message(message(document={"file_id": "bad", "file_name": "receipt.csv"},
                                                    caption="Do not run."))
                self.assert_generic_failure()
                self.assertEqual(list((self.workspace() / "inbox").iterdir()), [])
        self.run_night.assert_not_called()

    def test_upload_errors_are_generic_and_never_stringify_exceptions(self):
        self.telegram.add_file("receipt")
        for method in ("get_file", "download_file"):
            for error in (RuntimeError("private-error-marker " + str(self.root)), UnprintableError()):
                with self.subTest(method=method, error_type=type(error).__name__):
                    self.clear_output()
                    with patch.object(self.telegram, method, side_effect=error):
                        self.bot.handle_message(message(document={"file_id": "receipt", "file_name": "receipt.csv"},
                                                        caption="Never run a failed upload."))
                    self.assert_generic_failure()
        self.run_night.assert_not_called()

    def test_upload_collision_with_external_symlink_does_not_overwrite_its_target(self):
        self.initialize()
        outside = self.root / "private-error-marker.csv"
        outside.write_bytes(b"outside original")
        link = self.workspace() / "inbox" / "receipt.csv"
        self.symlink(link, outside)
        self.telegram.add_file("collision", b"new upload")
        self.bot.handle_message(message(document={"file_id": "collision", "file_name": "receipt.csv"}))
        self.assertEqual(outside.read_bytes(), b"outside original")
        self.assertTrue(link.is_symlink())
        regular_files = [path for path in link.parent.iterdir() if not path.is_symlink()]
        if regular_files:
            self.assertEqual([path.read_bytes() for path in regular_files], [b"new upload"])
            self.assertTrue(regular_files[0].resolve().is_relative_to(self.workspace().resolve()))
        else:
            self.assert_generic_failure()
        self.assertNotIn("outside original", self.replies())
        self.run_night.assert_not_called()

    def test_payslip_chooses_latest_week_and_prefers_its_pdf_with_verbatim_rate(self):
        self.put("payslips/2026-W40.pdf", b"older pdf")
        self.put("payslips/" + WEEK + ".html", "latest html")
        latest = self.put("payslips/" + WEEK + ".pdf", b"latest pdf")
        self.put("payslips/not-a-week.pdf", b"ignore")
        self.put("audit/2026-W40/numbers.json", json.dumps({"hourly_rate_rm": "99.9900"}))
        self.put("audit/" + WEEK + "/numbers.json", json.dumps({"hourly_rate_rm": "03.1000"}))
        snapshot = self.protected_snapshot()
        self.bot.handle_message(message(" \n payslip \t"))
        self.assertEqual(self.telegram.documents, [(101, latest, b"latest pdf")])
        self.assertIn("03.1000", self.replies())
        self.assertNotIn("99.9900", self.replies())
        self.run_night.assert_not_called()
        self.assert_unchanged(snapshot)

    def test_latest_html_wins_over_an_older_pdf_across_year_boundary(self):
        self.put("payslips/2026-W53.pdf", b"older pdf")
        latest = self.put("payslips/2027-W01.html", "latest html")
        self.bot.handle_message(message("payslip"))
        self.assertEqual([item[1] for item in self.telegram.documents], [latest])
        self.run_night.assert_not_called()

    def test_missing_numbers_or_rate_hides_rate_instead_of_inventing_it(self):
        for index, numbers in enumerate((None, {}, {"take_home_rm": "19.37"}, {"hourly_rate_rm": ""})):
            with self.subTest(numbers=numbers):
                chat_id = 400 + index
                self.put("payslips/" + WEEK + ".html", chat_id=chat_id)
                self.put("audit/2026-W40/numbers.json", json.dumps({"hourly_rate_rm": "88.8800"}), chat_id)
                if numbers is not None:
                    self.put("audit/" + WEEK + "/numbers.json", json.dumps(numbers), chat_id)
                self.bot.handle_message(message("payslip", chat_id=chat_id))
                text = self.replies(chat_id).lower()
                self.assertNotIn("88.8800", text)
                self.assertNotIn("rm0", text.replace(" ", ""))
                self.assertNotIn("none", text)
                self.assertNotIn("hourly rate", text)
                self.assertEqual(len([item for item in self.telegram.documents if item[0] == chat_id]), 1)
        self.run_night.assert_not_called()

    def test_no_payslip_gives_reply_without_runner_or_attachment(self):
        self.bot.handle_message(message("payslip"))
        self.assertTrue(self.replies())
        self.assertEqual(self.telegram.documents, [])
        self.run_night.assert_not_called()

    def test_payslip_in_one_chat_cannot_be_retrieved_from_another(self):
        self.put("payslips/" + WEEK + ".pdf", b"first chat only")
        self.bot.handle_message(message("payslip", chat_id=202))
        self.assertTrue(self.replies(202))
        self.assertEqual(self.telegram.documents, [])
        self.run_night.assert_not_called()

    def test_review_uses_latest_audit_week_and_read_only_subprocess(self):
        self.put("audit/2026-W40/numbers.json", "{}")
        self.put("audit/" + WEEK + "/review_items.md", "source lines")
        self.put("payslips/2027-W01.html", "not the review week")
        snapshot = self.protected_snapshot()
        result = {"transactions": [{"txn_id": "T0042", "date": "2026-10-08",
                                    "reconciliation_status": "needs_review", "amount_rm": "007.2500",
                                    "description": "Blurry receipt", "notes": "Confirm supplier amount"}],
                  "review_items": ["Confirm the bazaar hours.", "Check the missing receipt."]}
        completed = subprocess.CompletedProcess([], 0, stdout=json.dumps(result), stderr="")
        with patch("subprocess.run", return_value=completed) as run:
            self.bot.handle_message(message("  review  "))
        run.assert_called_once()
        self.assert_review_command(run, WEEK)
        for expected in ("T0042", "needs_review", "007.2500", "Confirm supplier amount",
                         "Confirm the bazaar hours.", "Check the missing receipt."):
            self.assertIn(expected, self.replies())
        self.assertEqual(self.telegram.documents, [])
        self.run_night.assert_not_called()
        self.assert_unchanged(snapshot)

    def assert_review_command(self, run, week):
        args, kwargs = run.call_args
        command = args[0] if args else kwargs["args"]
        self.assertIsInstance(command, (list, tuple))
        words = [str(word) for word in command]
        self.assertTrue(any(word.replace("\\", "/").endswith("tools/lembur.py") for word in words))
        self.assertIn("review", words)
        self.assertEqual(words[words.index("--week") + 1], week)
        self.assertEqual(Path(words[words.index("--workspace") + 1]).resolve(), self.workspace().resolve())
        self.assertIs(kwargs.get("capture_output"), True)
        self.assertFalse(kwargs.get("shell", False))
        self.assertNotIn("input", kwargs)

    def test_review_without_audit_uses_the_injected_today_iso_week(self):
        self.current_day = "2027-01-04"
        completed = subprocess.CompletedProcess([], 0, stdout='{"transactions": [], "review_items": []}', stderr="")
        with patch("subprocess.run", return_value=completed) as run:
            self.bot.handle_message(message("review"))
        self.assert_review_command(run, "2027-W01")
        self.assertTrue(self.replies())
        self.run_night.assert_not_called()

    def test_review_failures_do_not_echo_stderr_or_stringify_exceptions(self):
        failures = [subprocess.CompletedProcess([], 1, stdout="", stderr="private-error-marker"),
                    subprocess.CompletedProcess([], 0, stdout="private-error-marker", stderr=""),
                    RuntimeError("private-error-marker"), UnprintableError()]
        for failure in failures:
            with self.subTest(result_type=type(failure).__name__):
                self.clear_output()
                options = {"side_effect": failure} if isinstance(failure, Exception) else {"return_value": failure}
                with patch("subprocess.run", **options):
                    self.bot.handle_message(message("review"))
                self.assert_generic_failure()
        self.run_night.assert_not_called()

    def test_approve_moves_only_selected_numbered_draft_and_preserves_ledgers(self):
        older = self.put("approvals/2026-W40/2_old.md", "older draft")
        first = self.put("approvals/" + WEEK + "/1_post.md", "first draft")
        selected = self.put("approvals/" + WEEK + "/2_supplier.md", "selected draft")
        twentieth = self.put("approvals/" + WEEK + "/20_post.md", "twentieth draft")
        self.put("approvals/2026-W42/notes.txt", "not a numbered markdown draft")
        self.put("approvals/2026-W42/readme.md", "not a numbered markdown draft")
        snapshot = self.protected_snapshot()
        self.bot.handle_message(message("  approve 2  "))
        destination = selected.parent / "approved" / selected.name
        self.assertFalse(selected.exists())
        self.assertEqual(destination.read_text(encoding="utf-8"), "selected draft")
        for path in (older, first, twentieth):
            self.assertTrue(path.exists())
        self.assertTrue(self.replies())
        self.assertEqual(self.telegram.documents, [])
        self.run_night.assert_not_called()
        self.assert_unchanged(snapshot)

    def test_skip_leaves_selected_draft_pending_and_confirms(self):
        pending = self.put("approvals/" + WEEK + "/2_supplier.md", "unchanged draft")
        snapshot = self.protected_snapshot()
        self.bot.handle_message(message("  skip 2  "))
        self.assertEqual(pending.read_text(encoding="utf-8"), "unchanged draft")
        self.assertFalse((pending.parent / "approved" / pending.name).exists())
        self.assertTrue(self.replies())
        self.assertEqual(self.telegram.documents, [])
        self.run_night.assert_not_called()
        self.assert_unchanged(snapshot)

    def test_latest_week_includes_already_approved_numbered_drafts(self):
        older = self.put("approvals/2026-W40/2_old.md", "do not approve an older week")
        approved = self.put("approvals/" + WEEK + "/approved/1_post.md", "already approved")
        for command in ("approve 2", "skip 2", "approve 1"):
            with self.subTest(command=command):
                self.clear_output()
                self.bot.handle_message(message(command))
                self.assertTrue(older.exists())
                self.assertEqual(approved.read_text(encoding="utf-8"), "already approved")
                self.assertTrue(self.replies())
                self.assertEqual(self.telegram.documents, [])
        self.run_night.assert_not_called()

    def test_missing_and_ambiguous_draft_numbers_do_not_change_files_or_run(self):
        first = self.put("approvals/" + WEEK + "/2_post.md", "first")
        second = self.put("approvals/" + WEEK + "/2_supplier.md", "second")
        for command in ("approve 2", "skip 2", "approve 99", "skip 99"):
            with self.subTest(command=command):
                self.clear_output()
                self.bot.handle_message(message(command))
                self.assertEqual(first.read_text(encoding="utf-8"), "first")
                self.assertEqual(second.read_text(encoding="utf-8"), "second")
                self.assertFalse((first.parent / "approved" / first.name).exists())
                self.assertFalse((second.parent / "approved" / second.name).exists())
                self.assertTrue(self.replies())
                self.assertEqual(self.telegram.documents, [])
        self.run_night.assert_not_called()

    def test_approval_does_not_overwrite_an_existing_approved_file(self):
        pending = self.put("approvals/" + WEEK + "/2_supplier.md", "pending version")
        approved = self.put("approvals/" + WEEK + "/approved/2_supplier.md", "approved version")
        self.bot.handle_message(message("approve 2"))
        self.assertEqual(pending.read_text(encoding="utf-8"), "pending version")
        self.assertEqual(approved.read_text(encoding="utf-8"), "approved version")
        self.assertTrue(self.replies())
        self.run_night.assert_not_called()

    def test_approval_in_another_chat_does_not_move_first_chat_draft(self):
        pending = self.put("approvals/" + WEEK + "/2_supplier.md", "first chat only")
        self.bot.handle_message(message("approve 2", chat_id=202))
        self.assertTrue(pending.exists())
        self.assertTrue(self.replies(202))
        self.run_night.assert_not_called()

    def test_successful_payslip_day_reports_verbatim_figures_review_and_numbered_drafts(self):
        payslip = self.put("payslips/" + WEEK + ".html", "ready payslip")
        first = self.put("approvals/" + WEEK + "/1_post.md", "first draft")
        second = self.put("approvals/" + WEEK + "/2_supplier.md", "second draft")
        self.summary = night_summary(payslip_day=True, payslip=str(payslip),
                                     drafts=[{"number": 1, "file": str(first.relative_to(self.workspace()))},
                                             {"number": 2, "file": str(second.relative_to(self.workspace()))}],
                                     review=["Check the unmatched receipt.", "Confirm the event hours."])
        self.bot.handle_message(message("Sunday night message."))
        text = self.replies()
        self.assertIn("Your board meeting is ready", text)
        for value in self.summary["figures"].values():
            self.assertIn(value, text)
        for line in self.summary["review"]:
            self.assertIn(line, text)
        for draft in self.summary["drafts"]:
            filename = Path(draft["file"]).name
            self.assertIn(filename, text)
            self.assertRegex(text, rf"(?m)^.*\b{draft['number']}\b.*{re.escape(filename)}")
        self.assertIn((101, payslip, b"ready payslip"), self.telegram.documents)
        self.assertTrue(all(path.resolve().is_relative_to(self.workspace().resolve())
                            for _, path, _ in self.telegram.documents))
        self.assertTrue(first.exists())
        self.assertTrue(second.exists())

    def test_workspace_relative_payslip_from_runner_is_resolved_inside_workspace(self):
        payslip = self.put("payslips/" + WEEK + ".html", "relative payslip")
        self.summary = night_summary(payslip_day=True, payslip="payslips/" + WEEK + ".html")
        self.bot.handle_message(message("Sunday night."))
        self.assertIn((101, payslip, b"relative payslip"), self.telegram.documents)

    def test_non_payslip_day_is_explicitly_partial_and_has_no_morning_success(self):
        self.summary = night_summary(failed=None, review=["Confirm one receipt."])
        self.bot.handle_message(message("Monday night."))
        self.assertIn("partial", self.replies().lower())
        self.assertNotIn("Your board meeting is ready", self.replies())
        for value in self.summary["figures"].values():
            self.assertIn(value, self.replies())
        self.assertIn("Confirm one receipt.", self.replies())
        self.assertEqual(self.telegram.documents, [])

    def test_failed_night_never_reports_success_or_attaches_even_if_summary_has_payslip(self):
        payslip = self.put("payslips/" + WEEK + ".html", "do not attach")
        self.summary = night_summary(payslip_day=True, payslip=str(payslip),
                                     failed={"step": 8, "reason": "Audit did not finish."},
                                     steps=[{"step": 8, "name": "Audit", "agent": "auditor",
                                             "status": "failed", "note": "Audit did not finish."}])
        self.bot.handle_message(message("Sunday night."))
        self.assertTrue(self.replies())
        self.assertNotIn("Your board meeting is ready", self.replies())
        self.assertEqual(self.telegram.documents, [])
        self.run_night.assert_called_once()

    def test_runner_exceptions_are_generic_and_never_stringified(self):
        for error in (RuntimeError("private-error-marker " + str(self.root)), UnprintableError()):
            with self.subTest(error_type=type(error).__name__):
                self.clear_output()
                self.run_night.side_effect = error
                self.bot.handle_message(message("Tonight's message."))
                self.assert_generic_failure()

    def test_runner_payslip_paths_cannot_leave_workspace_or_cross_chat(self):
        outside = self.root / "private-error-marker.html"
        outside.write_text("outside confidential fixture", encoding="utf-8")
        other = self.put("payslips/" + WEEK + ".html", "other chat confidential fixture", chat_id=202)
        for path in (str(outside), "../../private-error-marker.html", str(other)):
            with self.subTest(path=path):
                self.clear_output()
                self.summary = night_summary(payslip_day=True, payslip=path)
                self.bot.handle_message(message("Sunday night."))
                self.assert_generic_failure()
                self.assertNotIn("confidential fixture", self.replies())
        self.assertEqual(outside.read_text(encoding="utf-8"), "outside confidential fixture")

    def test_runner_draft_paths_cannot_leave_workspace(self):
        outside = self.root / "private-error-marker.md"
        outside.write_text("outside confidential fixture", encoding="utf-8")
        payslip = self.put("payslips/" + WEEK + ".html", "valid payslip")
        for path in (str(outside), "../../private-error-marker.md"):
            with self.subTest(path=path):
                self.clear_output()
                self.summary = night_summary(payslip_day=True, payslip=str(payslip),
                                             drafts=[{"number": 2, "file": path}])
                self.bot.handle_message(message("Sunday night."))
                self.assert_generic_failure()
                self.assertNotIn("outside confidential fixture", self.replies())

    def test_workspace_validation_rejects_chat_symlink_outside_workspaces(self):
        outside = self.root / "private-error-marker"
        outside.mkdir()
        self.symlink(self.workspace(), outside, directory=True)
        with self.assertRaises(Exception):
            self.bot._workspace(101)
        self.bot.handle_message(message("Do not initialize this symlink."))
        self.assert_generic_failure()
        self.assertEqual(list(outside.iterdir()), [])
        self.run_night.assert_not_called()

    def test_workspace_validation_rejects_a_symlinked_workspaces_root(self):
        outside = self.root / "private-error-marker"
        outside.mkdir()
        workspaces = self.root / "workspaces"
        if workspaces.exists():
            workspaces.rmdir()
        self.symlink(workspaces, outside, directory=True)
        with self.assertRaises(Exception):
            self.bot._workspace(101)
        self.bot.handle_message(message("Do not create an external workspace."))
        self.assert_generic_failure()
        self.assertEqual(list(outside.iterdir()), [])
        self.run_night.assert_not_called()

    def test_document_cannot_write_through_symlinked_inbox(self):
        self.initialize()
        outside = self.root / "private-error-marker"
        outside.mkdir()
        inbox = self.workspace() / "inbox"
        inbox.rmdir()
        self.symlink(inbox, outside, directory=True)
        self.telegram.add_file("receipt", b"do not save outside")
        self.bot.handle_message(message(document={"file_id": "receipt", "file_name": "receipt.csv"},
                                        caption="Never run."))
        self.assert_generic_failure()
        self.assertEqual(list(outside.iterdir()), [])
        self.run_night.assert_not_called()

    def test_payslip_cannot_send_a_symlinked_file_outside_workspace(self):
        outside = self.root / "private-error-marker.pdf"
        outside.write_bytes(b"outside confidential fixture")
        self.initialize()
        self.symlink(self.workspace() / "payslips" / (WEEK + ".pdf"), outside)
        self.bot.handle_message(message("payslip"))
        self.assert_generic_failure()
        self.run_night.assert_not_called()

    def test_payslip_rate_cannot_be_read_through_a_symlink_outside_workspace(self):
        self.put("payslips/" + WEEK + ".html")
        outside = self.root / "private-error-marker.json"
        outside.write_text(json.dumps({"hourly_rate_rm": "external-confidential-rate"}), encoding="utf-8")
        self.symlink(self.workspace() / "audit" / WEEK / "numbers.json", outside)
        self.bot.handle_message(message("payslip"))
        self.assertNotIn("external-confidential-rate", self.replies())
        self.assertTrue(self.replies())
        self.run_night.assert_not_called()

    def test_review_rejects_a_symlinked_audit_week_without_running_subprocess(self):
        self.initialize()
        outside = self.root / "private-error-marker"
        outside.mkdir()
        (outside / "review_items.md").write_text("outside confidential review", encoding="utf-8")
        self.symlink(self.workspace() / "audit" / WEEK, outside, directory=True)
        completed = subprocess.CompletedProcess([], 0, stdout='{"transactions": [], "review_items": []}', stderr="")
        with patch("subprocess.run", return_value=completed) as run:
            self.bot.handle_message(message("review"))
        run.assert_not_called()
        self.assert_generic_failure()
        self.assertNotIn("outside confidential review", self.replies())
        self.run_night.assert_not_called()

    def test_runner_cannot_attach_a_symlinked_payslip_outside_workspace(self):
        self.initialize()
        outside = self.root / "private-error-marker.html"
        outside.write_text("outside confidential payslip", encoding="utf-8")
        path = self.workspace() / "payslips" / (WEEK + ".html")
        self.symlink(path, outside)
        self.summary = night_summary(payslip_day=True, payslip=str(path))
        self.bot.handle_message(message("Sunday night."))
        self.assert_generic_failure()

    def test_approve_rejects_a_draft_symlink_outside_workspace(self):
        outside = self.root / "private-error-marker.md"
        outside.write_text("outside draft", encoding="utf-8")
        self.initialize()
        pending = self.workspace() / "approvals" / WEEK / "2_supplier.md"
        self.symlink(pending, outside)
        self.bot.handle_message(message("approve 2"))
        self.assert_generic_failure()
        self.assertTrue(pending.is_symlink())
        self.assertEqual(outside.read_text(encoding="utf-8"), "outside draft")
        self.run_night.assert_not_called()

    def test_approve_cannot_move_into_a_symlinked_approved_directory(self):
        pending = self.put("approvals/" + WEEK + "/2_supplier.md", "pending draft")
        outside = self.root / "private-error-marker"
        outside.mkdir()
        self.symlink(pending.parent / "approved", outside, directory=True)
        self.bot.handle_message(message("approve 2"))
        self.assert_generic_failure()
        self.assertEqual(pending.read_text(encoding="utf-8"), "pending draft")
        self.assertEqual(list(outside.iterdir()), [])
        self.run_night.assert_not_called()

    def test_submit_serializes_same_chat_and_uses_today_when_queued_message_is_handled(self):
        first_started = threading.Event()
        first_finished = threading.Event()
        second_started = threading.Event()
        other_started = threading.Event()
        release = threading.Event()
        self.addCleanup(release.set)
        calls = []
        lock = threading.Lock()

        def runner(workspace, date, message):
            with lock:
                calls.append((Path(workspace), date, message))
            if message == "first":
                first_started.set()
                self.assertTrue(release.wait(WAIT), "First night was not released")
                first_finished.set()
            elif message == "second":
                second_started.set()
                self.assertTrue(first_finished.is_set(), "Same-chat nights overlapped")
            elif message == "other":
                other_started.set()
            return night_summary()

        bot = self.new_bot(runner)
        first = bot.submit(message("first"))
        self.assertIsInstance(first, Future)
        self.assertTrue(first_started.wait(WAIT), "First night did not start")
        second = bot.submit(message("second", message_id=72))
        other = bot.submit(message("other", chat_id=202))
        self.assertIsInstance(second, Future)
        self.assertTrue(other_started.wait(WAIT), "Another chat was blocked by the first chat")
        self.assertFalse(second_started.is_set(), "Queued same-chat night started too soon")
        self.current_day = "2026-10-12"
        release.set()
        first.result(timeout=WAIT)
        second.result(timeout=WAIT)
        other.result(timeout=WAIT)
        same_chat = [call for call in calls if call[0] == self.workspace()]
        self.assertEqual(same_chat, [(self.workspace(), DAY, "first"),
                                     (self.workspace(), "2026-10-12", "second")])

    def test_different_chat_nights_execute_concurrently(self):
        started_a = threading.Event()
        started_b = threading.Event()
        release = threading.Event()
        self.addCleanup(release.set)

        def runner(workspace, date, message):
            (started_a if Path(workspace) == self.workspace(101) else started_b).set()
            self.assertTrue(release.wait(WAIT), "Concurrent night was not released")
            return night_summary()

        bot = self.new_bot(runner)
        first = bot.submit(message("first", chat_id=101))
        self.assertTrue(started_a.wait(WAIT), "First chat did not start")
        second = bot.submit(message("second", chat_id=202))
        self.assertTrue(started_b.wait(WAIT), "Second chat did not execute concurrently")
        self.assertFalse(first.done())
        self.assertFalse(second.done())
        release.set()
        first.result(timeout=WAIT)
        second.result(timeout=WAIT)
        self.assertTrue(self.replies(101))
        self.assertTrue(self.replies(202))

    def test_fixed_approval_submitted_during_night_waits_for_the_same_chat(self):
        pending = self.put("approvals/" + WEEK + "/2_supplier.md", "pending draft")
        started = threading.Event()
        other_started = threading.Event()
        release = threading.Event()
        self.addCleanup(release.set)

        def runner(workspace, date, message):
            if Path(workspace) == self.workspace():
                started.set()
                self.assertTrue(release.wait(WAIT), "Night was not released")
            else:
                other_started.set()
            return night_summary()

        bot = self.new_bot(runner)
        first = bot.submit(message("running night"))
        self.assertTrue(started.wait(WAIT))
        approval = bot.submit(message("approve 2", message_id=72))
        other = bot.submit(message("other chat", chat_id=202))
        self.assertTrue(other_started.wait(WAIT))
        self.assertFalse(approval.done())
        self.assertTrue(pending.exists())
        release.set()
        first.result(timeout=WAIT)
        approval.result(timeout=WAIT)
        other.result(timeout=WAIT)
        self.assertFalse(pending.exists())
        self.assertEqual((pending.parent / "approved" / pending.name).read_text(encoding="utf-8"),
                         "pending draft")

    def test_runner_failure_does_not_stall_the_next_queued_message(self):
        def runner(workspace, date, message):
            if message == "fail":
                raise UnprintableError()
            return night_summary()

        bot = self.new_bot(runner)
        first = bot.submit(message("fail"))
        second = bot.submit(message("next", message_id=72))
        first.result(timeout=WAIT)
        second.result(timeout=WAIT)
        self.assertIn("partial", self.replies().lower())
        self.assertEqual(self.telegram.documents, [])

    def test_initialization_failure_leaves_no_partial_chat_and_retry_seeds_plan(self):
        with patch("app.bot.shutil.copyfile", side_effect=OSError("synthetic copy failure")):
            self.bot.handle_message(message("First night."))
        self.assertFalse(self.workspace().exists())
        self.run_night.assert_not_called()
        self.bot.handle_message(message("Retry night."))
        self.assertEqual({p.name for p in (self.workspace() / "plan").iterdir()}, set(PLAN_FILES))
        self.run_night.assert_called_once()

    def test_junction_checks_reject_chat_and_path_components(self):
        self.initialize()
        real = Path.is_junction
        for blocked in (self.root / "workspaces", self.workspace(), self.workspace() / "inbox"):
            with self.subTest(path=blocked):
                with patch.object(Path, "is_junction", lambda path: path == blocked or real(path)):
                    with self.assertRaises(Exception):
                        if blocked.name == "inbox":
                            self.bot._safe_path(self.workspace(), "inbox/file.txt")
                        else:
                            self.bot._workspace(101)

    def test_close_completes_queued_work_and_shuts_down_submit(self):
        started = threading.Event()
        release = threading.Event()
        self.addCleanup(release.set)

        def runner(workspace, date, message):
            started.set()
            self.assertTrue(release.wait(WAIT), "Night was not released")
            return night_summary()

        bot = self.new_bot(runner)
        first = bot.submit(message("first"))
        self.assertTrue(started.wait(WAIT))
        second = bot.submit(message("second", message_id=72))
        release.set()
        bot.close()
        self.bots.remove(bot)
        self.assertTrue(first.done())
        self.assertTrue(second.done())
        first.result(timeout=WAIT)
        second.result(timeout=WAIT)
        with self.assertRaises(RuntimeError):
            bot.submit(message("after close"))


if __name__ == "__main__":
    unittest.main()
