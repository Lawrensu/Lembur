"""Synthetic fixture and deterministic answer-key calculation (design sections 2-4).
Run after data/demo/.plan.ref/build.py. This is a test fixture, not Law's runtime.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from collections import defaultdict
from copy import deepcopy
import importlib.util
import json
import re
import openpyxl

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("plan_builder", ROOT / "data/demo/.plan.ref/build.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
TX = "txn_id date type category description product_id quantity amount_rm channel payment_method counterparty reference source_file reconciliation_status bank_reference notes".split()
BANK = "date description type amount_rm bank_reference".split()
HOURS = "entry_id date person activity product_id quantity minutes source assumption_ref".split()

def sen(value):
    d = Decimal(str(value))*100
    assert d == d.to_integral_value(), value
    return int(d)

def display(value, places=2):
    return str(Decimal(value).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))

def money(value):
    return display(Decimal(value)/100)

plan_book = openpyxl.load_workbook(ROOT / "data/demo/plan.xlsx", data_only=True)
plan = {s.title: [dict(zip(next(s.values), r)) for r in list(s.values)[1:]] for s in plan_book}
products = {r["product_id"]: r for r in plan["products"]}
channels = {r["channel"]: r for r in plan["channels"]}
assumptions = plan["assumptions"][0]
assert products["P01"]["minutes_per_unit"] == 20 and not plan["change_log"]
correction = {"changed_at": "2026-10-07", "field": "products.P01.minutes_per_unit", "old_value": 20, "new_value": 15,
              "reason": "I timed myself today, keychains take 15 minutes not 20", "source": "message.2026-10-07"}
products["P01"]["minutes_per_unit"] = 15
changes = [correction]

def value_on(ref, day):
    later = sorted([c for c in changes if c["field"] == ref and c["changed_at"] > day], key=lambda c:c["changed_at"])
    if later:
        return later[0]["old_value"]
    p = ref.split(".")
    return assumptions[p[1]] if p[0] == "assumptions" else (products if p[0] == "products" else channels)[p[1]][p[2]]

def source_on(ref, day):
    # Sharon's clarification: historical baseline remains estimate.
    return "corrected" if any(c["field"] == ref and c["changed_at"] <= day for c in changes) else "estimate"

rows, banks = [], []

def bank(day, who, kind, amount, ref):
    banks.append(dict(zip(BANK, [day, who, kind, amount, ref])))

def add(day, kind, category, desc, amount, who, ref=None, product=None, channel=None, cash=False, filename=None, status=None):
    r = dict.fromkeys(TX)
    r.update(txn_id=f"T{len(rows)+1:04d}", date=day, type=kind, category=category, description=desc,
             product_id=product, quantity=1 if product else None, amount_rm=amount, channel=channel,
             payment_method="cash" if cash else "bank_transfer", counterparty=who, reference=ref,
             source_file=f"receipts/2026-10/{filename}" if filename else f"receipts/2026-10/message_{day}.txt",
             reconciliation_status=status)
    rows.append(r)
    return r

def sale(day, who, product="P01", channel="instagram", ref=None, amount=None, no_ref=False):
    price = products[product]["price_rm"]
    cash = channel == "bazaar"
    filename = None if cash else f"order_{day}_{who.lower()}.png"
    r = add(day, "income", "sales", f"1 {products[product]['name']}", price, who,
            None if no_ref else ref, product, channel, cash, filename)
    if not cash:
        bank(day, f"Transfer from {who} - accessories", "income", price if amount is None else amount, ref)
    return r

sale("2026-10-05", "Dana", ref="DEMO-IN-001", no_ref=True)
sale("2026-10-05", "Mira", ref="DEMO-IN-002", no_ref=True)
add("2026-10-05", "expense", "materials", "Small bead restock", 18, "Demo Bead Nook", "DEMO-OUT-001", filename="receipt_beads.png")
bank("2026-10-05", "Demo Bead Nook - bead materials restock", "expense", 18, "DEMO-OUT-001")
add("2026-10-05", "expense", "materials", "Small bead restock", 18, "Demo Bead Nook", "DEMO-OUT-001", filename="receipt_beads_copy.png")
sale("2026-10-06", "Farah", ref="DEMO-IN-003")
sale("2026-10-06", "Nisa", ref="DEMO-IN-004")
sale("2026-10-06", "Hana", "P02", ref="DEMO-IN-005")
sale("2026-10-07", "Iman", ref="DEMO-IN-006")
add("2026-10-07", "expense", "packaging", "Small pouch restock", 6, "Demo Pouch Corner", "DEMO-OUT-002", filename="receipt_pouches.png")
bank("2026-10-07", "Demo Pouch Corner - packaging pouches", "expense", 6, "DEMO-OUT-002")
sale("2026-10-08", "Lina", ref="DEMO-IN-007")
sale("2026-10-08", "Rina", "P02", "telegram", ref="DEMO-IN-008")
blur = add("2026-10-08", "expense", "materials", "Thread refill; total unreadable", None, "Demo Thread Stop", cash=True, filename="receipt_thread_blurred.png", status="needs_review")
blur["notes"] = "Amount unreadable at intake; request a clearer receipt. Do not infer an amount."
sale("2026-10-09", "Suri", ref="DEMO-IN-009")
# Nine shipped orders in this synthetic week; all billed under one courier settlement.
shipping_sen = 9 * sen(channels["instagram"]["shipping_cost_per_order_rm"])
add("2026-10-09", "expense", "shipping", "Courier settlement for nine weekly parcels", float(Decimal(shipping_sen)/100), "Demo Parcel Desk", "DEMO-OUT-003", filename="receipt_shipping.png")
bank("2026-10-09", "Demo Parcel Desk - nine weekly parcels", "expense", float(Decimal(shipping_sen)/100), "DEMO-OUT-003")
for who in ["Aina", "Bella", "Citra"]:
    sale("2026-10-10", who, channel="bazaar")
sale("2026-10-10", "Dina", "P02", "bazaar")
sale("2026-10-11", "Zahra", ref="DEMO-IN-010", amount=4.5)
bank("2026-10-11", "Demo Bead Nook - bead materials top-up", "expense", 9, "DEMO-OUT-004")
raw = deepcopy(rows)

# Reconciliation: preserve intake flags, cash first, duplicate key, reference then amount.
used = set()
pending = []
for i, r in enumerate(rows):
    if r["reconciliation_status"] == "needs_review":
        continue
    if r["payment_method"] == "cash":
        r["reconciliation_status"] = "cash_declared"
        continue
    keys = ["date", "type", "amount_rm", "counterparty", "reference"]
    dup = next((p for p in rows[:i] if all(p[k] == r[k] for k in keys)), None)
    if dup:
        r["reconciliation_status"] = "duplicate"
        r["notes"] = f"Duplicate of {dup['txn_id']}; exclude from totals and hours."
        continue
    match = next((b for b in banks if r["reference"] and b["bank_reference"] == r["reference"] and b["type"] == r["type"] and b["bank_reference"] not in used), None)
    if match:
        r["bank_reference"] = match["bank_reference"]
        used.add(match["bank_reference"])
        if sen(r["amount_rm"]) != sen(match["amount_rm"]):
            r["notes"] = f"Document RM{money(sen(r['amount_rm']))}; bank RM{money(sen(match['amount_rm']))}; bank amount used. Confirm underpayment."
            r["amount_rm"] = match["amount_rm"]
            r["reconciliation_status"] = "needs_review"
        else:
            r["reconciliation_status"] = "matched"
    else:
        pending.append(r)

candidates = {}
for r in pending:
    candidates[r["txn_id"]] = [b for b in banks if b["bank_reference"] not in used and b["type"] == r["type"] and sen(b["amount_rm"]) == sen(r["amount_rm"]) and abs((date.fromisoformat(b["date"]) - date.fromisoformat(r["date"])).days) <= 1]
for r in pending:
    fits = candidates[r["txn_id"]]
    if not fits:
        r["reconciliation_status"] = "unmatched"
        continue
    sole = len(fits) == 1 and sum(any(b["bank_reference"] == fits[0]["bank_reference"] for b in v) for v in candidates.values()) == 1
    if sole:
        selected = fits[0]
        r["reconciliation_status"] = "matched"
    else:
        chosen = [b for b in fits if f"from {r['counterparty']} -" in b["description"] and b["bank_reference"] not in used]
        assert len(chosen) == 1
        selected = chosen[0]
        r["reconciliation_status"] = "ambiguous_resolved"
        r["notes"] = f"Multiple RM{money(sen(r['amount_rm']))} candidates; counterparty {r['counterparty']} matches bank description. Paired to {selected['bank_reference']}."
    r["bank_reference"] = selected["bank_reference"]
    used.add(selected["bank_reference"])
for b in banks:
    if b["bank_reference"] not in used:
        r = dict.fromkeys(TX)
        r.update(txn_id=f"T{len(rows)+1:04d}", date=b["date"], type=b["type"], category="materials",
                 amount_rm=b["amount_rm"], description=b["description"], payment_method="bank_transfer",
                 bank_reference=b["bank_reference"], reconciliation_status="unmatched",
                 notes="No document was found. Bank description names bead materials supplier; request receipt.")
        rows.append(r)

counted = [r for r in rows if r["reconciliation_status"] != "duplicate" and r["amount_rm"] is not None]
prod_groups, fulfil_groups = defaultdict(int), defaultdict(int)
for r in counted:
    if r["category"] == "sales" and r["product_id"] and r["quantity"]:
        prod_groups[r["date"], r["product_id"]] += r["quantity"]
        fulfil_groups[r["date"], r["product_id"], r["channel"]] += 1
hours = []
def hour(day, activity, product, qty, minutes, source, ref):
    assert isinstance(minutes, int)
    hours.append(dict(zip(HOURS, [None, day, "person_1", activity, product, qty, minutes, source, ref])))
for (day, p), qty in sorted(prod_groups.items()):
    ref = f"products.{p}.minutes_per_unit"
    hour(day, "production", p, qty, qty*value_on(ref, day), source_on(ref, day), ref)
for (day, p, channel), qty in sorted(fulfil_groups.items()):
    ref = f"channels.{channel}.fulfilment_minutes_per_order"
    minutes = qty*value_on(ref, day)
    if minutes:
        hour(day, "fulfilment", p, qty, minutes, source_on(ref, day), ref)
hour("2026-10-10", "event", None, None, 8*60, "stated", "message.2026-10-10")
ref = "assumptions.admin_hours_per_week"
hour("2026-10-11", "admin", None, None, value_on(ref, "2026-10-11")*60, source_on(ref, "2026-10-11"), ref)
activity_order = {v:i for i,v in enumerate(["production", "fulfilment", "event", "admin"])}
hours.sort(key=lambda r:(r["date"], activity_order[r["activity"]], r["product_id"] or "", r["assumption_ref"]))
for i, h in enumerate(hours, 1): h["entry_id"] = f"H{i:04d}"

categories = {c:sum(sen(r["amount_rm"]) for r in counted if r["category"] == c) for c in ["sales", "materials", "packaging", "platform_fees", "shipping", "other_expenses"]}
take_home = categories["sales"] - sum(v for k,v in categories.items() if k != "sales")
minutes = sum(h["minutes"] for h in hours)
activity = {a:sum(h["minutes"] for h in hours if h["activity"] == a) for a in activity_order}
product_results = {}
for p, config in products.items():
    sales = [r for r in counted if r["category"] == "sales" and r["product_id"] == p]
    revenue = sum(sen(r["amount_rm"]) for r in sales)
    qty = sum(r["quantity"] for r in sales)
    costs = qty*(sen(config["material_cost_rm"]) + sen(config["packaging_cost_rm"]))
    channel_cost = 0
    for r in sales:
        c = channels[r["channel"]]
        fee = int((Decimal(sen(r["amount_rm"]))*Decimal(str(c["fee_percent"]))/100).quantize(Decimal(1), rounding=ROUND_HALF_UP))
        channel_cost += fee+sen(c["fee_per_order_rm"])+sen(c["shipping_cost_per_order_rm"])
    profit = revenue-costs-channel_cost
    direct = sum(h["minutes"] for h in hours if h["product_id"] == p)
    product_results[p] = dict(units=qty, revenue_sen=revenue, unit_cost_sen=costs, channel_cost_sen=channel_cost, profit_sen=profit, direct_minutes=direct, profit_per_hour=display(Decimal(profit)*60/(direct*100)) if direct else None, loses_money=profit < 0)
result = dict(category_sen=categories, take_home_sen=take_home, total_minutes=minutes,
              display_hours=display(Decimal(minutes)/60, 1), hourly_rate=display(Decimal(take_home)*60/(minutes*100)),
              margin_percent=display(Decimal(take_home)*100/categories["sales"], 0), activity_minutes=activity,
              shared_minutes=activity["event"]+activity["admin"], products=product_results,
              review_ids=[r["txn_id"] for r in rows if r["reconciliation_status"] in ["duplicate", "unmatched", "needs_review"]])
assert product_results["P01"]["units"] > product_results["P02"]["units"]
assert product_results["P01"]["profit_sen"] < 0
assert shipping_sen == sum(sen(channels[r["channel"]]["shipping_cost_per_order_rm"]) for r in counted if r["category"] == "sales")
book = ROOT / "data/answer_key/expected_ledger.xlsx"
mod.save_book(book, {"transactions":(TX, [[r[k] for k in TX] for r in rows]), "bank_lines":(BANK, [[r[k] for k in BANK] for r in banks]), "hours":(HOURS, [[r[k] for k in HOURS] for r in hours])}, "Lembur expected ledger - synthetic demo - pending sign-off")
# Native workbook round-trip: exact types/values, no formulas or uncached cells.
check = openpyxl.load_workbook(book, data_only=True)
for name, headers, expected in [("transactions",TX,rows),("bank_lines",BANK,banks),("hours",HOURS,hours)]:
    actual = list(check[name].values)
    assert list(actual[0]) == headers
    assert [dict(zip(headers,r)) for r in actual[1:]] == expected
out = ROOT / "data/answer_key/.expected_ledger.ref"
(out/"calculation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
(out/"render_manifest.json").write_text(json.dumps({"transactions":rows, "raw_documents":raw, "bank_lines":banks, "correction":correction}, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
