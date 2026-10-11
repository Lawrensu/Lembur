"""Telegram front door for the package 3 contract in SYSTEM_DESIGN section 6.5."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
import threading
import urllib.error
import urllib.parse
import urllib.request
import uuid


ROOT = Path(__file__).resolve().parents[1]
MALAYSIA = timezone(timedelta(hours=8))
PLAN_FILES = ("plan_products.csv", "plan_channels.csv", "plan_assumptions.csv",
              "plan_change_log.csv")
WEEK = re.compile(r"\d{4}-W\d{2}\Z")
DRAFT = re.compile(r"(\d+)_.*\.md\Z")
WELCOME = (
    "Hi, I am Lembur, your back office team. You sleep, we do the overtime.",
    "Before bed, send me today's receipts, order screenshots or your bank statement as files. "
    "Then send one message about your day, for example what you sold and any hours you worked at an event.",
    "I record everything, work out what you earned per hour, and on Sunday I send your payslip "
    "with drafts of changes that could earn you more.",
    "Words I understand: payslip, review, approve N, skip N, help. Anything else I treat as tonight's message.",
)
GREETINGS = {"/start", "/help", "help", "hi", "hello", "hey", "start"}
STARTING = "Got it. The night shift is starting. This usually takes under a minute, and longer on payslip day."
FAILURE = "I could not finish that request. Nothing was guessed. Please try again or ask the team to check the run."


class BotError(Exception):
    """A safe error which never carries a credential or remote response."""


def malaysia_today():
    return datetime.now(MALAYSIA).date().isoformat()


def load_token(repo_root=ROOT):
    """Read only Telegram configuration; do not overwrite another package's env."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        path = Path(repo_root) / ".env"
        if path.is_file():
            for line in path.read_text(encoding="utf-8-sig").splitlines():
                key, separator, value = line.strip().partition("=")
                if separator and key.strip() == "TELEGRAM_BOT_TOKEN":
                    token = value.strip().strip("\"'")
                    break
    if not token or not re.fullmatch(r"\d+:[A-Za-z0-9_-]+", token):
        raise BotError("Set TELEGRAM_BOT_TOKEN in the local .env file before starting.")
    return token


class Telegram:
    """Standard library HTTPS calls. Never expose token-bearing request errors."""

    def __init__(self, token):
        if not re.fullmatch(r"\d+:[A-Za-z0-9_-]+", token):
            raise BotError("Invalid Telegram token configuration.")
        self._token = token

    def _request(self, request, timeout=40):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (OSError, ValueError) as exc:
            raise BotError("Telegram request failed.") from None

    def _call(self, method, fields=None, body=None, content_type=None):
        if body is None:
            body = json.dumps(fields or {}, ensure_ascii=True).encode("utf-8")
            content_type = "application/json"
        request = urllib.request.Request(
            "https://api.telegram.org/bot" + self._token + "/" + method,
            data=body, headers={"Content-Type": content_type}, method="POST")
        try:
            result = json.loads(self._request(request))
            if not isinstance(result, dict) or result.get("ok") is not True:
                raise BotError("Telegram did not accept the request.")
            return result["result"]
        except (ValueError, KeyError, TypeError):
            raise BotError("Telegram returned an unreadable response.") from None

    def get_updates(self, offset=0):
        result = self._call("getUpdates", {"offset": offset, "timeout": 25,
                                           "allowed_updates": ["message"]})
        if not isinstance(result, list):
            raise BotError("Telegram returned unreadable updates.")
        return result

    def get_file(self, file_id):
        return self._call("getFile", {"file_id": file_id})

    def download_file(self, file_path):
        if not isinstance(file_path, str) or not file_path or any(
                part in ("", ".", "..") for part in file_path.split("/")) \
                or ":" in file_path or "\\" in file_path:
            raise BotError("Telegram file path is invalid.")
        request = urllib.request.Request(
            "https://api.telegram.org/file/bot" + self._token + "/"
            + urllib.parse.quote(file_path, safe="/"))
        return self._request(request)

    def send_message(self, chat_id, text):
        # Plain text, without parse_mode. Splitting is not business arithmetic.
        text = text.replace(self._token, "[redacted]")
        for start in range(0, len(text), 3500):
            self._call("sendMessage", {"chat_id": chat_id, "text": text[start:start + 3500]})

    def send_document(self, chat_id, path):
        path = Path(path)
        boundary = "lembur_" + uuid.uuid4().hex
        filename = path.name.replace('"', "_").replace("\r", "_").replace("\n", "_")
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        body = (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{chat_id}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"document\"; filename=\"{filename}\"\r\n"
            f"Content-Type: {mime}\r\n\r\n"
        ).encode("utf-8") + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode("ascii")
        self._call("sendDocument", body=body, content_type="multipart/form-data; boundary=" + boundary)


def run_night(workspace, date, message):
    """Import the actual orchestration package only when a night is requested."""
    if str(ROOT) not in sys.path:  # started as "python app/bot.py": make the app package findable
        sys.path.insert(0, str(ROOT))
    try:
        from app.runner import run_night as runner
    except ModuleNotFoundError:
        raise BotError("The runner is not available yet.") from None
    return runner(workspace, date, message)


class Bot:
    def __init__(self, telegram, run_night=None, repo_root=ROOT, today=None):
        self.telegram = telegram
        self.run_night = run_night or globals()["run_night"]
        self.root = Path(repo_root).resolve()
        self.today = today or malaysia_today
        self._workers = {}
        self._chat_locks = {}
        self._guard = threading.Lock()
        self._closed = False

    @staticmethod
    def _chat_id(chat_id):
        if isinstance(chat_id, bool) or not isinstance(chat_id, int):
            raise BotError("Invalid chat.")
        return chat_id

    def _lock(self, chat_id):
        with self._guard:
            return self._chat_locks.setdefault(chat_id, threading.RLock())

    def _safe_path(self, workspace, value):
        workspace = Path(workspace)
        path = Path(value)
        if not path.is_absolute():
            path = workspace / path
        if not path.resolve().is_relative_to(workspace.resolve()):
            raise BotError("The requested path leaves this chat's workspace.")
        # Symlinks inside a workspace can alias another chat or protected file.
        current = path
        while current != workspace and current != current.parent:
            if current.is_symlink() or current.is_junction():
                raise BotError("Symlink paths are not supported.")
            current = current.parent
        return path

    def _workspace(self, chat_id):
        chat_id = self._chat_id(chat_id)
        base = self.root / "workspaces"
        workspace = base / str(chat_id)
        if base.is_symlink() or base.is_junction() or workspace.is_symlink() or workspace.is_junction() \
                or not workspace.resolve().is_relative_to(base.resolve()):
            raise BotError("Unsafe chat workspace.")
        new = not workspace.exists()
        if new:
            sources = [self.root / "data" / "demo" / filename for filename in PLAN_FILES]
            if not all(source.is_file() for source in sources):
                raise BotError("The baseline plan is not available.")
            base.mkdir(exist_ok=True)
            with tempfile.TemporaryDirectory(prefix=".new-chat-", dir=base) as temporary:
                staged = Path(temporary) / str(chat_id)
                staged.mkdir()
                for folder in ("inbox", "plan", "receipts", "boardroom", "audit", "payslips", "approvals"):
                    (staged / folder).mkdir()
                for source in sources:
                    shutil.copyfile(source, staged / "plan" / source.name)
                staged.rename(workspace)
        return workspace

    def _weeks(self, workspace, folder):
        base = self._safe_path(workspace, folder)
        if not base.exists():
            return []
        result = []
        for path in base.iterdir():
            if WEEK.fullmatch(path.name):
                checked = self._safe_path(workspace, path)
                if checked.is_dir():
                    result.append(checked)
        return sorted(result, key=lambda path: path.name, reverse=True)

    def _save_upload(self, workspace, message):
        if "document" in message:
            upload = message["document"]
            if not isinstance(upload, dict):
                raise BotError("Invalid document.")
            original = upload.get("file_name")
            kind, extension = "file", ""
        else:
            variants = message.get("photo")
            if not isinstance(variants, list) or not variants or not all(isinstance(p, dict) for p in variants):
                raise BotError("Invalid photo.")
            upload = max(variants, key=lambda p: (p.get("width", 0) * p.get("height", 0), p.get("file_size", 0)))
            original = None
            kind, extension = "photo", ".jpg"
        file_id = upload.get("file_id")
        if not isinstance(file_id, str) or not file_id:
            raise BotError("Missing file identifier.")
        if original is not None:
            if not isinstance(original, str):
                raise BotError("Invalid file name.")
            filename = re.split(r"[/\\]", original)[-1]
            filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", filename).rstrip(" .")
            if not filename:
                raise BotError("Invalid file name.")
            if re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", filename):
                filename = "_" + filename
        else:
            received = datetime.fromtimestamp(message["date"], MALAYSIA)
            filename = kind + "_" + received.strftime("%Y%m%d_%H%M%S") + "_" + str(message["message_id"]) + extension
        inbox = self._safe_path(workspace, "inbox")
        inbox.mkdir(exist_ok=True)
        destination = self._safe_path(workspace, inbox / filename)
        metadata = self.telegram.get_file(file_id)
        remote = metadata.get("file_path")
        if not isinstance(remote, str) or not remote:
            raise BotError("The upload is unavailable.")
        content = self.telegram.download_file(remote)
        if not isinstance(content, bytes):
            raise BotError("The upload is unreadable.")
        stem, suffix = destination.stem, destination.suffix
        number = 1
        while True:
            try:
                with destination.open("xb") as handle:
                    handle.write(content)
                return destination
            except FileExistsError:
                number += 1
                destination = self._safe_path(workspace, inbox / (stem + "_" + str(number) + suffix))

    def _latest_payslip(self, workspace):
        folder = self._safe_path(workspace, "payslips")
        candidates = []
        if folder.exists():
            for path in folder.iterdir():
                if path.suffix in (".html", ".pdf") and WEEK.fullmatch(path.stem):
                    checked = self._safe_path(workspace, path)
                    if checked.is_file():
                        candidates.append(checked)
        return max(candidates, key=lambda p: (p.stem, p.suffix == ".pdf"), default=None)

    def _payslip(self, chat_id, workspace):
        path = self._latest_payslip(workspace)
        if path is None:
            self.telegram.send_message(chat_id, "No payslip is ready yet.")
            return
        numbers_path = self._safe_path(workspace, "audit/" + path.stem + "/numbers.json")
        numbers = json.loads(numbers_path.read_text(encoding="utf-8")) if numbers_path.is_file() else {}
        rate = numbers.get("hourly_rate_rm")
        reply = "Your latest payslip: " + path.name
        if isinstance(rate, str) and rate:
            reply += "\nHourly rate: RM " + rate + " per hour."
        self.telegram.send_document(chat_id, path)
        self.telegram.send_message(chat_id, reply)

    def _review(self, chat_id, workspace):
        weeks = self._weeks(workspace, "audit")
        if weeks:
            week = weeks[0].name
        else:
            year, number, _ = datetime.fromisoformat(self.today()).isocalendar()
            week = "%04d-W%02d" % (year, number)
        # The review command is read-only; no runner or model is involved.
        for name in ("ledger_transactions.csv", "ledger_bank_lines.csv", "ledger_hours.csv",
                     "audit/" + week + "/review_items.md"):
            self._safe_path(workspace, name)
        result = subprocess.run([sys.executable, "-B", str(self.root / "tools" / "lembur.py"),
                                 "review", "--workspace", str(workspace), "--week", week],
                                cwd=self.root, capture_output=True, text=True,
                                encoding="utf-8", timeout=30)
        if result.returncode:
            raise BotError("The review list is unavailable.")
        review = json.loads(result.stdout)
        lines = []
        for row in review["transactions"]:
            amount = row.get("amount_rm")
            parts = [row["txn_id"], row.get("date", ""), row["reconciliation_status"],
                     "RM " + amount if amount else "Unknown amount", row.get("description", ""), row.get("notes", "")]
            lines.append(" | ".join(part for part in parts if part))
        lines.extend(review["review_items"])
        self.telegram.send_message(chat_id, "Needs your review:\n" + "\n".join(lines) if lines else "No review items are listed.")

    def _approval(self, chat_id, workspace, command, number):
        for folder in self._weeks(workspace, "approvals"):
            approved = self._safe_path(workspace, folder / "approved")
            pending = [self._safe_path(workspace, p) for p in folder.iterdir()
                       if DRAFT.fullmatch(p.name) and p.is_file()]
            previous = [self._safe_path(workspace, p) for p in approved.iterdir()
                        if DRAFT.fullmatch(p.name) and p.is_file()] if approved.exists() else []
            if not pending and not previous:
                continue
            selected = [p for p in pending if int(DRAFT.fullmatch(p.name)[1]) == number]
            if len(selected) != 1:
                self.telegram.send_message(chat_id, "That draft number is not uniquely pending in your latest draft week.")
                return
            path = selected[0]
            if command == "skip":
                self.telegram.send_message(chat_id, "Draft " + str(number) + " is still waiting for approval. Nothing was sent.")
                return
            destination = self._safe_path(workspace, approved / path.name)
            if destination.exists():
                self.telegram.send_message(chat_id, "An approved copy already exists. The pending draft was left unchanged.")
                return
            approved.mkdir(exist_ok=True)
            path.rename(destination)
            self.telegram.send_message(chat_id, "Draft " + str(number) + " is approved and ready for you to send. Nothing was sent by the bot.")
            return
        self.telegram.send_message(chat_id, "No numbered drafts are ready for approval.")

    def _report_night(self, chat_id, workspace, summary):
        required = {"week", "payslip_day", "steps", "figures", "payslip", "drafts", "review", "failed"}
        if not isinstance(summary, dict) or not required.issubset(summary):
            raise BotError("The runner returned an incomplete summary.")
        figures = summary["figures"]
        if not isinstance(figures, dict) or not all(isinstance(figures.get(key), str) for key in
                ("hourly_rate_rm", "take_home_rm", "hours_total")):
            raise BotError("The runner returned invalid figures.")
        if summary["failed"] or any(step.get("status") == "failed" for step in summary["steps"]):
            failed = summary["failed"] or {}
            reason = failed.get("reason")
            self.telegram.send_message(chat_id, "The night stopped before completion. " +
                                       (reason if isinstance(reason, str) and reason else "Please check the review list."))
            return
        payslip = self._safe_path(workspace, summary["payslip"]) if summary["payslip"] else None
        if payslip is not None and not payslip.is_file():
            raise BotError("The reported payslip does not exist.")
        drafts = [(item["number"], self._safe_path(workspace, item["file"])) for item in summary["drafts"]]
        if any(not path.is_file() for _, path in drafts):
            raise BotError("A reported draft does not exist.")
        heading = "Your board meeting is ready." if summary["payslip_day"] and payslip else "Your figures are partial for this week."
        lines = [heading]
        for key, label, unit in (("hourly_rate_rm", "Hourly rate: RM ", " per hour"),
                                 ("take_home_rm", "Take home: RM ", ""),
                                 ("hours_total", "Working time: ", " hours")):
            if figures[key]:
                lines.append(label + figures[key] + unit)
        if payslip:
            lines.append("Payslip: " + payslip.name)
        if drafts:
            lines.append("Drafts waiting for individual approval:")
            lines.extend(str(number) + ": " + path.name for number, path in drafts)
            lines.append("Reply approve N or skip N. You send approved drafts yourself.")
        if summary["review"]:
            lines.append("Needs your review:")
            lines.extend(summary["review"])
        if payslip:
            self.telegram.send_document(chat_id, payslip)
        self.telegram.send_message(chat_id, "\n".join(lines))

    def handle_message(self, message):
        chat_id = self._chat_id(message["chat"]["id"])
        with self._lock(chat_id):
            try:
                workspace = self._workspace(chat_id)
                has_upload = "document" in message or "photo" in message
                if has_upload:
                    saved = self._save_upload(workspace, message)
                    self.telegram.send_message(chat_id, "Saved " + saved.name + " to your inbox.")
                    text = message.get("caption", "")
                else:
                    text = message.get("text", "")
                if not isinstance(text, str) or not text.strip():
                    return
                command = text.strip()
                # A short ask that names a fixed word means that word: "show me my payslip".
                words = re.findall(r"[a-z]+", command.lower())
                if len(words) <= 8 and not re.search(r"[0-9]", command):
                    if "payslip" in words:
                        command = "payslip"
                    elif "review" in words:
                        command = "review"
                if command.lower().rstrip("!. ") in GREETINGS:
                    self.telegram.send_message(chat_id, "\n\n".join(WELCOME))
                elif command == "payslip":
                    self._payslip(chat_id, workspace)
                elif command == "review":
                    self._review(chat_id, workspace)
                elif match := re.fullmatch(r"(approve|skip) ([0-9]+)", command):
                    self._approval(chat_id, workspace, match[1], int(match[2]))
                else:
                    self.telegram.send_message(chat_id, STARTING)
                    summary = self.run_night(workspace, self.today(), text)
                    self._report_night(chat_id, workspace, summary)
            except Exception as error:
                # Never send raw exceptions: HTTPS exceptions can embed the token.
                # The local console gets where it failed, without the exception's own text.
                where = traceback.extract_tb(error.__traceback__)[-1]
                detail = str(error) if isinstance(error, BotError) else ""
                print("Lembur bot: %s at %s line %s. %s" % (type(error).__name__, Path(where.filename).name,
                                                            where.lineno, detail), file=sys.stderr, flush=True)
                try:
                    self.telegram.send_message(chat_id, FAILURE)
                except Exception:
                    pass

    def submit(self, message):
        chat_id = self._chat_id(message["chat"]["id"])
        with self._guard:
            if self._closed:
                raise RuntimeError("The bot is closed.")
            if chat_id not in self._workers:
                self._workers[chat_id] = ThreadPoolExecutor(max_workers=1)
            return self._workers[chat_id].submit(self.handle_message, message)

    def close(self):
        with self._guard:
            self._closed = True
            workers = list(self._workers.values())
        for worker in workers:
            worker.shutdown(wait=True)

    def poll(self, stop=None):
        stop = stop or threading.Event()
        offset = 0
        try:
            while not stop.is_set():
                try:
                    updates = self.telegram.get_updates(offset)
                except BotError:
                    if stop.wait(2):
                        break
                    continue
                pending = []
                next_offset = offset
                for update in updates:
                    if "message" in update:
                        pending.append(self.submit(update["message"]))
                    next_offset = max(next_offset, update["update_id"] + 1)
                # Acknowledge only after this batch is handled, not while queued.
                for future in pending:
                    future.result()
                offset = next_offset
        finally:
            self.close()


def main():
    try:
        bot = Bot(Telegram(load_token()))
        bot.poll()
    except KeyboardInterrupt:
        return 0
    except Exception:
        print("The bot could not start. Check local configuration and connectivity; credentials were not logged.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
