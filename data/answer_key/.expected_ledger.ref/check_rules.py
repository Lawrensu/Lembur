"""Read-only synthetic fixture validation; writes only adjacent rule_check.md.

Run with Python -B. No application code, renderers, or independent calculators
are imported. Only raw_documents from the permitted manifest is used as intake
metadata. Image observations below are manual transcriptions, NOT automated OCR.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import date, datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from pathlib import Path, PurePosixPath
import csv
import hashlib
import io
import json
import re
import sys

import openpyxl
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INBOX = ROOT / "data/demo/inbox"
START = date(2026, 10, 5)
DAYS = [(START + timedelta(days=i)).isoformat() for i in range(7)]
CATEGORIES = "sales materials packaging platform_fees shipping other_expenses".split()
STATUSES = {"matched", "ambiguous_resolved", "unmatched", "duplicate", "needs_review", "cash_declared"}
REVIEW = {"unmatched", "duplicate", "needs_review"}
SCHEMAS = {
    "products": "product_id name price_rm material_cost_rm packaging_cost_rm minutes_per_unit".split(),
    "channels": "channel fee_percent fee_per_order_rm shipping_cost_per_order_rm fulfilment_minutes_per_order".split(),
    "assumptions": "admin_hours_per_week planned_margin_percent target_hourly_rate_rm".split(),
    "change_log": "changed_at field old_value new_value reason source".split(),
    "transactions": "txn_id date type category description product_id quantity amount_rm channel payment_method counterparty reference source_file reconciliation_status bank_reference notes".split(),
    "bank_lines": "date description type amount_rm bank_reference".split(),
    "hours": "entry_id date person activity product_id quantity minutes source assumption_ref".split(),
}
RESULTS = []
EVIDENCE = []
FINGERPRINTS = {}

# Observed directly in the rendered images on 2026-10-10; not inferred from JSON.
# Order tuple: date, customer, product, quantity, amount, channel, printed reference.
ORDER_VISUALS = {
    "order_2026-10-05_dana.png": ("5d9fb21d22b7ebd294ca7268786a3cf046aed2cc3270f5b38a43fe36586da6af", ("2026-10-05", "Dana", "P01", 1, 500, "instagram", None)),
    "order_2026-10-05_mira.png": ("eb7c9461292c40cfa04d34c4427a16ae06169c202df0c7df4e40bd24fe9ed4f9", ("2026-10-05", "Mira", "P01", 1, 500, "instagram", None)),
    "order_2026-10-06_farah.png": ("8aeb78dab505818dbc97ff12306172e5edb65fedaf18222473af3ab9f144f18a", ("2026-10-06", "Farah", "P01", 1, 500, "instagram", "DEMO-IN-003")),
    "order_2026-10-06_hana.png": ("59042ba63fd16eb9fcb2403f907ee317418459d2697b94166823034413cee582", ("2026-10-06", "Hana", "P02", 1, 1800, "instagram", "DEMO-IN-005")),
    "order_2026-10-06_nisa.png": ("aca7ee08b8e9ff38ca750d72fa527fbd87367e07264b8c9106e74423f69e5478", ("2026-10-06", "Nisa", "P01", 1, 500, "instagram", "DEMO-IN-004")),
    "order_2026-10-07_iman.png": ("0028e34871653080c3198d02edab0d4d9f6351cec98266f42e59e82c16a52f05", ("2026-10-07", "Iman", "P01", 1, 500, "instagram", "DEMO-IN-006")),
    "order_2026-10-08_lina.png": ("bae94791df8492c87eedb31e064d5091e49a66dfaf97e376ecbbd1abc8143ea9", ("2026-10-08", "Lina", "P01", 1, 500, "instagram", "DEMO-IN-007")),
    "order_2026-10-08_rina.png": ("dbba022cc4bfa86c7704d51fc07b7e91944bcdb814eee737ca86eb7c7e433fee", ("2026-10-08", "Rina", "P02", 1, 1800, "telegram", "DEMO-IN-008")),
    "order_2026-10-09_suri.png": ("457a1165192d7c31ee85c78fa58301a69db4620a9b01d3fbd9ec6d582a9b8a0a", ("2026-10-09", "Suri", "P01", 1, 500, "instagram", "DEMO-IN-009")),
    "order_2026-10-11_zahra.png": ("b51353a294ba30574ff6ff019d654a623a41095d5e6c34b3003ddb83b32c620c", ("2026-10-11", "Zahra", "P01", 1, 500, "instagram", "DEMO-IN-010")),
}
# Receipt tuple: date, supplier, amount (None = unreadable), method, reference.
RECEIPT_VISUALS = {
    "receipt_beads.png": ("58f2010d99a74db5b01dca1969b7cf1850cb93f02f4c77061746b081de835add", ("2026-10-05", "Demo Bead Nook", 1800, "bank_transfer", "DEMO-OUT-001")),
    "receipt_pouches.png": ("89027eb6c17281be56536eae0d5d50c45c0618eca38077e65866eaf82df07ef9", ("2026-10-07", "Demo Pouch Corner", 600, "bank_transfer", "DEMO-OUT-002")),
    "receipt_shipping.png": ("af540321667891715f1ed0540091f841782995035313709595e8a6e6531d863c", ("2026-10-09", "Demo Parcel Desk", 3600, "bank_transfer", "DEMO-OUT-003")),
    "receipt_thread_blurred.png": ("941767990d765f2b0192b4910ec64237cd4200e75215feb894c1aae14de0edd7", ("2026-10-08", "Demo Thread Stop", None, "cash", None)),
}


def check(name, condition, detail=""):
    RESULTS.append(("PASS" if condition else "FAIL", name, str(detail)))
    return bool(condition)


def sen(value):
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError("Boolean is not money")
    scaled = Decimal(str(value)) * 100
    if not scaled.is_finite() or scaled != scaled.to_integral_value():
        raise ValueError(f"Not whole-sen money: {value!r}")
    return int(scaled)


def whole(value):
    return not isinstance(value, bool) and isinstance(value, (int, float, Decimal)) and Decimal(str(value)) == int(value)


def rounded(numerator, denominator=1):
    if denominator <= 0:
        raise ValueError("Positive denominator required")
    sign = -1 if numerator < 0 else 1
    quotient, remainder = divmod(abs(numerator), denominator)
    return sign * (quotient + (2 * remainder >= denominator))


def rm(value):
    if value is None:
        return "unknown"
    return f"{'-' if value < 0 else ''}RM{abs(value) // 100}.{abs(value) % 100:02d}"


def rate(value, minutes):
    return rm(rounded(value * 60, minutes)) if minutes else "not shown"


def fee(amount, percent):
    exact = amount * Fraction(str(percent)) / 100
    return rounded(exact.numerator, exact.denominator)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def counted(row):
    return row["reconciliation_status"] != "duplicate" and row["amount_rm"] is not None


def normalise(rows):
    return [{k: sen(v) if k.endswith("_rm") else v for k, v in row.items()} for row in rows]


def read_book(path, sheets):
    book = openpyxl.load_workbook(path, read_only=True, data_only=False)
    data = {}
    try:
        check(f"Schema: {path.name} sheets", book.sheetnames == sheets, str(book.sheetnames))
        for name in sheets:
            sheet = book[name]
            rows = list(sheet.iter_rows())
            headers = [c.value for c in rows[0]]
            check(f"Schema: {path.name}/{name} exact headers", headers == SCHEMAS[name], ", ".join(map(str, headers)))
            formulas = [c.coordinate for row in rows for c in row if c.data_type == "f"]
            check(f"Literal fixture cells: {path.name}/{name}", not formulas, f"Formula cells: {formulas}")
            body = [row for row in rows[1:] if any(c.value is not None for c in row)]
            check(f"No blank data rows: {path.name}/{name}", len(body) == len(rows) - 1)
            records = [dict(zip(headers, [c.value for c in row])) for row in body]
            bad_formats = [c.coordinate for row in body for key, c in zip(headers, row)
                           if key.endswith("_rm") and c.value is not None and c.number_format != "0.00"]
            check(f"Money displayed with two decimals: {path.name}/{name}", not bad_formats, f"Nonconforming cells: {bad_formats}")
            data[name] = normalise(records)
    finally:
        book.close()
    return data


def candidates(row, banks):
    return [b for b in banks if b["type"] == row["type"] and b["amount_rm"] == row["amount_rm"]
            and abs((date.fromisoformat(b["date"]) - date.fromisoformat(row["date"])).days) <= 1]


def reconcile(raw, banks):
    """Rebuild final-state decisions without consulting expected statuses/assignments."""
    out = deepcopy(sorted(raw, key=lambda r: r["txn_id"]))
    unused = {b["bank_reference"]: b for b in banks}
    seen = {}
    pending = []
    decisions = {}
    for row in out:
        tid = row["txn_id"]
        if row["reconciliation_status"] == "needs_review":
            decisions[tid] = ("intake", None)
            continue
        if row["payment_method"] == "cash":
            row["reconciliation_status"] = "cash_declared"
            decisions[tid] = ("cash", None)
            continue
        key = tuple(row[k] for k in ("date", "type", "amount_rm", "counterparty", "reference"))
        if key in seen:
            row["reconciliation_status"] = "duplicate"
            decisions[tid] = ("duplicate", seen[key])
            continue
        seen[key] = tid
        bank = unused.get(row["reference"])
        if bank and bank["type"] == row["type"]:
            original = row["amount_rm"]
            row["reconciliation_status"] = "matched" if original == bank["amount_rm"] else "needs_review"
            row["amount_rm"] = bank["amount_rm"]
            row["bank_reference"] = bank["bank_reference"]
            decisions[tid] = ("reference", original)
            del unused[bank["bank_reference"]]
        else:
            pending.append(row)
    # Keep candidate competition simultaneous; do not silently let row order pick a payer.
    pools = {r["txn_id"]: candidates(r, unused.values()) for r in pending}
    demand = Counter(b["bank_reference"] for pool in pools.values() for b in pool)
    for row in pending:
        pool = pools[row["txn_id"]]
        choice = None
        if not pool:
            status = "unmatched"
        elif len(pool) == 1 and demand[pool[0]["bank_reference"]] == 1:
            status, choice = "matched", pool[0]
        else:
            named = [b for b in pool if row["counterparty"] and
                     re.search(r"(?<!\w)" + re.escape(row["counterparty"]) + r"(?!\w)", b["description"], re.I)
                     and b["bank_reference"] in unused]
            status = "ambiguous_resolved" if len(named) == 1 else "needs_review"
            choice = named[0] if len(named) == 1 else None
        row["reconciliation_status"] = status
        if choice:
            row["bank_reference"] = choice["bank_reference"]
            del unused[choice["bank_reference"]]
        decisions[row["txn_id"]] = ("amount", [b["bank_reference"] for b in pool])
    next_id = max(int(r["txn_id"][1:]) for r in out) + 1
    for bank in unused.values():
        row = dict.fromkeys(SCHEMAS["transactions"])
        row.update(bank)
        row.update(txn_id=f"T{next_id:04d}", payment_method="bank_transfer", reconciliation_status="unmatched")
        text = bank["description"].lower()
        row["category"] = "sales" if bank["type"] == "income" else "materials" if "bead materials" in text else "other_expenses"
        out.append(row)
        decisions[row["txn_id"]] = ("leftover", bank["bank_reference"])
        next_id += 1
    return out, decisions


def make_hours(sales, products, channels, assumptions, correction, events):
    production = Counter()
    fulfilment = Counter()
    for row in sales:
        if counted(row) and row["category"] == "sales" and row["product_id"] and row["quantity"]:
            production[(row["date"], row["product_id"])] += row["quantity"]
            fulfilment[(row["date"], row["product_id"], row["channel"])] += 1
    rows = []
    for (day, pid), units in sorted(production.items()):
        changed = pid == correction["product_id"] and day >= correction["changed_at"]
        minutes = correction["new_value"] if changed else products[pid]["minutes_per_unit"]
        rows.append((day, "person_1", "production", pid, units, units * minutes,
                     "corrected" if changed else "estimate", f"products.{pid}.minutes_per_unit"))
    for (day, pid, channel), orders in sorted(fulfilment.items()):
        minutes = orders * channels[channel]["fulfilment_minutes_per_order"]
        if minutes:
            rows.append((day, "person_1", "fulfilment", pid, orders, minutes, "estimate", f"channels.{channel}.fulfilment_minutes_per_order"))
    for day, minutes in events:
        rows.append((day, "person_1", "event", None, None, minutes, "stated", f"message.{day}"))
    admin = Fraction(str(assumptions["admin_hours_per_week"])) * 60
    if admin.denominator != 1:
        raise ValueError("Admin assumption does not produce whole minutes")
    rows.append((DAYS[-1], "person_1", "admin", None, None, int(admin), "estimate", "assumptions.admin_hours_per_week"))
    return rows


def validate():
    inputs = [ROOT / "docs/PLAN.md", ROOT / "docs/SYSTEM_DESIGN.md", ROOT / "data/demo/plan.xlsx",
              ROOT / "data/answer_key/expected_ledger.xlsx", ROOT / "data/demo/messages.md", HERE / "render_manifest.json"]
    inputs += sorted(p for p in INBOX.iterdir() if p.is_file())
    FINGERPRINTS.update({str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in inputs})
    check("Output scope", HERE == ROOT / "data/answer_key/.expected_ledger.ref")
    check("Arithmetic: halves away from zero", (rounded(609, 2), rounded(-609, 2), rounded(30449, 100)) == (305, -305, 304))
    check("Arithmetic: fees rounded per order", fee(101, 50) == 51 and 2 * fee(101, 50) == 102 and fee(202, 50) == 101)
    try:
        sen("1.001")
        rejected = False
    except ValueError:
        rejected = True
    check("Arithmetic: sub-sen input rejected, blanks preserved", rejected and sen(None) is None and sen("4.50") == 450)
    check("Arithmetic: zero-minute rate suppressed", rate(100, 0) == "not shown")

    specification = (ROOT / "docs/SYSTEM_DESIGN.md").read_text(encoding="utf-8")
    section = specification.split("## 3.2 ", 1)[1].split("## 4. ", 1)[0]
    for name, headers in SCHEMAS.items():
        part = section.split(f"* **`{name}`**", 1)[1].split("\n* **", 1)[0]
        extracted = re.findall(r"^  \* `([^`]+)`", part, re.M)
        check(f"Schema contract agrees with design: {name}", extracted == headers)
    plan = read_book(ROOT / "data/demo/plan.xlsx", ["products", "channels", "assumptions", "change_log"])
    ledger = read_book(ROOT / "data/answer_key/expected_ledger.xlsx", ["transactions", "bank_lines", "hours"])
    tx, bank_expected, hours = (ledger[k] for k in ("transactions", "bank_lines", "hours"))
    products = {r["product_id"]: r for r in plan["products"]}
    channels = {r["channel"]: r for r in plan["channels"]}
    check("Plan keys and single assumptions row", len(products) == len(plan["products"]) and len(channels) == len(plan["channels"]) and len(plan["assumptions"]) == 1)
    assumptions = plan["assumptions"][0]
    check("Plan IDs and channel labels", all(re.fullmatch(r"P\d{2}", p) for p in products) and all(re.fullmatch(r"[a-z][a-z_]*", c) for c in channels))
    check("Plan nonnegative costs and whole production/packing minutes", all(
        r["price_rm"] > 0 and r["material_cost_rm"] >= 0 and r["packaging_cost_rm"] >= 0 and whole(r["minutes_per_unit"]) and r["minutes_per_unit"] > 0 for r in products.values()) and all(
        0 <= r["fee_percent"] <= 100 and r["fee_per_order_rm"] >= 0 and r["shipping_cost_per_order_rm"] >= 0 and whole(r["fulfilment_minutes_per_order"]) and r["fulfilment_minutes_per_order"] >= 0 for r in channels.values()))
    check("Plan assumption domains", assumptions["admin_hours_per_week"] >= 0 and 0 <= assumptions["planned_margin_percent"] <= 100 and assumptions["target_hourly_rate_rm"] >= 0)

    message_text = (ROOT / "data/demo/messages.md").read_text(encoding="utf-8")
    parts = re.split(r"^## (\d{4}-\d{2}-\d{2}) - ([A-Za-z]+)\s*$", message_text, flags=re.M)
    dates = parts[1::3]
    blocks = dict(zip(dates, parts[3::3]))
    messages = {}
    listed = []
    file_dates = {}
    for day, weekday, body in zip(parts[1::3], parts[2::3], parts[3::3]):
        check(f"Nightly message {day}: weekday and single message", weekday == date.fromisoformat(day).strftime("%A") and len(re.findall(r"^- Message: (.+)$", body, re.M)) == 1)
        messages[day] = re.search(r"^- Message: (.+)$", body, re.M).group(1)
        line = re.search(r"^- Files: (.+)$", body, re.M).group(1)
        names = [] if line.startswith("none;") else [n.strip().rstrip(".") for n in line.split(";")]
        listed.extend(names)
        for name in names:
            file_dates[name] = day
    check("One ISO week, messages cover Monday-Sunday exactly", dates == DAYS and START.isocalendar()[:2] == (2026, 41), ", ".join(dates))
    actual_files = sorted(p.name for p in INBOX.iterdir() if p.is_file())
    check("Every inbox file listed exactly once and every listed basename exists", sorted(listed) == actual_files and len(listed) == len(set(listed)), f"{len(actual_files)} inbox files")
    check("No nested or unaccounted inbox sources", all(p.is_file() for p in INBOX.iterdir()))
    check("Synthetic fixture explicitly declared; Malaysia-time week", "All people, orders and suppliers in this fixture are fictional" in message_text and "No real personal or banking data" in message_text and "Malaysia time" in message_text)

    csv_paths = list(INBOX.glob("*.csv"))
    check("Bank statement is CSV, not a photo", len(csv_paths) == 1 and "SYNTHETIC" in csv_paths[0].name and all(p.suffix == ".csv" for p in INBOX.glob("*bank*")))
    with csv_paths[0].open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        csv_rows = list(reader)
        check("CSV exact schema", reader.fieldnames == SCHEMAS["bank_lines"])
    check("CSV money spelling: two decimals, positive", all(re.fullmatch(r"\d+\.\d{2}", r["amount_rm"]) and sen(r["amount_rm"]) > 0 for r in csv_rows))
    bank = normalise(csv_rows)
    check("CSV equals expected bank_lines, all fields and row order", bank == bank_expected, f"{len(bank)} lines compared")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=SCHEMAS["bank_lines"], lineterminator="\n")
    writer.writeheader()
    for row in bank_expected:
        writer.writerow({**row, "amount_rm": rm(row["amount_rm"])[2:]})
    replay = list(csv.DictReader(io.StringIO(buffer.getvalue(), newline="")))
    check("Bank CSV round-trip from workbook is lossless", replay == csv_rows and normalise(replay) == bank_expected)
    references = [r["bank_reference"] for r in bank]
    check("Bank references all present and globally unique", len(references) == len(set(references)) and all(references))
    check("Bank statement arrives only on Sunday", file_dates[csv_paths[0].name] == DAYS[-1])

    # Deliberately ignore manifest transactions, bank_lines, and correction outputs.
    raw = normalise(json.loads((HERE / "render_manifest.json").read_text(encoding="utf-8"), parse_float=Decimal)["raw_documents"])
    check("Raw intake uses transaction schema", all(list(r) == SCHEMAS["transactions"] for r in raw))
    check("Raw intake has no bank assignments or settled statuses", all(r["bank_reference"] is None and r["reconciliation_status"] in (None, "needs_review") for r in raw))
    for label, rows, key, pattern in (("transactions", tx, "txn_id", r"T\d{4}"), ("raw intake", raw, "txn_id", r"T\d{4}"), ("hours", hours, "entry_id", r"H\d{4}")):
        ids = [r[key] for r in rows]
        check(f"Unique valid IDs: {label}", len(ids) == len(set(ids)) and all(re.fullmatch(pattern, i) for i in ids))
    for label, rows in (("transactions", tx), ("raw documents", raw), ("bank lines", bank), ("hours", hours)):
        check(f"ISO dates within specified week: {label}", all(isinstance(r["date"], str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["date"]) and r["date"] in DAYS for r in rows))
    check("Transactions and hours span all seven dates", {r["date"] for r in tx} == set(DAYS) and {r["date"] for r in hours} == set(DAYS))
    check("Payment enum exact on raw and expected rows", all(r["payment_method"] in {"cash", "bank_transfer"} for r in raw + tx))
    check("Category/type rule and required transaction fields", all(r["category"] in CATEGORIES and r["type"] == ("income" if r["category"] == "sales" else "expense") and r["date"] and r["payment_method"] and (r["amount_rm"] is None or r["amount_rm"] > 0) for r in raw + tx))
    check("Bank type/positive amount", all(r["type"] in {"income", "expense"} and r["amount_rm"] > 0 for r in bank))
    check("Reconciliation status enum exact", all(r["reconciliation_status"] in STATUSES for r in tx))
    check("Blank amount only for unreadable intake", all(r["reconciliation_status"] == "needs_review" and "unreadable" in (r["notes"] or "").lower() for r in raw + tx if r["amount_rm"] is None))
    check("No n/a or empty-string stand-ins", all(v not in ("n/a", "N/A", "") for row in raw + tx + hours for v in row.values()))
    sales = [r for r in tx if r["category"] == "sales"]
    check("One product per order, valid quantity and channel", all(r["product_id"] in products and whole(r["quantity"]) and r["quantity"] > 0 and r["channel"] in channels for r in raw + tx if r["category"] == "sales"))
    check("Expense-only fields are empty", all(r["product_id"] is None and r["quantity"] is None and r["channel"] is None for r in raw + tx if r["type"] == "expense"))
    check("No sales source split into multiple product rows", len({(r["source_file"], r["counterparty"]) for r in sales}) == len(sales))

    unresolved_sources = []
    rendered = {}
    for row in raw + tx:
        source = row["source_file"]
        if source is None:
            if not (row["bank_reference"] and row["reconciliation_status"] == "unmatched"):
                unresolved_sources.append(row["txn_id"])
            continue
        path = PurePosixPath(source)
        expected_parent = f"receipts/{row['date'][:7]}"
        if str(path.parent) != expected_parent or ".." in path.parts or "\\" in source:
            unresolved_sources.append(row["txn_id"])
        match = re.fullmatch(r"message_(\d{4}-\d{2}-\d{2})\.txt", path.name)
        if match:
            if match[1] != row["date"] or match[1] not in messages:
                unresolved_sources.append(row["txn_id"])
        elif not (INBOX / path.name).is_file() or file_dates.get(path.name) != row["date"]:
            unresolved_sources.append(row["txn_id"])
    for row in raw:
        if row["source_file"].endswith(".png"):
            rendered[PurePosixPath(row["source_file"]).name] = row
    check("Every source basename/file or dated message exists", not unresolved_sources, f"Unresolved rows: {unresolved_sources}; message paths resolve to dated sections, not pre-existing workspace files")
    check("Every rendered image has exactly one raw source row", set(rendered) == {p.name for p in INBOX.glob("*.png")} and len(rendered) == sum(r["source_file"].endswith(".png") for r in raw))

    cash_observed = []
    for day, text in messages.items():
        for name, qty, pid, product_name, amount in re.findall(r"([A-Z][a-z]+) bought (one|\d+) (P\d{2}) ([a-z ]+?) for RM(\d+\.\d{2})", text):
            cash_observed.append((day, name, pid, 1 if qty == "one" else int(qty), sen(amount), "bazaar", "cash", f"receipts/{day[:7]}/message_{day}.txt", product_name))
    cash_rows = [r for r in sales if r["payment_method"] == "cash"]
    cash_actual = [(r["date"], r["counterparty"], r["product_id"], r["quantity"], r["amount_rm"], r["channel"], r["payment_method"], r["source_file"], products[r["product_id"]]["name"].lower()) for r in cash_rows]
    check("Cash source exact: every declared order once, no extra orders", Counter(cash_observed) == Counter(cash_actual) and len(cash_observed) == 4 and "Cash orders, all separate" in messages[DAYS[5]] and "All four orders were at the bazaar" in messages[DAYS[5]], f"{len(cash_rows)} separate cash orders; total {rm(sum(r['amount_rm'] for r in cash_rows))}")
    check("Cash orders have no invented references", all(r["reference"] is None and r["bank_reference"] is None and r["reconciliation_status"] == "cash_declared" for r in cash_rows))

    # The hashes bind the recorded manual observations to these exact bytes.
    for name, (sha, observation) in {**ORDER_VISUALS, **RECEIPT_VISUALS}.items():
        row = rendered[name]
        if name in ORDER_VISUALS:
            fields = ("date", "counterparty", "product_id", "quantity", "amount_rm", "channel", "reference")
        else:
            fields = ("date", "counterparty", "amount_rm", "payment_method", "reference")
        check(f"Manual rendering evidence current: {name}", digest(INBOX / name) == sha and tuple(row[k] for k in fields) == observation,
              "Hash matches visually inspected bytes and raw metadata matches recorded visible fields; not OCR")
    check("Rendered order payment labels", all(rendered[name]["payment_method"] == "bank_transfer" for name in ORDER_VISUALS))
    check("Rendered inventory covered by manual review or byte-identical duplicate", set(rendered) == set(ORDER_VISUALS) | set(RECEIPT_VISUALS) | {"receipt_beads_copy.png"})
    broken_images = []
    for path in INBOX.glob("*.png"):
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                image.load()
                if image.format != "PNG" or min(image.size) <= 0:
                    broken_images.append(path.name)
        except Exception as exc:
            broken_images.append(f"{path.name}: {exc}")
    check("All PNG files decode completely", not broken_images, broken_images)
    hashes = defaultdict(list)
    for path in INBOX.glob("*.png"):
        hashes[digest(path)].append(path.name)
    duplicates = [sorted(names) for names in hashes.values() if len(names) > 1]
    check("Exactly the intended duplicate image bytes", duplicates == [["receipt_beads.png", "receipt_beads_copy.png"]], duplicates)

    rebuilt, decisions = reconcile(raw, bank)
    by_id = {r["txn_id"]: r for r in tx}
    raw_by_id = {r["txn_id"]: r for r in raw}
    check("Independent reconciliation produces exactly expected row IDs", {r["txn_id"] for r in rebuilt} == set(by_id))
    for row in rebuilt:
        actual = by_id[row["txn_id"]]
        differences = [k for k in SCHEMAS["transactions"] if k != "notes" and row[k] != actual[k]]
        check(f"Independent reconciliation: {row['txn_id']}", not differences,
              f"{row['reconciliation_status']}; bank {row['bank_reference'] or 'none'}; {rm(row['amount_rm'])}; differing fields: {differences}")
        kind, value = decisions[row["txn_id"]]
        notes = actual["notes"] or ""
        if kind == "duplicate":
            check("Duplicate receipt: original named, noncash, excluded and reviewed", value in notes and actual["payment_method"] == "bank_transfer" and not counted(actual) and actual["reconciliation_status"] in REVIEW and actual["bank_reference"] is None, f"{actual['txn_id']} duplicates {value}")
            original = raw_by_id[value]
            check("Duplicate receipt: date/type/amount/supplier/printed reference identical", all(raw_by_id[actual["txn_id"]][k] == original[k] for k in ("date", "type", "amount_rm", "counterparty", "reference")))
        if kind == "reference" and value != row["amount_rm"]:
            check("Mismatch: same printed reference, bank amount used, both notes amounts", actual["reference"] == actual["bank_reference"] and rm(value) in notes and rm(row["amount_rm"]) in notes and actual["reconciliation_status"] == "needs_review" and counted(actual), f"{actual['txn_id']}: document {rm(value)}, bank {rm(row['amount_rm'])}")
        if kind == "intake":
            check("Blurry receipt: intake flag overrides cash, blank amount, no totals, source retained", actual == raw_by_id[row["txn_id"]] and actual["amount_rm"] is None and not counted(actual) and actual["reconciliation_status"] == "needs_review" and (INBOX / PurePosixPath(actual["source_file"]).name).is_file(), f"{actual['txn_id']}; total not guessed")
        if kind == "amount" and row["reconciliation_status"] == "ambiguous_resolved":
            check(f"Ambiguity explained: {row['txn_id']}", len(value) >= 2 and actual["counterparty"] in notes and actual["bank_reference"] in notes and "candidate" in notes.lower(), f"Candidates: {', '.join(value)}")
        if kind == "leftover":
            check("Missing receipt: supplier clear, blank source, counted and reviewed", actual["type"] == "expense" and actual["category"] == "materials" and actual["source_file"] is None and counted(actual) and actual["reconciliation_status"] == "unmatched" and "no document" in notes.lower() and "Demo Bead Nook" in actual["description"] and "bead materials" in actual["description"].lower(), f"{actual['txn_id']}: {actual['description']}; {rm(actual['amount_rm'])}")
            check("Missing receipt: no raw document or image evidence for bank reference/date", all(r["reference"] != value for r in raw) and not any(r["type"] == "expense" and r["date"] == actual["date"] for r in raw), "Sunday message acknowledges absence, rather than supplying an expense receipt")
    review_ids = {r["txn_id"] for r in tx if r["reconciliation_status"] in REVIEW}
    check("Exact review membership for all planted problem rows", review_ids == {r["txn_id"] for r in rebuilt if r["reconciliation_status"] in REVIEW} == {"T0004", "T0012", "T0019", "T0020"}, ", ".join(sorted(review_ids)))
    EVIDENCE.append("Review entries: " + "; ".join(f"{tid} {by_id[tid]['reconciliation_status']} - {by_id[tid]['notes']}" for tid in sorted(review_ids)))
    check("Exactly one duplicate, blurry, mismatch and missing receipt", sum(k == "duplicate" for k, v in decisions.values()) == 1 and sum(k == "intake" for k, v in decisions.values()) == 1 and sum(k == "leftover" for k, v in decisions.values()) == 1 and sum(k == "reference" and v != by_id[tid]["amount_rm"] for tid, (k, v) in decisions.items()) == 1)
    used = [r["bank_reference"] for r in tx if r["bank_reference"]]
    check("Every bank assignment exists, every line used exactly once", Counter(used) == Counter(references))
    for b in bank:
        users = [r for r in tx if r["bank_reference"] == b["bank_reference"]]
        check(f"Bank assignment: {b['bank_reference']}", len(users) == 1 and users[0]["type"] == b["type"] and users[0]["amount_rm"] == b["amount_rm"], ", ".join(r["txn_id"] for r in users))
    no_ref_sales = [r for r in raw if r["type"] == "income" and r["payment_method"] == "bank_transfer" and r["reference"] is None]
    check("Same-amount no-reference transfers really are ambiguous", len(no_ref_sales) == 2 and all(len(candidates(r, bank)) >= 2 for r in no_ref_sales) and no_ref_sales[0]["amount_rm"] == no_ref_sales[1]["amount_rm"] and abs((date.fromisoformat(no_ref_sales[0]["date"]) - date.fromisoformat(no_ref_sales[1]["date"])).days) <= 1)
    check("All reference-bearing transfers assigned to their printed reference", all(by_id[r["txn_id"]]["bank_reference"] == r["reference"] for r in raw if r["payment_method"] == "bank_transfer" and r["reference"] and decisions[r["txn_id"]][0] != "duplicate"))
    for left in no_ref_sales:
        for right in no_ref_sales:
            if left["txn_id"] < right["txn_id"]:
                check("Ambiguous pair uses different justified bank assignments", by_id[left["txn_id"]]["bank_reference"] != by_id[right["txn_id"]]["bank_reference"] and all(by_id[r["txn_id"]]["reconciliation_status"] == "ambiguous_resolved" for r in (left, right)))

    corrections = []
    events = []
    other_stated = []
    for day, text in messages.items():
        match = re.search(r"I timed myself today, keychains take (\d+) minutes not (\d+)", text)
        if match:
            corrections.append({"changed_at": day, "product_id": "P01", "old_value": int(match[2]), "new_value": int(match[1]), "reason": match[0], "source": f"message.{day}"})
        event = re.search(r"campus bazaar today from (\d{1,2}:\d{2}[ap]m) to (\d{1,2}:\d{2}[ap]m)", text)
        if event:
            times = [datetime.strptime(t, "%I:%M%p") for t in event.groups()]
            minutes = (times[1].hour * 60 + times[1].minute) - (times[0].hour * 60 + times[0].minute)
            events.append((day, minutes))
        remainder = text.replace(match[0], "") if match else text
        if event:
            remainder = remainder.replace(event[0], "").replace("eight hours in total", "")
        if re.search(r"\b(hours?|minutes?|mins?)\b|\d{1,2}:\d{2}[ap]m", remainder, re.I):
            other_stated.append(day)
    check("One midweek production correction from actual message", len(corrections) == 1 and corrections[0]["changed_at"] == "2026-10-07" and corrections[0]["old_value"] == 20 and corrections[0]["new_value"] == 15)
    correction = corrections[0]
    check("Baseline preserved, correction not pre-applied", not plan["change_log"] and products["P01"]["minutes_per_unit"] == correction["old_value"])
    replay_detail = blocks[correction["changed_at"]]
    check("Correction reply, field, old/new/date/source agree", f'"{correction["reason"]}"' in replay_detail and "products.P01.minutes_per_unit" in replay_detail and f'old_value: {correction["old_value"]}' in replay_detail and f'new_value: {correction["new_value"]}' in replay_detail and f'changed_at: {correction["changed_at"]}' in replay_detail and correction["source"] in replay_detail and "one correction, not two" in replay_detail)
    correction_sales = [r for r in sales if r["product_id"] == correction["product_id"] and counted(r)]
    before_units = sum(r["quantity"] for r in correction_sales if r["date"] < correction["changed_at"])
    after_units = sum(r["quantity"] for r in correction_sales if r["date"] >= correction["changed_at"])
    check("Corrected product sold before, on and after correction", before_units > 0 and after_units > 0 and any(r["date"] == correction["changed_at"] for r in correction_sales) and any(r["date"] > correction["changed_at"] for r in correction_sales), f"{before_units} units before; {after_units} units from October 7")
    check("One nightly event, stated duration unambiguous", events == [("2026-10-10", 480)] and "eight hours in total" in messages[DAYS[5]], "Saturday 10:00am-6:00pm = 480 minutes")
    check("Stated hours are for events only", not other_stated and all(r["activity"] == "event" for r in hours if r["source"] == "stated"), f"Other duration-bearing nightly messages: {other_stated}")
    rebuilt_hours = make_hours(rebuilt, products, channels, assumptions, correction, events)
    hours_fields = SCHEMAS["hours"][1:]
    actual_hours = [tuple(r[k] for k in hours_fields) for r in hours]
    check("Exact hours multiset: grouping, quantity, minutes, source and reference", Counter(actual_hours) == Counter(rebuilt_hours), f"{len(actual_hours)} actual / {len(rebuilt_hours)} independently derived lines; IDs not used to manufacture grouping")
    for row in hours:
        value = tuple(row[k] for k in hours_fields)
        check(f"Hours line {row['entry_id']}", value in rebuilt_hours and whole(row["minutes"]) and row["minutes"] >= 0,
              f"{row['date']}; {row['activity']}; {row['product_id'] or 'shared'}; quantity {row['quantity']}; {row['minutes']} minutes; {row['source']}; {row['assumption_ref']}")
    group_keys = [(r["date"], r["activity"], r["product_id"], r["assumption_ref"]) for r in hours]
    check("No duplicate hours groups/events/admin", len(group_keys) == len(set(group_keys)))
    check("Hours person and activity/source enums", all(r["person"] == "person_1" and r["activity"] in {"production", "fulfilment", "event", "admin"} and r["source"] in {"estimate", "corrected", "stated"} for r in hours))
    check("Hours quantities/empties and zero-fulfilment omission", all((r["product_id"] in products and whole(r["quantity"]) and r["quantity"] > 0) if r["activity"] in {"production", "fulfilment"} else (r["product_id"] is None and r["quantity"] is None) for r in hours) and all(r["minutes"] > 0 for r in hours if r["activity"] == "fulfilment"))
    check("Approved correction labels: estimate before October 7, corrected from October 7", all(r["source"] == ("corrected" if r["date"] >= correction["changed_at"] else "estimate") for r in hours if r["activity"] == "production" and r["product_id"] == "P01"))
    check("Only corrected field receives corrected label", all(r["assumption_ref"] == "products.P01.minutes_per_unit" and r["date"] >= correction["changed_at"] for r in hours if r["source"] == "corrected"))
    check("Admin closes week on Sunday and event uses message reference", [r["date"] for r in hours if r["activity"] == "admin"] == [DAYS[-1]] and all(r["source"] == "stated" and r["assumption_ref"] == f"message.{r['date']}" and r["date"] in messages for r in hours if r["activity"] == "event"))
    # Rebuild a second time in memory; no event insertion or workbook write occurs.
    check("Independent hours reconstruction is repeatable", rebuilt_hours == make_hours(rebuilt, products, channels, assumptions, correction, events))

    totals = {c: sum(r["amount_rm"] for r in tx if counted(r) and r["category"] == c) for c in CATEGORIES}
    independently_totalled = {c: sum(r["amount_rm"] for r in rebuilt if counted(r) and r["category"] == c) for c in CATEGORIES}
    check("All category totals agree with independent reconciliation", totals == independently_totalled, "; ".join(f"{c} {rm(v)}" for c, v in totals.items()))
    take_home = totals["sales"] - sum(totals[c] for c in CATEGORIES if c != "sales")
    week_minutes = sum(r["minutes"] for r in hours)
    check("Week minutes agree with independent hours", week_minutes == sum(r[5] for r in rebuilt_hours), f"{week_minutes} minutes")
    shared = sum(r["minutes"] for r in hours if r["activity"] in {"event", "admin"})
    direct = sum(r["minutes"] for r in hours if r["activity"] in {"production", "fulfilment"})
    check("Shared hours not allocated to products", shared + direct == week_minutes and all(r["product_id"] is None for r in hours if r["activity"] in {"event", "admin"}), f"direct {direct}; shared {shared}")
    EVIDENCE.append("Category totals: " + "; ".join(f"{c} {rm(v)}" for c, v in totals.items()) + ".")
    display_hours = rounded(week_minutes, 6)
    EVIDENCE.append(f"Take home {rm(take_home)}; {week_minutes} minutes ({display_hours // 10}.{display_hours % 10} displayed hours); hourly rate {rate(take_home, week_minutes)}. Unknown thread cost remains excluded, so take home is provisional.")
    profit_rows = []
    for pid, product in products.items():
        orders = [r for r in sales if counted(r) and r["product_id"] == pid]
        units = sum(r["quantity"] for r in orders)
        revenue = sum(r["amount_rm"] for r in orders)
        unit_costs = units * (product["material_cost_rm"] + product["packaging_cost_rm"])
        channel_costs = sum(fee(r["amount_rm"], channels[r["channel"]]["fee_percent"]) + channels[r["channel"]]["fee_per_order_rm"] + channels[r["channel"]]["shipping_cost_per_order_rm"] for r in orders)
        profit = revenue - unit_costs - channel_costs
        minutes = sum(r["minutes"] for r in hours if r["product_id"] == pid and r["activity"] in {"production", "fulfilment"})
        profit_rows.append((pid, units, profit))
        EVIDENCE.append(f"{pid} {product['name']}: {units} units; revenue {rm(revenue)}; unit costs {rm(unit_costs)}; channel costs {rm(channel_costs)}; profit {rm(profit)}; {minutes} direct minutes; profit per hour {rate(profit, minutes)}.")
    max_units = max(p[1] for p in profit_rows)
    leaders = [p for p in profit_rows if p[1] == max_units]
    check("Planted bestseller has strictly negative plan-based profit", len(leaders) == 1 and leaders[0][2] < 0, "; ".join(f"{p}: {u} units, profit {rm(v)}" for p, u, v in profit_rows))
    check("Two bases remain separate: product profit not forced to equal take home", sum(p[2] for p in profit_rows) != take_home, f"Product profit sum {rm(sum(p[2] for p in profit_rows))}; take home {rm(take_home)}")
    known_materials = [r for r in tx if counted(r) and r["category"] == "materials"]
    biggest = max(r["amount_rm"] for r in known_materials)
    check("Materials restock size: largest known purchase below take home and sales", 0 < biggest < take_home and biggest < totals["sales"], f"Largest {rm(biggest)}; total known materials {rm(totals['materials'])}; take home {rm(take_home)}. Operational proxy, not a specified numeric threshold.")
    check("Materials wording supports restock/top-up rather than bulk capital stock", all(any(word in r["description"].lower() for word in ("restock", "top-up")) for r in known_materials))
    shipped = [r for r in sales if counted(r) and channels[r["channel"]]["shipping_cost_per_order_rm"] > 0]
    expected_shipping = sum(channels[r["channel"]]["shipping_cost_per_order_rm"] for r in shipped)
    check("Courier expense is not a sale and covers nine parcel labels once", len(shipped) == 9 and totals["shipping"] == expected_shipping and "nine parcel labels" in messages[DAYS[4]] and "not another sale" in messages[DAYS[4]], f"{len(shipped)} shipped orders; {rm(expected_shipping)}")
    if totals["sales"]:
        margin = rounded(take_home * 100, totals["sales"])
        EVIDENCE.append(f"Reality margin {margin}% versus planned {assumptions['planned_margin_percent']}%; hourly rate {rate(take_home, week_minutes)} versus target {rm(assumptions['target_hourly_rate_rm'])}.")
    EVIDENCE.append("Expected Auditor direction, inferred rather than compared to a separate ruling: retain all four review entries; request the missing/clearer receipts and resolve Zahra's underpayment; treat take home as provisional; challenge growth in the loss-making keychain channel and below-target time return.")
    EVIDENCE.append(f"Correction replay: append one products.{correction['product_id']}.minutes_per_unit change from {correction['old_value']} to {correction['new_value']} dated {correction['changed_at']}, with the student's exact reason and {correction['source']} source; update the working plan only. Baseline input remains unchanged. Before correction: {before_units} units x {correction['old_value']} = {before_units * correction['old_value']} minutes; on/after: {after_units} units x {correction['new_value']} = {after_units * correction['new_value']} minutes.")
    EVIDENCE.append("Manual visual review on 2026-10-10: all ten order images and four distinct receipt images were inspected; the additional bead copy is checked by byte identity. Each inspected image visibly says SYNTHETIC DEMO and NOT A REAL ORDER/RECEIPT. Visible source dates, amounts, identities, products and references agreed with the recorded observations at inspection. Current applicability requires the corresponding hash/metadata checks to pass.")
    EVIDENCE.append("Blurry receipt: date 2026-10-08, Demo Thread Stop, Thread refill and Cash remain readable; the whole amount band is obscured and no numeric total is legible elsewhere. No amount was inferred or recovered.")
    EVIDENCE.append("Mismatch visual: Zahra's order prints RM5.00 and DEMO-IN-010; CSV has RM4.50 on that same reference. No-reference visuals: Dana and Mira each print RM5.00 on 2026-10-05 and have no payment-reference field.")

    # Negative controls touch only in-memory copies, never source files.
    swapped = deepcopy(bank_expected)
    swapped[0]["bank_reference"], swapped[1]["bank_reference"] = swapped[1]["bank_reference"], swapped[0]["bank_reference"]
    check("Negative control: equal-amount bank reference swap detected", swapped != bank)
    altered = deepcopy(actual_hours)
    old = list(altered[0])
    old[5] += 1
    altered[0] = tuple(old)
    check("Negative control: one-minute hours error detected", Counter(altered) != Counter(rebuilt_hours))
    altered = deepcopy(actual_hours)
    old = list(altered[0])
    old[6] = "corrected"
    altered[0] = tuple(old)
    check("Negative control: incorrect pre-correction label detected", Counter(altered) != Counter(rebuilt_hours))
    check("Negative control: duplicate hours line detected", Counter(actual_hours + actual_hours[:1]) != Counter(rebuilt_hours))
    check("Negative control: counted-row exclusions distinguish zero from unknown", not counted({"reconciliation_status": "needs_review", "amount_rm": None}) and not counted({"reconciliation_status": "duplicate", "amount_rm": 1800}) and counted({"reconciliation_status": "unmatched", "amount_rm": 900}))
    after = {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in inputs}
    check("All permitted input bytes unchanged during validation", after == FINGERPRINTS)


def write_report():
    failed = [(name, detail) for status, name, detail in RESULTS if status == "FAIL"]
    lines = ["# Synthetic fixture rule check", "", f"- Result: {len(RESULTS) - len(failed)} passed; {len(failed)} failed. This is fixture validation, not an end-to-end application certification.",
             "- Scope: PLAN.md section 10; SYSTEM_DESIGN.md sections 2-4; demo plan, expected ledger, nightly messages, every inbox file, and raw_documents from render_manifest.json.",
             "- Independence: no independent calculator, fixture builder or renderer files read/imported; no expected manifest transactions, bank lines or computed correction used as an oracle. Reconciliation and hours were derived anew; money calculations use integer sen and exact rational rates.",
             "- Writes: only check_rules.py and rule_check.md in data/answer_key/.expected_ledger.ref. No input, git, file name or directory is modified, renamed or deleted.",
             '- Reproduce from any working directory: `"C:/Users/user/.workbuddy-ai/binaries/python/envs/lembur/Scripts/python.exe" -B "C:/Users/user/Documents/Hackerdorm/Lembur/data/answer_key/.expected_ledger.ref/check_rules.py"`.',
             "- Exit code: 0 when all implemented checks pass; 1 for a failed check or incomplete validation. Re-running refreshes only this report.", "", "## Failures", ""]
    lines += [f"- {name}: {detail}" for name, detail in failed] or ["- None detected in the checks executed."]
    lines += ["", "## Findings", ""] + [f"- {text}" for text in EVIDENCE]
    lines += ["", "## Limitations and explicit interpretations", "",
              "- Visual OCR is not automated. PNG decoding and SHA-256 checks cannot read text or prove unreadability. Recorded manual observations cover the inspected bytes only; any changed image fails its evidence check and requires fresh visual inspection.",
              "- The manifest is source fixture metadata, not independently extracted image text. Only raw_documents is used to reconstruct intake; manual observations reduce, but do not eliminate, shared-authoring-error risk.",
              "- Missing-receipt absence is checked against the complete supplied inbox and raw-document inventory. The Sunday message acknowledges the missing receipt; it is not treated as a replacement receipt. No claim is made about files outside this supplied scope.",
              "- Filed receipts/... paths are replay destinations. Each basename is checked against inbox or the exact dated message section; physical workspace filing and saved message text files were not created or tested.",
              "- Sharon's approved interpretation is applied: pre-correction production source is estimate; P01 source is corrected for dates on/after 2026-10-07. The literal design sentence about values coming from change_log could otherwise label old_value-backed dates differently.",
              "- The baseline plan intentionally has no change_log row. The correction is reconstructed from Wednesday's message in memory. Append-only history and corrected working-plan persistence are runtime behaviors, not proved by this baseline fixture.",
              "- Restock size has no numeric acceptance threshold in PLAN. The check uses largest known materials purchase below both weekly sales and take home, plus restock/top-up wording. The unreadable thread amount remains unknown; no claim is made that its true cost is modest.",
              "- All channel percentage/per-order fees in this fixture are zero. Half-away rounding and per-order fee rounding are checked with separate in-memory arithmetic controls; the fixture itself does not exercise nonzero fees.",
              "- Message parsing is deliberately limited to this fixture's wording. Stated-duration scanning examines nightly Message lines, not replay instructions; Wednesday's minutes-per-unit correction is not an extra stated-hours entry.",
              "- Category totals, take home, rates, product profits and ruling direction are derived here. answer_key.md, other calculators, payslip output and the actual Auditor ruling were outside the supplied comparison scope and were not read or compared.",
              "- Review membership is checked from exact expected-ledger statuses and explanatory notes; no runtime review-list artifact is present in the supplied inputs.",
              "- Actual intake, reconciliation rerun/idempotence, late-document arrival, Sunday-only bank-row creation, saved filing, unclear-event handling and approval behavior are not executed. The in-memory reconstruction and repeatability checks do not certify those application paths.",
              "- Dates are naive ISO strings interpreted in Malaysia time, as stated by the messages. No timezone conversion or real banking activity is implied. All persons, suppliers and transactions are synthetic."]
    lines += ["", "## Reproducible checks", ""]
    lines += [f"- {status} - {name}" + (f": {detail}" if detail else "") for status, name, detail in RESULTS]
    lines += ["", "## Input fingerprints", ""]
    lines += [f"- `{name}`: `{sha}`" for name, sha in sorted(FINGERPRINTS.items())]
    (HERE / "rule_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(RESULTS) - len(failed)} passed; {len(failed)} failed. Report: {HERE / 'rule_check.md'}")
    for name, detail in failed:
        print(f"FAIL: {name}: {detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        validate()
    except Exception as exc:
        check("Validation incomplete", False, f"{type(exc).__name__}: {exc}")
    sys.exit(write_report())
