"""Numbers tool: docs/SYSTEM_DESIGN.md section 4.3.

Money is in whole sen and time in whole minutes. Display strings are added
beside each figure so agents copy them and never calculate.
"""

from __future__ import annotations

from collections import OrderedDict
from decimal import Decimal

from conventions import (
    hours_display, in_week, is_counted, is_empty, rm, round_half_away, text,
    to_decimal, to_sen, week_bounds,
)
from schema import ACTIVITIES, CATEGORIES, EXPENSE_CATEGORIES


def _rate_sen(amount_sen: int, minutes: int):
    """Sen per hour, or None when there are no minutes."""
    if not minutes:
        return None
    return round_half_away(Decimal(amount_sen) * 60 / minutes)


def _money(sen):
    return None if sen is None else rm(sen)


def compute(transactions: list, hours: list, plan, week: str) -> dict:
    invalid = []
    for row in transactions:
        if not is_counted(row):
            continue
        category, kind = text(row.get("category")), text(row.get("type"))
        if category not in CATEGORIES:
            invalid.append("%s: empty or unknown category %r"
                           % (text(row.get("txn_id")), category))
        elif kind not in ("income", "expense") or (category == "sales") != (kind == "income"):
            invalid.append("%s: category and type disagree"
                           % text(row.get("txn_id")))
    if invalid:
        raise ValueError("counted rows need category classification: "
                         + "; ".join(invalid))
    warnings = []
    rows = [r for r in transactions
            if is_counted(r) and in_week(r.get("date"), week)]
    lines = [l for l in hours if in_week(l["date"], week)]

    totals = OrderedDict((category, 0) for category in CATEGORIES)
    for row in rows:
        category = text(row.get("category"))
        if category not in totals:
            raise ValueError("%s has unknown category %r"
                             % (text(row["txn_id"]), category))
        totals[category] += to_sen(row["amount_rm"])
    sales = totals["sales"]
    take_home = sales - sum(totals[c] for c in EXPENSE_CATEGORIES)

    minutes = OrderedDict((activity, 0) for activity in ACTIVITIES)
    for line in lines:
        minutes[text(line["activity"])] += int(text(line["minutes"]))
    week_minutes = sum(minutes.values())
    shared_minutes = minutes["event"] + minutes["admin"]

    products = OrderedDict()
    for product_id in plan.products:
        products[product_id] = {
            "units": Decimal(0), "revenue": 0, "channel_costs": 0,
            "direct_minutes": 0,
        }
    for row in rows:
        product_id = text(row.get("product_id"))
        if text(row.get("category")) != "sales" or not product_id:
            continue
        if product_id not in products or is_empty(row.get("quantity")):
            warnings.append("%s: sale left out of product profit"
                            % text(row["txn_id"]))
            continue
        item = products[product_id]
        amount = to_sen(row["amount_rm"])
        item["units"] += to_decimal(row["quantity"])
        item["revenue"] += amount
        channel = plan.channels.get(text(row.get("channel")))
        if channel is None:
            warnings.append("%s: no channel costs, channel is not in the plan"
                            % text(row["txn_id"]))
            continue
        fee = round_half_away(Decimal(amount) * to_decimal(channel["fee_percent"]) / 100)
        item["channel_costs"] += (
            fee + to_sen(channel["fee_per_order_rm"])
            + to_sen(channel["shipping_cost_per_order_rm"])
        )
    for line in lines:
        product_id = text(line["product_id"])
        if text(line["activity"]) in ("production", "fulfilment") \
                and product_id in products:
            products[product_id]["direct_minutes"] += int(text(line["minutes"]))

    product_output = []
    for product_id, item in products.items():
        plan_row = plan.products[product_id]
        unit_cost = to_sen(plan_row["material_cost_rm"]) + to_sen(plan_row["packaging_cost_rm"])
        unit_costs = round_half_away(item["units"] * unit_cost)
        profit = item["revenue"] - unit_costs - item["channel_costs"]
        per_hour = _rate_sen(profit, item["direct_minutes"])
        units = item["units"]
        product_output.append(OrderedDict([
            ("product_id", product_id),
            ("name", text(plan_row["name"])),
            ("units_sold", int(units) if units == units.to_integral() else str(units)),
            ("revenue_rm", rm(item["revenue"])),
            ("unit_costs_rm", rm(unit_costs)),
            ("channel_costs_rm", rm(item["channel_costs"])),
            ("profit_rm", rm(profit)),
            ("direct_minutes", item["direct_minutes"]),
            ("direct_hours", hours_display(item["direct_minutes"])),
            ("profit_per_hour_rm", _money(per_hour)),
            ("loses_money", profit < 0),
        ]))

    margin = None if not sales else round_half_away(Decimal(take_home) * 100 / sales)
    hourly_rate = _rate_sen(take_home, week_minutes)
    monday, sunday = week_bounds(week)
    assumptions = plan.assumptions

    return OrderedDict([
        ("week", week),
        ("date_from", monday.isoformat()),
        ("date_to", sunday.isoformat()),
        ("hourly_rate_rm", _money(hourly_rate)),
        ("take_home_rm", rm(take_home)),
        ("category_totals_rm", OrderedDict((c, rm(v)) for c, v in totals.items())),
        ("minutes", OrderedDict(list(minutes.items()) + [("total", week_minutes)])),
        ("hours", OrderedDict(
            [(a, hours_display(m)) for a, m in minutes.items()]
            + [("total", hours_display(week_minutes))])),
        ("shared_minutes", shared_minutes),
        ("shared_hours", hours_display(shared_minutes)),
        ("products", product_output),
        ("plan_versus_reality", OrderedDict([
            ("margin_percent", margin),
            ("planned_margin_percent", text(assumptions["planned_margin_percent"])),
            ("hourly_rate_rm", _money(hourly_rate)),
            ("target_hourly_rate_rm", rm(to_sen(assumptions["target_hourly_rate_rm"]))),
        ])),
        ("warnings", warnings),
    ])
