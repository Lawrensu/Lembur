"""Hours tool: docs/SYSTEM_DESIGN.md section 4.2."""

from __future__ import annotations

from collections import OrderedDict

from conventions import (
    in_week, is_counted, is_empty, round_half_away, text, to_date,
    to_decimal, week_bounds,
)
from schema import ACTIVITIES, PERSON


def _source(corrected: bool) -> str:
    return "corrected" if corrected else "estimate"


def _line(date, activity, minutes, source, ref, product_id="", quantity=""):
    return {
        "entry_id": "",
        "date": to_date(date).isoformat(),
        "person": PERSON,
        "activity": activity,
        "product_id": product_id,
        "quantity": text(quantity),
        "minutes": str(minutes),
        "source": source,
        "assumption_ref": ref,
    }


def _sort_key(line: dict):
    return (
        to_date(line["date"]), ACTIVITIES.index(text(line["activity"])),
        text(line["product_id"]), text(line["assumption_ref"]),
        int(text(line["minutes"])),
    )


def build_hours(transactions: list, hours: list, plan, week: str,
                events=(), payslip_day: bool = False):
    """Rebuild the week's hours lines. Returns (all hours lines, warnings).

    Production and fulfilment lines of the week are rebuilt from the ledger
    on every run. The admin line is rebuilt on payslip day. Event lines are
    kept, and each event in `events` (date, minutes, message_date) is added
    once.
    """
    warnings = []
    rebuilt = {"production", "fulfilment"} | ({"admin"} if payslip_day else set())
    lines = [dict(l) for l in hours
             if not (in_week(l["date"], week) and text(l["activity"]) in rebuilt)]

    production = OrderedDict()
    fulfilment = OrderedDict()
    for row in transactions:
        if text(row.get("category")) != "sales" or not is_counted(row) \
                or not in_week(row.get("date"), week):
            continue
        product_id = text(row.get("product_id"))
        if not product_id or is_empty(row.get("quantity")):
            continue
        if product_id not in plan.products:
            warnings.append("%s: product %s is not in the plan"
                            % (text(row["txn_id"]), product_id))
            continue
        day = to_date(row["date"])
        key = (day, product_id)
        production[key] = production.get(key, 0) + to_decimal(row["quantity"])
        channel = text(row.get("channel"))
        if channel not in plan.channels:
            warnings.append("%s: channel %s is not in the plan"
                            % (text(row["txn_id"]), channel or "(empty)"))
            continue
        key = (day, product_id, channel)
        fulfilment[key] = fulfilment.get(key, 0) + 1

    for (day, product_id), units in production.items():
        ref = "products.%s.minutes_per_unit" % product_id
        value, corrected = plan.in_force(ref, day)
        lines.append(_line(day, "production", round_half_away(units * value),
                           _source(corrected), ref, product_id, units))

    for (day, product_id, channel), orders in fulfilment.items():
        ref = "channels.%s.fulfilment_minutes_per_order" % channel
        value, corrected = plan.in_force(ref, day)
        minutes = round_half_away(orders * value)
        if minutes:
            lines.append(_line(day, "fulfilment", minutes, _source(corrected),
                               ref, product_id, orders))

    for event in events:
        ref = "message.%s" % to_date(event.get("message_date")
                                     or event["date"]).isoformat()
        line = _line(event["date"], "event", int(event["minutes"]), "stated", ref)
        if not in_week(line["date"], week):
            warnings.append("event on %s is outside %s" % (line["date"], week))
            continue
        same = [l for l in lines if text(l["activity"]) == "event"
                and _sort_key(l) == _sort_key(line)]
        if not same:
            lines.append(line)

    if payslip_day:
        sunday = week_bounds(week)[1]
        ref = "assumptions.admin_hours_per_week"
        value, corrected = plan.in_force(ref, sunday)
        lines.append(_line(sunday, "admin", round_half_away(value * 60),
                           _source(corrected), ref))

    lines.sort(key=_sort_key)
    for number, line in enumerate(lines, start=1):
        line["entry_id"] = "H%04d" % number
    return lines, warnings
