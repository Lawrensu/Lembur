"""The tool layer: docs/SYSTEM_DESIGN.md, Runtime and How an agent acts.

run_tool is the only way an agent acts. It runs one tool for one agent, checks
that the agent is allowed to use it, keeps every path inside the student's
workspace, and returns a dict that always carries ok. A mistake by an agent
comes back as ok false and never raises.

This module loads from its file path with no key and no network. It reaches
for app/model.py only when ask is left out and an image has to be read.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
ENTRY_POINT = ROOT / "tools" / "lembur.py"

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff"}

READ_ONLY_DOCUMENT_FOLDERS = ("inbox", "receipts")

# write_file refuses these, so they change only through the lembur command.
PROTECTED_NAMES = {
    "ledger_transactions.csv",
    "ledger_bank_lines.csv",
    "ledger_hours.csv",
    "plan_products.csv",
    "plan_channels.csv",
    "plan_assumptions.csv",
    "plan_change_log.csv",
    "numbers.json",
}
PROTECTED_FOLDER = "payslips"
PROTECTED_SUFFIXES = (".html", ".pdf")

AGENT_TOOLS = {
    "bookkeeper": {"read_document", "list_files", "read_file", "write_file",
                   "move_file", "calendar"},
    "payroll": {"list_files", "read_file", "write_file", "calendar"},
    "growth_coach": {"list_files", "read_file", "write_file"},
    "auditor": {"list_files", "read_file", "write_file"},
}

AGENT_COMMANDS = {
    "bookkeeper": {"add-transactions", "add-bank-lines", "reconcile", "resolve",
                   "classify", "close-week", "review"},
    "payroll": {"correct-plan", "hours", "numbers", "review", "payslip"},
    "growth_coach": {"review"},
    "auditor": {"numbers-check", "review"},
}

IMAGE_PROMPT = ("Read this document. Return everything printed on it as plain "
                "text. Do not guess a value you cannot read.")


class Refused(ValueError):
    """A mistake by an agent. Returned as ok false, never raised."""


def text(value) -> str:
    return "" if value is None else str(value).strip()


def root_of(workspace) -> Path:
    if workspace is None or text(workspace) == "":
        raise Refused("workspace is required")
    return Path(workspace).resolve()


def inside(root: Path, value) -> Path:
    """A path that must stay inside the workspace."""
    name = text(value)
    if not name:
        raise Refused("a path is required")
    candidate = Path(name)
    if candidate.is_absolute():
        raise Refused("path must be relative to the workspace: " + name)
    target = (root / candidate).resolve()
    if target != root and root not in target.parents:
        raise Refused("path leaves the workspace: " + name)
    return target


def _csv_rows(path: Path) -> list:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _default_ask():
    """app/model.py, reached for only when an image has to be read."""
    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))
    import model
    return model.ask


def _lembur(root: Path, args: dict) -> dict:
    command = text(args.get("command"))
    if not command:
        raise Refused("lembur needs a command")

    options = args.get("options")
    if options is None:
        options = {}
    if not isinstance(options, dict):
        raise Refused("options must be an object")

    has_input = args.get("input") is not None
    has_input_file = bool(text(args.get("input_file")))
    if has_input and has_input_file:
        raise Refused("give input or input_file, not both")

    rows = None
    if has_input:
        rows = args["input"]
        # payslip reads one object; every other command reads an array of rows
        if not isinstance(rows, (list, dict)):
            raise Refused("input must be a JSON array or object")
    elif has_input_file:
        source = inside(root, args["input_file"])
        if not source.is_file():
            raise Refused("no such input file: " + text(args["input_file"]))
        rows = _csv_rows(source)

    argv = [sys.executable, "-B", str(ENTRY_POINT), command,
            "--workspace", str(root)]
    for key, value in options.items():
        if value is None or value is False:
            continue
        name = str(key).lstrip("-")
        # the tool layer alone decides the workspace and the input file
        if name in ("workspace", "input"):
            raise Refused("options may not set " + name)
        flag = "--" + name
        if value is True:
            argv.append(flag)
        else:
            argv.extend([flag, str(value)])

    handle = None
    if rows is not None:
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8", newline="\n")
        json.dump(rows, handle, ensure_ascii=False)
        handle.close()
        argv.extend(["--input", handle.name])
    try:
        done = subprocess.run(argv, cwd=str(ROOT), text=True, capture_output=True)
    finally:
        if handle is not None:
            os.unlink(handle.name)

    printed = done.stdout.strip()
    try:
        result = json.loads(printed)
    except ValueError:
        result = None
    if not isinstance(result, dict):
        result = {"error": printed or done.stderr.strip() or "the command printed no JSON"}

    ok = done.returncode == 0
    answer = {"ok": ok, "result": result}
    if not ok:
        message = text(result.get("error")) or done.stderr.strip() or "the command failed"
        answer["error"] = message
    return answer


def _read_document(root: Path, args: dict, ask) -> dict:
    target = inside(root, args.get("path"))
    relative = target.relative_to(root)
    folder = relative.parts[0] if relative.parts else ""
    if folder not in READ_ONLY_DOCUMENT_FOLDERS:
        raise Refused("read_document reads only " + " or ".join(READ_ONLY_DOCUMENT_FOLDERS))
    if not target.is_file():
        raise Refused("no such file: " + text(args.get("path")))
    if target.suffix.lower() in IMAGE_SUFFIXES:
        reader = ask if ask is not None else _default_ask()
        messages = [{"role": "user", "content": IMAGE_PROMPT}]
        return {"ok": True, "text": reader("read", messages, images=[str(target)])}
    return {"ok": True, "text": target.read_text(encoding="utf-8", errors="replace")}


def _list_files(root: Path, args: dict) -> dict:
    folder = inside(root, args.get("folder"))
    if not folder.is_dir():
        raise Refused("no such folder: " + text(args.get("folder")))
    names = sorted(item.name for item in folder.iterdir() if item.is_file())
    return {"ok": True, "files": names}


def _read_file(root: Path, args: dict) -> dict:
    target = inside(root, args.get("path"))
    if not target.is_file():
        raise Refused("no such file: " + text(args.get("path")))
    return {"ok": True, "text": target.read_text(encoding="utf-8", errors="replace")}


def _write_file(root: Path, args: dict) -> dict:
    target = inside(root, args.get("path"))
    relative = target.relative_to(root)
    if target.name in PROTECTED_NAMES:
        raise Refused(target.name + " changes only through the lembur command")
    if PROTECTED_FOLDER in relative.parts and target.suffix.lower() in PROTECTED_SUFFIXES:
        raise Refused("the payslip changes only through the lembur command")
    body = args.get("text")
    if body is None:
        raise Refused("write_file needs text")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a" if args.get("append") else "w", encoding="utf-8", newline="\n") as out:
        out.write(str(body))
    return {"ok": True}


def _move_file(root: Path, args: dict) -> dict:
    source = inside(root, args.get("from"))
    target = inside(root, args.get("to"))
    if not source.is_file():
        raise Refused("no such file: " + text(args.get("from")))
    target.parent.mkdir(parents=True, exist_ok=True)
    source.replace(target)
    return {"ok": True}


def _calendar(args: dict) -> dict:
    written = text(args.get("date"))
    try:
        day = dt.date.fromisoformat(written)
    except ValueError:
        raise Refused("date must be written YYYY-MM-DD: " + (written or "(empty)"))
    monday = day - dt.timedelta(days=day.weekday())
    sunday = monday + dt.timedelta(days=6)
    year, week, _ = day.isocalendar()
    return {"ok": True, "week": "%d-W%02d" % (year, week),
            "week_start": monday.isoformat(), "payslip_day": sunday.isoformat(),
            "is_payslip_day": day == sunday}


def _act(workspace, agent, name, args, ask) -> dict:
    agent, name = text(agent), text(name)
    if agent not in AGENT_TOOLS:
        raise Refused("unknown agent: " + (agent or "(empty)"))
    if not isinstance(args, dict):
        raise Refused("args must be an object")
    if name == "lembur":
        command = text(args.get("command"))
        if command not in AGENT_COMMANDS[agent]:
            raise Refused("the %s may not run %s" % (agent, command or "a command"))
    elif name not in AGENT_TOOLS[agent]:
        raise Refused("the %s may not use %s" % (agent, name or "a tool"))

    root = root_of(workspace)
    if name == "lembur":
        return _lembur(root, args)
    if name == "read_document":
        return _read_document(root, args, ask)
    if name == "list_files":
        return _list_files(root, args)
    if name == "read_file":
        return _read_file(root, args)
    if name == "write_file":
        return _write_file(root, args)
    if name == "move_file":
        return _move_file(root, args)
    if name == "calendar":
        return _calendar(args)
    raise Refused("unknown tool: " + (name or "(empty)"))


def run_tool(workspace, agent, name, args, ask=None) -> dict:
    """Run one tool for one agent. Always returns a dict with ok."""
    try:
        return _act(workspace, agent, name, args, ask)
    except Refused as exc:
        return {"ok": False, "error": str(exc)}
    except Exception as exc:  # a tool error is data, never a crash
        reason = str(exc).strip() or type(exc).__name__
        return {"ok": False, "error": reason}
