"""Dates, weeks, money and rounding from docs/SYSTEM_DESIGN.md section 2."""

from __future__ import annotations

import datetime as dt
from decimal import ROUND_HALF_UP, Decimal


def is_empty(value) -> bool:
    return value is None or str(value).strip() == ""


def text(value) -> str:
    return "" if value is None else str(value).strip()


def to_decimal(value) -> Decimal:
    return Decimal(text(value))


def round_half_away(value: Decimal) -> int:
    """Whole number, halves away from zero: 304.5 becomes 305."""
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def to_sen(value):
    """Ringgit as written in a file to whole sen. Empty stays empty (None)."""
    if is_empty(value):
        return None
    return round_half_away(to_decimal(value) * 100)


def rm(sen: int) -> str:
    sign = "-" if sen < 0 else ""
    return "%s%d.%02d" % (sign, abs(sen) // 100, abs(sen) % 100)


def hours_display(minutes: int) -> str:
    tenths = round_half_away(Decimal(minutes) * 10 / 60)
    return "%d.%d" % (tenths // 10, tenths % 10)


def to_date(value) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(text(value)[:10])


def iso_week(value) -> str:
    year, week, _ = to_date(value).isocalendar()
    return "%d-W%02d" % (year, week)


def week_bounds(week: str):
    """Monday and Sunday of a week written like 2026-W41."""
    year, number = week.split("-W")
    monday = dt.date.fromisocalendar(int(year), int(number), 1)
    return monday, monday + dt.timedelta(days=6)


def in_week(value, week: str) -> bool:
    return not is_empty(value) and iso_week(value) == week


def add_note(row: dict, message: str) -> None:
    existing = text(row.get("notes"))
    row["notes"] = message if not existing else existing + "; " + message


def is_counted(row: dict) -> bool:
    """Counted row: not a duplicate and the amount could be read."""
    return (
        text(row.get("reconciliation_status")) != "duplicate"
        and not is_empty(row.get("amount_rm"))
    )
