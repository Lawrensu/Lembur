"""The plan file: current values, values in force on a date, corrections."""

from __future__ import annotations

from decimal import Decimal

from conventions import text, to_date, to_decimal
from schema import CORRECTABLE_COLUMNS


class Plan:
    def __init__(self, book: dict):
        self.book = book
        self.products = {text(r["product_id"]): r for r in book["products"]}
        self.channels = {text(r["channel"]): r for r in book["channels"]}
        self.assumptions = book["assumptions"][0]
        self.change_log = book.setdefault("change_log", [])

    def _row(self, ref: str):
        """The row and column an assumption reference names."""
        parts = ref.split(".")
        if parts[0] == "assumptions" and len(parts) == 2:
            return self.assumptions, parts[1]
        sheet = {"products": self.products, "channels": self.channels}.get(parts[0])
        key, column = ".".join(parts[1:-1]), parts[-1]
        if sheet is None or key not in sheet or column not in sheet[key]:
            raise KeyError("no plan value named %s" % ref)
        return sheet[key], column

    def current(self, ref: str) -> Decimal:
        row, column = self._row(ref)
        return to_decimal(row[column])

    def in_force(self, ref: str, date):
        """Value in force on a date, and whether it came from a correction."""
        day = to_date(date)
        entries = [e for e in self.change_log if text(e["field"]) == ref]
        later = sorted(
            (e for e in entries if to_date(e["changed_at"]) > day),
            key=lambda e: to_date(e["changed_at"]),
        )
        corrected = any(to_date(e["changed_at"]) <= day for e in entries)
        value = to_decimal(later[0]["old_value"]) if later else self.current(ref)
        return value, corrected

    def correct(self, ref: str, new_value, changed_at, reason: str) -> dict:
        """Apply a student correction: update the cell and log the change."""
        row, column = self._row(ref)
        if column not in CORRECTABLE_COLUMNS:
            raise ValueError("%s cannot be corrected" % ref)
        day = to_date(changed_at).isoformat()
        entry = {
            "changed_at": day,
            "field": ref,
            "old_value": text(row[column]),
            "new_value": text(new_value),
            "reason": reason,
            "source": "message.%s" % day,
        }
        row[column] = text(new_value)
        self.change_log.append(entry)
        return entry
