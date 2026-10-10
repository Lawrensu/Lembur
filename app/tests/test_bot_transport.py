"""Offline transport and polling tests using only synthetic Telegram credentials."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import traceback
from types import ModuleType
import unittest
from unittest.mock import MagicMock, Mock, call, patch
import urllib.error

from app import bot


TOKEN = "123:fake_token"
DAY = "2026-10-11"


class BotTransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        environment = patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": TOKEN})
        environment.start()
        self.addCleanup(environment.stop)
        transport = patch("app.bot.urllib.request.urlopen",
                          side_effect=AssertionError("Unexpected transport call"))
        self.urlopen = transport.start()
        self.addCleanup(transport.stop)
        for target in ("socket.create_connection", "socket.socket.connect"):
            guard = patch(target, side_effect=AssertionError("Network is forbidden"))
            blocked = guard.start()
            self.addCleanup(guard.stop)
            self.addCleanup(blocked.assert_not_called)
        self.telegram = bot.Telegram(TOKEN)
        self.response = MagicMock()
        self.response.__enter__.return_value = self.response

    def respond(self, content):
        self.response.read.return_value = content
        self.urlopen.side_effect = None
        self.urlopen.return_value = self.response

    def test_get_updates_posts_offset_timeout_and_message_filter(self):
        updates = [{"update_id": 72, "message": {"chat": {"id": 101}, "text": "payslip"}}]
        self.respond(json.dumps({"ok": True, "result": updates}).encode("utf-8"))

        self.assertEqual(self.telegram.get_updates(offset=71), updates)

        self.urlopen.assert_called_once()
        request = self.urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.telegram.org/bot" + TOKEN + "/getUpdates")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(json.loads(request.data.decode("utf-8")),
                         {"offset": 71, "timeout": 25, "allowed_updates": ["message"]})
        self.assertEqual(self.urlopen.call_args.kwargs, {"timeout": 40})
        self.response.__exit__.assert_called_once()

    def test_get_file_posts_file_id_and_returns_metadata(self):
        metadata = {"file_id": "synthetic-file", "file_path": "documents/receipt.txt"}
        self.respond(json.dumps({"ok": True, "result": metadata}).encode("utf-8"))

        self.assertEqual(self.telegram.get_file("synthetic-file"), metadata)

        self.urlopen.assert_called_once()
        request = self.urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.telegram.org/bot" + TOKEN + "/getFile")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(json.loads(request.data.decode("utf-8")), {"file_id": "synthetic-file"})

    def test_download_file_encodes_path_and_returns_exact_bytes(self):
        content = b"synthetic download\x00\xff"
        self.respond(content)

        self.assertEqual(self.telegram.download_file("documents/résumé 100% #?.txt"), content)

        self.urlopen.assert_called_once()
        request = self.urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.telegram.org/file/bot" + TOKEN
                         + "/documents/r%C3%A9sum%C3%A9%20100%25%20%23%3F.txt")
        self.assertEqual(request.get_method(), "GET")
        self.assertIsNone(request.data)
        self.assertEqual(self.urlopen.call_args.kwargs, {"timeout": 40})

    def test_download_file_rejects_urls_and_traversal_before_transport(self):
        paths = ("https://example.invalid/receipt.txt", "//example.invalid/receipt.txt",
                 "../receipt.txt", "documents/../receipt.txt", "documents/./receipt.txt",
                 "/receipt.txt", "documents//receipt.txt", "documents\\receipt.txt")
        for path in paths:
            with self.subTest(path=path):
                with self.assertRaises(bot.BotError) as caught:
                    self.telegram.download_file(path)
                self.assertEqual(str(caught.exception), "Telegram file path is invalid.")
        self.urlopen.assert_not_called()

    def test_send_document_posts_multipart_utf8_filename_and_exact_bytes(self):
        path = self.root / "résumé café.txt"
        content = "Café total: RM 7.25\n".encode("utf-8") + b"\x00\xff"
        path.write_bytes(content)
        self.respond(b'{"ok": true, "result": {"message_id": 73}}')

        self.telegram.send_document(101, path)

        self.urlopen.assert_called_once()
        request = self.urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.telegram.org/bot" + TOKEN + "/sendDocument")
        self.assertEqual(request.get_method(), "POST")
        content_type = request.get_header("Content-type")
        self.assertTrue(content_type.startswith("multipart/form-data; boundary="))
        boundary = content_type.split("boundary=", 1)[1].encode("ascii")
        self.assertTrue(boundary)
        self.assertTrue(request.data.startswith(b"--" + boundary + b"\r\n"))
        self.assertIn(b'Content-Disposition: form-data; name="chat_id"\r\n\r\n101\r\n',
                      request.data)
        document_header = (f'Content-Disposition: form-data; name="document"; '
                           f'filename="{path.name}"\r\nContent-Type: text/plain\r\n\r\n')
        self.assertIn(document_header.encode("utf-8") + content
                      + b"\r\n--" + boundary + b"--\r\n", request.data)
        self.assertEqual(request.data.count(b"--" + boundary), 3)
        self.assertNotIn(str(self.root).encode("utf-8"), request.data)
        self.assertEqual(path.read_bytes(), content)

    def test_send_message_splits_plain_text_and_redacts_token_before_splitting(self):
        text = "*Café* " + "x" * 3488 + TOKEN + "\n" + "y" * 3505
        expected = text.replace(TOKEN, "[redacted]")
        self.respond(b'{"ok": true, "result": {"message_id": 74}}')

        self.telegram.send_message(101, text)

        self.assertEqual(self.urlopen.call_count, 3)
        chunks = []
        for transport_call in self.urlopen.call_args_list:
            request = transport_call.args[0]
            self.assertEqual(request.full_url, "https://api.telegram.org/bot" + TOKEN + "/sendMessage")
            self.assertEqual(request.get_method(), "POST")
            self.assertEqual(request.get_header("Content-type"), "application/json")
            fields = json.loads(request.data.decode("utf-8"))
            self.assertEqual(set(fields), {"chat_id", "text"})
            self.assertEqual(fields["chat_id"], 101)
            self.assertLessEqual(len(fields["text"]), 3500)
            self.assertNotIn(TOKEN, fields["text"])
            chunks.append(fields["text"])
        self.assertEqual(chunks, [expected[start:start + 3500]
                                  for start in range(0, len(expected), 3500)])
        self.assertEqual("".join(chunks), expected)
        self.assertIn("*Café*", chunks[0])
        self.assertEqual(expected.count("[redacted]"), 1)

    def test_load_token_reads_quoted_env_without_environment_or_file_changes_or_output(self):
        env_path = self.root / ".env"
        other = self.root / "existing.txt"
        other.write_bytes(b"preserve this synthetic file\r\n")
        for quote in ('"', "'"):
            with self.subTest(quote=quote):
                env_path.write_bytes(("\ufeff# synthetic configuration\r\nOTHER=value\r\n"
                                      f" TELEGRAM_BOT_TOKEN = {quote}{TOKEN}{quote} \r\n")
                                     .encode("utf-8"))
                before = {path.name: path.read_bytes() for path in self.root.iterdir()}
                stdout, stderr = io.StringIO(), io.StringIO()
                with patch.dict(os.environ, {}, clear=True), \
                        redirect_stdout(stdout), redirect_stderr(stderr):
                    self.assertNotIn("TELEGRAM_BOT_TOKEN", os.environ)
                    self.assertEqual(bot.load_token(self.root), TOKEN)
                    self.assertNotIn("TELEGRAM_BOT_TOKEN", os.environ)
                self.assertEqual(stdout.getvalue(), "")
                self.assertEqual(stderr.getvalue(), "")
                self.assertEqual({path.name: path.read_bytes() for path in self.root.iterdir()}, before)
        self.urlopen.assert_not_called()

    def test_urlerror_and_httperror_do_not_expose_url_token_or_raw_error(self):
        url = "https://api.telegram.org/bot" + TOKEN + "/getUpdates"
        raw = "synthetic-transport-marker " + url
        errors = (urllib.error.URLError(raw),
                  urllib.error.HTTPError(url, 401, raw, {}, io.BytesIO(raw.encode("utf-8"))))
        for error in errors:
            with self.subTest(error_type=type(error).__name__):
                self.urlopen.reset_mock()
                self.urlopen.side_effect = error
                with self.assertRaises(bot.BotError) as caught:
                    self.telegram.get_updates()
                safe = caught.exception
                self.assertEqual(str(safe), "Telegram request failed.")
                rendered = "".join(traceback.format_exception(type(safe), safe, safe.__traceback__))
                for forbidden in (url, TOKEN, "synthetic-transport-marker"):
                    self.assertNotIn(forbidden, str(safe))
                    self.assertNotIn(forbidden, rendered)
                self.assertIsNone(safe.__cause__)
                self.assertTrue(safe.__suppress_context__)
                self.urlopen.assert_called_once()

    def test_poll_advances_offset_dispatches_messages_and_closes(self):
        stop = threading.Event()
        first = {"chat": {"id": 101}, "text": "payslip"}
        second = {"chat": {"id": 202}, "text": "review"}
        updates = [{"update_id": 9, "message": first},
                   {"update_id": 13, "edited_message": first},
                   {"update_id": 11, "message": second}]
        telegram = Mock(spec=bot.Telegram)

        def get_updates(offset):
            if telegram.get_updates.call_count == 1:
                return updates
            stop.set()
            return []

        telegram.get_updates.side_effect = get_updates
        instance = bot.Bot(telegram, repo_root=self.root)
        self.addCleanup(instance.close)
        with patch.object(instance, "submit") as submit, \
                patch.object(instance, "close", wraps=instance.close) as close:
            instance.poll(stop)
        self.assertEqual(telegram.get_updates.call_args_list, [call(0), call(14)])
        self.assertEqual(submit.call_args_list, [call(first), call(second)])
        close.assert_called_once_with()
        self.assertTrue(stop.is_set())
        self.assertTrue(instance._closed)
        self.urlopen.assert_not_called()

    def test_poll_waits_for_handled_batch_before_acknowledging_updates(self):
        from concurrent.futures import Future
        stop = threading.Event()
        pending = Future()
        received = threading.Event()
        telegram = Mock(spec=bot.Telegram)
        def updates(offset):
            if offset == 0:
                received.set()
                return [{"update_id": 1, "message": {"chat": {"id": 101}, "text": "night"}}]
            self.assertTrue(pending.done())
            stop.set()
            return []
        telegram.get_updates.side_effect = updates
        instance = bot.Bot(telegram, repo_root=self.root)
        errors = []
        def polling():
            try:
                instance.poll(stop)
            except Exception as error:
                errors.append(error)
        with patch.object(instance, "submit", return_value=pending):
            thread = threading.Thread(target=polling)
            thread.start()
            try:
                self.assertTrue(received.wait(5))
                self.assertEqual(telegram.get_updates.call_count, 1)
            finally:
                pending.set_result(None)
                thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(telegram.get_updates.call_args_list, [call(0), call(2)])

    def test_poll_errors_retry_with_mocked_event_backoff_and_close(self):
        stop = Mock(spec=threading.Event)
        stop.is_set.return_value = False
        stop.wait.side_effect = [False, True]
        telegram = Mock(spec=bot.Telegram)
        telegram.get_updates.side_effect = [bot.BotError("Synthetic poll error."),
                                            bot.BotError("Synthetic poll error.")]
        instance = bot.Bot(telegram, repo_root=self.root)
        self.addCleanup(instance.close)
        with patch.object(instance, "submit") as submit, \
                patch.object(instance, "close", wraps=instance.close) as close:
            instance.poll(stop)
        self.assertEqual(telegram.get_updates.call_args_list, [call(0), call(0)])
        self.assertEqual(stop.wait.call_args_list, [call(2), call(2)])
        self.assertEqual(stop.is_set.call_count, 2)
        submit.assert_not_called()
        close.assert_called_once_with()
        self.assertTrue(instance._closed)
        self.urlopen.assert_not_called()

    def test_default_runner_missing_does_not_affect_fixed_commands(self):
        workspace = self.root / "workspaces" / "101"
        workspace.mkdir(parents=True)
        telegram = Mock(spec=bot.Telegram)
        completed = subprocess.CompletedProcess([], 0,
                                                stdout='{"transactions": [], "review_items": []}')
        with patch.dict(sys.modules, {"app.runner": None}), \
                patch.object(bot, "run_night", wraps=bot.run_night) as runner, \
                patch("app.bot.subprocess.run", return_value=completed) as review:
            instance = bot.Bot(telegram, repo_root=self.root, today=lambda: DAY)
            self.addCleanup(instance.close)
            self.assertIs(instance.run_night, runner)
            for command in ("payslip", "review", "approve 1", "skip 1"):
                instance.handle_message({"chat": {"id": 101}, "text": command})
            runner.assert_not_called()
            self.assertEqual(telegram.send_message.call_args_list, [
                call(101, "No payslip is ready yet."),
                call(101, "No review items are listed."),
                call(101, "No numbered drafts are ready for approval."),
                call(101, "No numbered drafts are ready for approval."),
            ])
            telegram.send_document.assert_not_called()
            review.assert_called_once()
            with self.assertRaises(bot.BotError) as caught:
                instance.run_night(workspace, DAY, "Synthetic night.")
            self.assertEqual(str(caught.exception), "The runner is not available yet.")
        self.urlopen.assert_not_called()

    def test_default_runner_lazily_imports_test_only_standin(self):
        workspace = self.root / "workspaces" / "101"
        standin = ModuleType("app.runner")
        summary = {"week": "2026-W41", "payslip_day": False, "steps": [],
                   "figures": {"hourly_rate_rm": "", "take_home_rm": "", "hours_total": ""},
                   "payslip": "", "drafts": [], "review": [], "failed": {}}
        standin.run_night = Mock(return_value=summary)
        with patch.dict(sys.modules, {"app.runner": None}):
            instance = bot.Bot(Mock(spec=bot.Telegram), repo_root=self.root)
            self.addCleanup(instance.close)
            self.assertIs(instance.run_night, bot.run_night)
            standin.run_night.assert_not_called()
            with patch.dict(sys.modules, {"app.runner": standin}):
                result = instance.run_night(workspace, DAY, "Synthetic night.")
            self.assertIs(result, summary)
            standin.run_night.assert_called_once_with(workspace, DAY, "Synthetic night.")
            self.assertIsNone(sys.modules["app.runner"])
        self.urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
