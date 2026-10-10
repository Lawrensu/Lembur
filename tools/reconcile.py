"""Reconciliation tool: docs/SYSTEM_DESIGN.md section 4.1."""

from __future__ import annotations

from collections import Counter

from conventions import add_note, is_empty, rm, text, to_date, to_sen
from schema import CATEGORIES, PAYMENT_METHODS

REQUIRED = ["date", "type", "category", "amount_rm", "payment_method"]
SALES_REQUIRED = ["product_id", "quantity", "channel"]
DUPLICATE_KEY = ["date", "type", "amount_rm", "counterparty", "reference"]


def _status(row: dict) -> str:
    return text(row.get("reconciliation_status"))


def _txn_number(row: dict) -> int:
    return int(text(row["txn_id"])[1:])


def _intake_problem(row: dict):
    missing = [c for c in REQUIRED if is_empty(row.get(c))]
    if text(row.get("category")) == "sales":
        missing += [c for c in SALES_REQUIRED if is_empty(row.get(c))]
    if missing:
        return "missing " + ", ".join(missing)
    category, kind = text(row["category"]), text(row["type"])
    if category not in CATEGORIES:
        return "unknown category %s" % category
    if kind not in ("income", "expense") or (category == "sales") != (kind == "income"):
        return "category and type disagree"
    if text(row["payment_method"]) not in PAYMENT_METHODS:
        return "unknown payment method %s" % text(row["payment_method"])
    return None


def _duplicate_key(row: dict):
    return (
        to_date(row["date"]), text(row["type"]), to_sen(row["amount_rm"]),
        text(row.get("counterparty")), text(row.get("reference")),
    )


def _fits(row: dict, line: dict) -> bool:
    """Same type, same amount, dated within one day either side."""
    return (
        text(line["type"]) == text(row["type"])
        and to_sen(line["amount_rm"]) == to_sen(row["amount_rm"])
        and abs((to_date(line["date"]) - to_date(row["date"])).days) <= 1
    )


def _used_references(transactions: list) -> set:
    return {text(r.get("bank_reference")) for r in transactions} - {""}


def reconcile(transactions: list, bank_lines: list) -> list:
    """Steps 1 to 5. Sets a status on each row it can settle.

    Returns the ambiguous rows for the Bookkeeper, each with its candidate
    bank references. Their status stays empty until resolve() is called.
    """
    rows = sorted(transactions, key=_txn_number)
    lines = {text(line["bank_reference"]): line for line in bank_lines}
    used = _used_references(rows)
    seen = {}
    pending = []

    for row in rows:
        status = _status(row)
        testable = status == "" or (
            status == "unmatched" and is_empty(row.get("bank_reference"))
        )
        if status == "":
            problem = _intake_problem(row)
            if problem:
                row["reconciliation_status"] = "needs_review"
                add_note(row, problem)
                continue
            if text(row["payment_method"]) == "cash":
                row["reconciliation_status"] = "cash_declared"
                continue
        is_cash = text(row.get("payment_method")) == "cash"
        if is_cash or is_empty(row.get("date")) or is_empty(row.get("amount_rm")):
            continue

        key = _duplicate_key(row)
        if not testable:
            seen.setdefault(key, text(row["txn_id"]))
            continue
        if key in seen:
            row["reconciliation_status"] = "duplicate"
            add_note(row, "duplicate of %s" % seen[key])
            continue
        seen[key] = text(row["txn_id"])

        reference = text(row.get("reference"))
        line = lines.get(reference)
        if reference and line and reference not in used \
                and text(line["type"]) == text(row["type"]):
            used.add(reference)
            row["bank_reference"] = reference
            if to_sen(line["amount_rm"]) == to_sen(row["amount_rm"]):
                row["reconciliation_status"] = "matched"
            else:
                add_note(row, "document says RM%s, bank says RM%s" % (
                    rm(to_sen(row["amount_rm"])), rm(to_sen(line["amount_rm"]))))
                row["amount_rm"] = rm(to_sen(line["amount_rm"]))
                row["reconciliation_status"] = "needs_review"
            continue
        pending.append(row)

    candidates = {}
    claims = Counter()
    for row in pending:
        found = [ref for ref, line in lines.items()
                 if ref not in used and _fits(row, line)]
        candidates[text(row["txn_id"])] = found
        claims.update(found)

    ambiguous = []
    for row in pending:
        found = candidates[text(row["txn_id"])]
        if not found:
            row["reconciliation_status"] = "unmatched"
        elif len(found) == 1 and claims[found[0]] == 1:
            row["reconciliation_status"] = "matched"
            row["bank_reference"] = found[0]
        else:
            row["reconciliation_status"] = ""
            ambiguous.append({"txn_id": text(row["txn_id"]), "candidates": found})
    return ambiguous


def resolve(transactions: list, bank_lines: list, txn_id: str,
            bank_reference: str, reason: str) -> dict:
    """Step 6. Record the Bookkeeper's decision on one ambiguous row.

    An empty bank_reference means the Bookkeeper could not decide.
    """
    row = next(r for r in transactions if text(r["txn_id"]) == txn_id)
    if _status(row) != "":
        raise ValueError("%s is already settled" % txn_id)
    if not text(reason):
        raise ValueError("a reason is required")
    if not text(bank_reference):
        row["reconciliation_status"] = "needs_review"
        add_note(row, reason)
        return row
    line = next((l for l in bank_lines
                 if text(l["bank_reference"]) == bank_reference), None)
    if line is None or bank_reference in _used_references(transactions) \
            or not _fits(row, line):
        raise ValueError("%s is not a candidate for %s" % (bank_reference, txn_id))
    row["reconciliation_status"] = "ambiguous_resolved"
    row["bank_reference"] = bank_reference
    add_note(row, reason)
    return row


def close_week(transactions: list, bank_lines: list) -> list:
    """Step 7, payslip day only. Each unused bank line becomes a row."""
    waiting = [text(r["txn_id"]) for r in transactions if _status(r) == ""]
    if waiting:
        raise ValueError("rows still without a status: " + ", ".join(waiting))
    used = _used_references(transactions)
    number = max([_txn_number(r) for r in transactions] or [0])
    created = []
    leftover = [l for l in bank_lines if text(l["bank_reference"]) not in used]
    for line in sorted(leftover, key=lambda l: (to_date(l["date"]),
                                                text(l["bank_reference"]))):
        number += 1
        income = text(line["type"]) == "income"
        row = {
            "txn_id": "T%04d" % number,
            "date": to_date(line["date"]).isoformat(),
            "type": text(line["type"]),
            "category": "sales" if income else "other_expenses",
            "description": text(line["description"]),
            "amount_rm": rm(to_sen(line["amount_rm"])),
            "payment_method": "bank_transfer",
            "reconciliation_status": "unmatched",
            "bank_reference": text(line["bank_reference"]),
            "notes": "no document found for this bank line",
        }
        transactions.append(row)
        created.append(row)
    return created


def review_list(transactions: list) -> list:
    return [r for r in sorted(transactions, key=_txn_number)
            if _status(r) in ("unmatched", "duplicate", "needs_review")]
