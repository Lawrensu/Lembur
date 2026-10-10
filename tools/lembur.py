"""Command entry point for docs/SYSTEM_DESIGN.md sections 4 to 6."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

import business_numbers
from conventions import add_note, in_week, is_counted, iso_week, rm, text, to_sen, week_bounds
import hours as hours_tool
from plan import Plan
import reconcile as reconciliation
from schema import CATEGORIES, LEDGER_SHEETS, PLAN_SHEETS
import sheets


class CommandError(ValueError):
    def __init__(self, message, **details):
        super().__init__(message)
        self.details = details


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CommandError(message)

    def exit(self, status=0, message=None):
        raise CommandError(message or "invalid arguments")


def parser():
    root = Parser(add_help=False)
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("add-transactions", "add-bank-lines", "reconcile", "resolve",
                 "classify", "close-week", "correct-plan", "hours", "numbers",
                 "numbers-check", "review"):
        command = commands.add_parser(name, add_help=False)
        command.add_argument("--workspace", required=True, type=Path)
        if name in ("close-week", "hours", "numbers", "numbers-check", "review"):
            command.add_argument("--week", required=True)
        if name in ("add-transactions", "add-bank-lines", "hours"):
            command.add_argument("--input", required=name != "hours")
        if name in ("resolve", "classify"):
            command.add_argument("--txn-id", required=True)
            command.add_argument("--reason", required=True)
        if name == "resolve":
            command.add_argument("--bank-reference", required=True)
        if name == "classify":
            command.add_argument("--category", required=True)
        if name == "correct-plan":
            for option in ("field", "new-value", "changed-at", "reason"):
                command.add_argument("--" + option, required=True)
        if name == "hours":
            command.add_argument("--payslip-day", action="store_true")
    return root


def read_input(path):
    if path is None:
        return []
    if path == "-":
        value = json.load(sys.stdin)
    else:
        with open(path, encoding="utf-8-sig") as handle:
            value = json.load(handle)
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise CommandError("input must be a JSON array of objects")
    return value


def shape_rows(rows, columns):
    for row in rows:
        unknown = sorted(set(row) - set(columns))
        if unknown:
            raise CommandError("unknown input fields", fields=unknown)
        if any(isinstance(value, (dict, list)) for value in row.values()):
            raise CommandError("row values must be scalar")
    return [{column: text(row.get(column)) for column in columns} for row in rows]


def load_ledger(workspace):
    return sheets.load_book(workspace / "ledger", LEDGER_SHEETS, fmt="csv")


def save_ledger(workspace, ledger, *names):
    columns = {name: LEDGER_SHEETS[name] for name in names}
    sheets.save_book(workspace / "ledger", columns, ledger, fmt="csv")


def load_plan(workspace):
    book = sheets.load_book(workspace / "plan" / "plan", PLAN_SHEETS, fmt="csv")
    if len(book["assumptions"]) != 1:
        raise CommandError("plan assumptions must contain exactly one row")
    return Plan(book)


def issued(workspace, week):
    return any((workspace / "payslips" / (week + suffix)).is_file()
               for suffix in (".html", ".pdf"))


def require_open(workspace, week):
    if issued(workspace, week):
        raise CommandError("week is already issued", week=week)


def next_number(transactions):
    numbers = []
    for row in transactions:
        match = re.fullmatch(r"T(\d+)", text(row.get("txn_id")))
        if not match:
            raise CommandError("invalid stored transaction ID", txn_id=row.get("txn_id"))
        numbers.append(int(match.group(1)))
    return max(numbers, default=0)


def transaction(ledger, txn_id):
    row = next((row for row in ledger["transactions"] if row["txn_id"] == txn_id), None)
    if row is None:
        raise CommandError("transaction not found", txn_id=txn_id)
    return row


def is_late_bank_document(row, ledger):
    if row["payment_method"] != "bank_transfer":
        return False
    bank_rows = [old for old in ledger["transactions"]
                 if old["bank_reference"] and not old["source_file"]
                 and old["type"] == row["type"]]
    if row["reference"]:
        return any(old["bank_reference"] == row["reference"] for old in bank_rows)
    references = {old["bank_reference"] for old in bank_rows}
    for line in ledger["bank_lines"]:
        if line["bank_reference"] not in references:
            continue
        try:
            if reconciliation._fits(row, line):
                return True
        except (ValueError, TypeError, ArithmeticError):
            continue
    return False


def add_transactions(workspace, ledger, raw):
    for row in raw:
        forbidden = [key for key in ("txn_id", "bank_reference") if key in row]
        if forbidden:
            raise CommandError("intake cannot assign IDs or bank matches", fields=forbidden)
        if text(row.get("reconciliation_status")) not in ("", "needs_review"):
            raise CommandError("intake status must be empty or needs_review")
    rows = shape_rows(raw, LEDGER_SHEETS["transactions"])
    stored_sources = {row["source_file"] for row in ledger["transactions"]
                      if row["source_file"]}
    repeated = sorted({row["source_file"] for row in rows
                       if row["source_file"] in stored_sources})
    if repeated:
        raise CommandError("source files already in the ledger", source_files=repeated)
    number = next_number(ledger["transactions"])
    for row in rows:
        number += 1
        row["txn_id"] = "T%04d" % number
        # A late document never replaces the row already made from its bank line.
        bank_created = is_late_bank_document(row, ledger)
        try:
            closed_date = issued(workspace, iso_week(row["date"]))
        except (ValueError, TypeError):
            closed_date = False
        if (bank_created or closed_date) and row["reconciliation_status"] == "":
            row["reconciliation_status"] = "unmatched"
            add_note(row, "late document; not paired automatically")
    ledger["transactions"].extend(rows)
    save_ledger(workspace, ledger, "transactions")
    return {"transactions": rows}


def add_bank_lines(workspace, ledger, raw):
    rows = shape_rows(raw, LEDGER_SHEETS["bank_lines"])
    for row in rows:
        if row["amount_rm"]:
            row["amount_rm"] = rm(to_sen(row["amount_rm"]))
    known = {row["bank_reference"]: row for row in ledger["bank_lines"]}
    added, skipped = [], []
    conflicts = set()
    for row in rows:
        reference = row["bank_reference"]
        if not reference:
            raise CommandError("bank reference is required")
        if reference in known:
            if known[reference] == row:
                skipped.append(reference)
            else:
                conflicts.add(reference)
        else:
            known[reference] = row
            added.append(row)
    if conflicts:
        raise CommandError("bank references have different content",
                           bank_references=sorted(conflicts))
    if added:
        ledger["bank_lines"].extend(added)
        save_ledger(workspace, ledger, "bank_lines")
    return {"bank_lines": added, "skipped": skipped}


def classification_problem(row):
    category, kind = row["category"], row["type"]
    return category not in CATEGORIES or kind not in ("income", "expense") \
        or (category == "sales") != (kind == "income")


def classify(workspace, ledger, args):
    row = transaction(ledger, args.txn_id)
    if not is_counted(row) or not classification_problem(row):
        raise CommandError("row is not blocked by the classification gate", txn_id=args.txn_id)
    if args.category not in CATEGORIES or row["type"] not in ("income", "expense") \
            or (args.category == "sales") != (row["type"] == "income"):
        raise CommandError("new category must be known and agree with type", txn_id=args.txn_id)
    if not text(args.reason):
        raise CommandError("a reason is required")
    row["category"] = args.category
    add_note(row, text(args.reason))
    save_ledger(workspace, ledger, "transactions")
    return {"transaction": row}


def append_warnings(workspace, week, warnings):
    if not warnings:
        return
    path = workspace / "audit" / week / "review_items.md"
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    existing = content.splitlines()
    seen = set(existing)
    added = []
    for warning in warnings:
        line = "* " + str(warning).replace("\r", " ").replace("\n", " ")
        if line not in seen:
            seen.add(line)
            added.append(line)
    if added:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            if content and not content.endswith("\n"):
                handle.write("\n")
            handle.write("\n".join(added) + "\n")


def compute(ledger, plan, week):
    try:
        return business_numbers.compute(ledger["transactions"], ledger["hours"], plan, week)
    except ValueError as exc:
        blocked = [row["txn_id"] for row in ledger["transactions"]
                   if is_counted(row) and classification_problem(row)]
        if blocked:
            raise CommandError(str(exc), txn_ids=blocked) from None
        raise


def run(args):
    workspace = args.workspace
    if hasattr(args, "week"):
        if not re.fullmatch(r"\d{4}-W\d{2}", args.week):
            raise CommandError("week must be YYYY-Www")
        week_bounds(args.week)
    if args.command in ("hours", "numbers", "close-week"):
        require_open(workspace, args.week)
    ledger = load_ledger(workspace)
    if args.command == "add-transactions":
        return add_transactions(workspace, ledger, read_input(args.input))
    if args.command == "add-bank-lines":
        return add_bank_lines(workspace, ledger, read_input(args.input))
    if args.command == "reconcile":
        # Keep late documents for review, including when their bank row came first.
        late = [row for row in ledger["transactions"]
                if row["reconciliation_status"] == "unmatched"
                and "late document; not paired automatically" in row["notes"]]
        rows = [row for row in ledger["transactions"] if row not in late]
        ambiguous = reconciliation.reconcile(rows, ledger["bank_lines"])
        for item in ambiguous:
            item["candidates"] = [line for line in ledger["bank_lines"]
                                  if line["bank_reference"] in item["candidates"]]
        save_ledger(workspace, ledger, "transactions")
        return {"ambiguous": ambiguous}
    if args.command == "resolve":
        transaction(ledger, args.txn_id)
        row = reconciliation.resolve(ledger["transactions"], ledger["bank_lines"],
                                     args.txn_id, args.bank_reference, text(args.reason))
        save_ledger(workspace, ledger, "transactions")
        return {"transaction": row}
    if args.command == "classify":
        return classify(workspace, ledger, args)
    if args.command == "close-week":
        lines = [line for line in ledger["bank_lines"] if in_week(line["date"], args.week)]
        # Unsettled rows from a different week do not prevent closing this one.
        rows = [row for row in ledger["transactions"] if in_week(row["date"], args.week)]
        waiting = [row["txn_id"] for row in rows if not row["reconciliation_status"]]
        if waiting:
            raise CommandError("rows still without a status", txn_ids=waiting)
        if not lines:
            return {"transactions": []}
        # Include all stored rows to reserve IDs and already used bank references.
        # The underlying close function also checks status; other week pending rows
        # get temporary status copies, never a change in the ledger.
        copied = [dict(row) for row in ledger["transactions"]]
        for row in copied:
            if not in_week(row["date"], args.week) and not row["reconciliation_status"]:
                row["reconciliation_status"] = "unmatched"
        created = reconciliation.close_week(copied, lines)
        ledger["transactions"].extend(created)
        save_ledger(workspace, ledger, "transactions")
        return {"transactions": created}
    if args.command == "correct-plan":
        if not text(args.reason):
            raise CommandError("a reason is required")
        plan = load_plan(workspace)
        entry = plan.correct(args.field, args.new_value, args.changed_at, text(args.reason))
        sheets.save_book(workspace / "plan" / "plan", PLAN_SHEETS, plan.book, fmt="csv")
        return {"correction": entry}
    if args.command == "hours":
        events = read_input(args.input)
        allowed = {"date", "start", "end", "stated_hours", "message_date", "minutes"}
        for event in events:
            unknown = sorted(set(event) - allowed)
            if unknown:
                raise CommandError("unknown event fields", fields=unknown)
        lines, warnings = hours_tool.build_hours(
            ledger["transactions"], ledger["hours"], load_plan(workspace), args.week,
            events=events, payslip_day=args.payslip_day)
        ledger["hours"] = lines
        save_ledger(workspace, ledger, "hours")
        append_warnings(workspace, args.week, warnings)
        return {"hours": [line for line in lines if in_week(line["date"], args.week)],
                "warnings": warnings}
    if args.command in ("numbers", "numbers-check"):
        result = compute(ledger, load_plan(workspace), args.week)
        path = workspace / "audit" / args.week / "numbers.json"
        if args.command == "numbers-check":
            with path.open(encoding="utf-8") as handle:
                saved = json.load(handle)
            if not isinstance(saved, dict):
                raise CommandError("saved numbers must be an object")
            keys = sorted(set(saved) | set(result))
            differing = [key for key in keys
                         if key not in saved or key not in result
                         or json.dumps(saved[key], sort_keys=True) != json.dumps(result[key], sort_keys=True)]
            return {"equal": not differing, "differing_keys": differing}
        append_warnings(workspace, args.week, result["warnings"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result
    if args.command == "review":
        path = workspace / "audit" / args.week / "review_items.md"
        items = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
        rows = [row for row in reconciliation.review_list(ledger["transactions"])
                if in_week(row["date"], args.week)]
        return {"transactions": rows, "review_items": items}
    raise CommandError("unknown command")


def main(argv=None):
    try:
        args = parser().parse_args(argv)
        result = run(args)
        code = 1 if args.command == "numbers-check" and not result["equal"] else 0
    except Exception as exc:
        result = {"error": str(exc) or type(exc).__name__}
        if isinstance(exc, CommandError):
            result.update(exc.details)
        code = 1
    print(json.dumps(result, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
