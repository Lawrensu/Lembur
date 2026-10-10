"""compare_outputs.py -- Compare a real Night Shift workspace against the golden answer key.

Pass condition (PLAN section 10): the run's outputs match the answer key
exactly -- statuses, minutes, and money to the sen.  A mismatch is a bug
to fix, not something to explain away.

Three layers of comparison:
  1. Ledger sheets -- transactions, bank_lines, hours compared row by row.
  2. Derived figures -- category totals, take home, hourly rate, product
     profit, review IDs -- recalculated from the workspace ledger and
     compared against calculation.json.
  3. Plan state -- the workspace plan CSV files must have the correction applied
     (P01 minutes_per_unit = 15, one change_log row).

Usage:
    python compare_outputs.py
    python compare_outputs.py --workspace path/to/workspace
    python compare_outputs.py --workspace workspace --answer-key-dir data/answer_key

Files are CSV, one per sheet, named <book>_<sheet>.csv (SYSTEM_DESIGN section 3.1):
    workspace/ledger_*.csv, workspace/plan/plan_*.csv, data/answer_key/ledger_*.csv

Not compared, because an agent writes them in its own words: the notes and
description columns of transactions. Hours lines are matched by date, activity,
product and assumption reference, never by entry_id (PLAN section 10).

Outputs:
    Console           -- human-readable PASS/FAIL summary
    latest_report.json -- structured report for automation
    run_report.md      -- markdown report for human review
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORKSPACE = ROOT / "workspace"
DEFAULT_ANSWER_KEY = ROOT / "data" / "answer_key"

# ---------------------------------------------------------------------------
# Column definitions (must match SYSTEM_DESIGN section 3.3)
# ---------------------------------------------------------------------------

TX_COLS = (
    "txn_id date type category description product_id quantity amount_rm "
    "channel payment_method counterparty reference source_file "
    "reconciliation_status bank_reference notes"
).split()
BANK_COLS = "date description type amount_rm bank_reference".split()
HOURS_COLS = "entry_id date person activity product_id quantity minutes source assumption_ref".split()

PLAN_TX_COLS = "txn_id date type category description product_id quantity amount_rm channel payment_method counterparty reference source_file reconciliation_status bank_reference notes".split()
PLAN_BANK_COLS = "date description type amount_rm bank_reference".split()
PLAN_HOURS_COLS = "entry_id date person activity product_id quantity minutes source assumption_ref".split()

# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def to_sen(v):
    """Convert any money value to integer sen, or None if empty."""
    if v is None or v == "":
        return None
    d = Decimal(str(v)) * 100
    # Allow values that are exact to the sen (no fractional sen)
    return int(d.to_integral_value(rounding=ROUND_HALF_UP))


def norm_str(v):
    """Normalise a cell to a string or None."""
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def norm_date(v):
    """Normalise to YYYY-MM-DD string or None."""
    if v is None or v == "":
        return None
    if isinstance(v, (date, datetime)):
        return v.strftime("%Y-%m-%d")
    return str(v)


def norm_int(v):
    """Normalise to int or None."""
    if v is None or v == "":
        return None
    return int(Decimal(str(v)))


def display(value, places=2):
    """Round to the given decimal places using ROUND_HALF_UP, return string."""
    q = Decimal(1).scaleb(-places)
    return str(Decimal(value).quantize(q, rounding=ROUND_HALF_UP))


def money_display(sen_value):
    """Convert sen to a display string like 'RM2.53'."""
    if sen_value is None:
        return "(empty)"
    return "RM" + display(Decimal(sen_value) / 100)


def norm_row(row_dict, columns):
    """Apply the right normaliser to each field based on column name."""
    result = {}
    for col in columns:
        v = row_dict.get(col)
        if col == "amount_rm":
            result[col] = to_sen(v)
        elif col == "quantity" or col == "minutes":
            result[col] = norm_int(v)
        elif col == "date":
            result[col] = norm_date(v)
        else:
            result[col] = norm_str(v)
    return result


# ---------------------------------------------------------------------------
# CSV reader
# ---------------------------------------------------------------------------

def read_rows(path):
    """Read one CSV file into a list of rows, header first. None when it is missing."""
    if not Path(path).is_file():
        return None
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return [row for row in csv.reader(handle)]


def read_sheet(base, sheet_name, columns):
    """Read <base>_<sheet_name>.csv into a list of normalised dicts keyed by column name."""
    rows = read_rows(f"{base}_{sheet_name}.csv")
    if rows is None:
        return None  # file missing entirely
    if not rows:
        return []
    headers = [str(h).strip() for h in rows[0]]
    if headers != list(columns):
        return None  # column mismatch
    result = []
    for raw in rows[1:]:
        if all(c is None or c == "" for c in raw):
            continue  # skip blank rows
        d = dict(zip(columns, raw))
        result.append(norm_row(d, columns))
    return result


def read_ledger(path):
    """Read the three ledger CSV files that share the base path into a dict."""
    return {
        "transactions": read_sheet(path, "transactions", TX_COLS),
        "bank_lines": read_sheet(path, "bank_lines", BANK_COLS),
        "hours": read_sheet(path, "hours", HOURS_COLS),
    }


def read_plan(path):
    """Read the four plan CSV files that share the base path into a dict."""
    sheets = {}
    for name, cols in [
        ("products", "product_id name price_rm material_cost_rm packaging_cost_rm minutes_per_unit".split()),
        ("channels", "channel fee_percent fee_per_order_rm shipping_cost_per_order_rm fulfilment_minutes_per_order".split()),
        ("assumptions", "admin_hours_per_week planned_margin_percent target_hourly_rate_rm".split()),
        ("change_log", "changed_at field old_value new_value reason source".split()),
    ]:
        rows = read_rows(f"{path}_{name}.csv")
        if rows is None:
            sheets[name] = None
            continue
        if not rows:
            sheets[name] = []
            continue
        headers = [str(h).strip() for h in rows[0]]
        result = []
        for raw in rows[1:]:
            if all(c is None or c == "" for c in raw):
                continue
            d = {}
            for i, col in enumerate(headers):
                val = raw[i] if i < len(raw) else None
                if col in ("price_rm", "material_cost_rm", "packaging_cost_rm",
                           "fee_per_order_rm", "shipping_cost_per_order_rm"):
                    d[col] = to_sen(val)
                elif col in ("old_value", "new_value"):
                    # Generic plan values -- could be minutes, hours, or money.
                    # Normalise to int when whole, float when fractional, string otherwise.
                    if val is None or val == "":
                        d[col] = None
                    else:
                        try:
                            num = Decimal(str(val))
                            d[col] = int(num) if num == num.to_integral_value() else float(num)
                        except Exception:
                            d[col] = str(val).strip()
                elif col in ("minutes_per_unit", "fulfilment_minutes_per_order",
                             "admin_hours_per_week"):
                    d[col] = norm_int(val)
                elif col in ("fee_percent", "planned_margin_percent",
                             "target_hourly_rate_rm"):
                    d[col] = norm_str(val)
                elif col == "changed_at":
                    d[col] = norm_date(val)
                else:
                    d[col] = norm_str(val)
            result.append(d)
        sheets[name] = result
    return sheets


# ---------------------------------------------------------------------------
# Layer 1: Ledger sheet comparison
# ---------------------------------------------------------------------------

FREE_TEXT = {"transactions": ("notes", "description")}


def keyed_hours(rows):
    """Key hours lines by date, activity, product and reference, never by entry_id."""
    keyed = []
    for row in rows:
        line = {k: v for k, v in row.items() if k != "entry_id"}
        line["_key"] = "|".join(str(row.get(k) or "") for k in
                                ("date", "activity", "product_id", "assumption_ref"))
        keyed.append(line)
    return keyed


def compare_rows(expected_rows, actual_rows, id_col, sheet_name, ignore=()):
    """Compare two lists of rows by their ID column. Return a diff dict."""
    exp_by_id = {r[id_col]: r for r in expected_rows} if id_col else {}
    act_by_id = {r[id_col]: r for r in actual_rows} if id_col else {}

    if not id_col:
        # No ID column -- compare by position
        return _compare_by_position(expected_rows, actual_rows, sheet_name)

    missing = sorted(set(exp_by_id) - set(act_by_id))
    extra = sorted(set(act_by_id) - set(exp_by_id))
    field_diffs = []

    for rid in sorted(set(exp_by_id) & set(act_by_id)):
        exp = exp_by_id[rid]
        act = act_by_id[rid]
        for col in exp:
            if col == id_col or col in ignore:
                continue
            ev = exp.get(col)
            av = act.get(col)
            if ev != av:
                field_diffs.append({
                    "id": rid,
                    "field": col,
                    "expected": _fmt_value(ev),
                    "actual": _fmt_value(av),
                })

    return {
        "expected_count": len(expected_rows),
        "actual_count": len(actual_rows),
        "missing_ids": missing,
        "extra_ids": extra,
        "field_differences": field_diffs,
    }


def _compare_by_position(expected_rows, actual_rows, sheet_name):
    """Compare two lists of rows positionally (for bank_lines)."""
    # Use bank_reference as a fallback key if present
    id_col = "bank_reference"
    exp_by_id = {r[id_col]: r for r in expected_rows}
    act_by_id = {r[id_col]: r for r in actual_rows}

    missing = sorted(set(exp_by_id) - set(act_by_id))
    extra = sorted(set(act_by_id) - set(exp_by_id))
    field_diffs = []

    for rid in sorted(set(exp_by_id) & set(act_by_id)):
        exp = exp_by_id[rid]
        act = act_by_id[rid]
        for col in exp:
            if col == id_col:
                continue
            ev = exp.get(col)
            av = act.get(col)
            if ev != av:
                field_diffs.append({
                    "id": rid,
                    "field": col,
                    "expected": _fmt_value(ev),
                    "actual": _fmt_value(av),
                })

    return {
        "expected_count": len(expected_rows),
        "actual_count": len(actual_rows),
        "missing_ids": missing,
        "extra_ids": extra,
        "field_differences": field_diffs,
    }


def _fmt_value(v):
    if v is None:
        return "(empty)"
    return str(v)


# ---------------------------------------------------------------------------
# Layer 2: Derived figures recalculation
# ---------------------------------------------------------------------------

def recalculate(ledger, plan):
    """Recalculate all derived figures from the workspace ledger + plan.

    Implements the same rules as SYSTEM_DESIGN section 4.3 (numbers tool)
    and reads hours from the ledger's hours sheet (section 4.2 output).
    """
    txns = ledger["transactions"] or []
    hours = ledger["hours"] or []

    # Counted rows: status != "duplicate" and amount_rm is not None
    counted = [r for r in txns
               if r.get("reconciliation_status") != "duplicate"
               and r.get("amount_rm") is not None]

    # Category totals (in sen)
    categories = {c: 0 for c in
                  ["sales", "materials", "packaging",
                   "platform_fees", "shipping", "other_expenses"]}
    for r in counted:
        cat = r.get("category")
        if cat in categories:
            categories[cat] += r["amount_rm"]

    take_home = categories["sales"] - sum(v for k, v in categories.items() if k != "sales")

    # Hours: sum minutes
    total_minutes = sum(h.get("minutes", 0) or 0 for h in hours)

    # Activity breakdown
    activity_order = ["production", "fulfilment", "event", "admin"]
    activity = {a: sum(h.get("minutes", 0) or 0 for h in hours if h.get("activity") == a)
                for a in activity_order}
    shared_minutes = activity["event"] + activity["admin"]

    # Display values
    if total_minutes > 0:
        hourly_rate = display(Decimal(take_home) * 60 / (total_minutes * 100))
    else:
        hourly_rate = None

    display_hours = display(Decimal(total_minutes) / 60, 1) if total_minutes else "0.0"

    if categories["sales"] > 0:
        margin = display(Decimal(take_home) * 100 / categories["sales"], 0)
    else:
        margin = None

    # Product profit
    products_plan = {p["product_id"]: p for p in (plan.get("products") or [])}
    channels_plan = {c["channel"]: c for c in (plan.get("channels") or [])}

    product_results = {}
    for pid, config in products_plan.items():
        sales = [r for r in counted
                 if r.get("category") == "sales" and r.get("product_id") == pid]
        revenue = sum(r["amount_rm"] for r in sales)
        qty = sum(r.get("quantity", 0) or 0 for r in sales)

        unit_cost = qty * ((config.get("material_cost_rm") or 0) +
                           (config.get("packaging_cost_rm") or 0))

        channel_cost = 0
        for r in sales:
            ch = channels_plan.get(r.get("channel"), {})
            fee_pct = Decimal(str(ch.get("fee_percent") or 0))
            fee = int((Decimal(r["amount_rm"]) * fee_pct / 100).quantize(
                Decimal(1), rounding=ROUND_HALF_UP))
            channel_cost += (fee +
                             (ch.get("fee_per_order_rm") or 0) +
                             (ch.get("shipping_cost_per_order_rm") or 0))

        profit = revenue - unit_cost - channel_cost
        direct = sum(h.get("minutes", 0) or 0 for h in hours
                     if h.get("product_id") == pid)

        if direct > 0:
            pph = display(Decimal(profit) * 60 / (direct * 100))
        else:
            pph = None

        product_results[pid] = {
            "units": qty,
            "revenue_sen": revenue,
            "unit_cost_sen": unit_cost,
            "channel_cost_sen": channel_cost,
            "profit_sen": profit,
            "direct_minutes": direct,
            "profit_per_hour": pph,
            "loses_money": profit < 0,
        }

    # Review IDs
    review_ids = sorted([r["txn_id"] for r in txns
                         if r.get("reconciliation_status") in
                         ("unmatched", "duplicate", "needs_review")])

    return {
        "category_sen": categories,
        "take_home_sen": take_home,
        "total_minutes": total_minutes,
        "display_hours": display_hours,
        "hourly_rate": hourly_rate,
        "margin_percent": margin,
        "activity_minutes": activity,
        "shared_minutes": shared_minutes,
        "products": product_results,
        "review_ids": review_ids,
    }


def compare_derived(expected, actual):
    """Compare two derived-figures dicts. Return a list of differences."""
    diffs = []

    def check(label, exp, act):
        if exp != act:
            diffs.append({
                "field": label,
                "expected": _fmt_value(exp),
                "actual": _fmt_value(act),
            })

    # Category totals
    for cat in sorted(set(expected["category_sen"]) | set(actual.get("category_sen", {}))):
        check(f"category_sen.{cat}",
              expected["category_sen"].get(cat),
              actual.get("category_sen", {}).get(cat))

    check("take_home_sen", expected["take_home_sen"], actual.get("take_home_sen"))
    check("total_minutes", expected["total_minutes"], actual.get("total_minutes"))
    check("display_hours", expected["display_hours"], actual.get("display_hours"))
    check("hourly_rate", expected["hourly_rate"], actual.get("hourly_rate"))
    check("margin_percent", expected["margin_percent"], actual.get("margin_percent"))

    # Activity minutes
    for act_name in ["production", "fulfilment", "event", "admin"]:
        check(f"activity_minutes.{act_name}",
              expected["activity_minutes"].get(act_name),
              actual.get("activity_minutes", {}).get(act_name))

    check("shared_minutes", expected["shared_minutes"], actual.get("shared_minutes"))

    # Products
    for pid in sorted(set(expected["products"]) | set(actual.get("products", {}))):
        ep = expected["products"].get(pid, {})
        ap = actual.get("products", {}).get(pid, {})
        for field in ["units", "revenue_sen", "unit_cost_sen", "channel_cost_sen",
                       "profit_sen", "direct_minutes", "profit_per_hour", "loses_money"]:
            check(f"{pid}.{field}", ep.get(field), ap.get(field))

    # Review IDs
    check("review_ids", expected["review_ids"], actual.get("review_ids"))

    return diffs


# ---------------------------------------------------------------------------
# Layer 3: Plan state check
# ---------------------------------------------------------------------------

def check_plan_state(workspace_plan):
    """Check that the workspace plan has the correction applied.

    Expected state (from answer_key.md):
      - products.P01.minutes_per_unit = 15
      - change_log has exactly 1 row:
          changed_at=2026-10-07, field=products.P01.minutes_per_unit,
          old_value=20, new_value=15,
          reason=I timed myself today, keychains take 15 minutes not 20,
          source=message.2026-10-07
    """
    diffs = []

    if workspace_plan is None:
        diffs.append({"field": "plan_file", "expected": "exists", "actual": "missing"})
        return diffs

    products = workspace_plan.get("products") or []
    p01 = next((p for p in products if p.get("product_id") == "P01"), None)
    if p01 is None:
        diffs.append({"field": "products.P01", "expected": "exists", "actual": "missing"})
    else:
        actual_min = p01.get("minutes_per_unit")
        if actual_min != 15:
            diffs.append({
                "field": "products.P01.minutes_per_unit",
                "expected": 15,
                "actual": actual_min,
            })

    change_log = workspace_plan.get("change_log") or []
    if len(change_log) != 1:
        diffs.append({
            "field": "change_log.row_count",
            "expected": 1,
            "actual": len(change_log),
        })
    elif change_log:
        row = change_log[0]
        expected_row = {
            "changed_at": "2026-10-07",
            "field": "products.P01.minutes_per_unit",
            "old_value": 20,
            "new_value": 15,
            "source": "message.2026-10-07",
        }
        for k, ev in expected_row.items():
            av = row.get(k)
            if av != ev:
                diffs.append({
                    "field": f"change_log.{k}",
                    "expected": str(ev),
                    "actual": str(av),
                })
        # Check reason contains the key phrase
        reason = row.get("reason") or ""
        if "15 minutes" not in reason.lower():
            diffs.append({
                "field": "change_log.reason",
                "expected": "contains '15 minutes'",
                "actual": reason,
            })

    return diffs


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(ledger_diffs, derived_diffs, plan_diffs,
                    expected_ledger, workspace_ledger):
    """Build the structured report."""
    total_diffs = 0
    for sheet_diff in ledger_diffs.values():
        total_diffs += len(sheet_diff.get("missing_ids", []))
        total_diffs += len(sheet_diff.get("extra_ids", []))
        total_diffs += len(sheet_diff.get("field_differences", []))
    total_diffs += len(derived_diffs)
    total_diffs += len(plan_diffs)

    # Sheet-level missing/extra
    sheet_errors = []
    for name, sd in ledger_diffs.items():
        if sd is None:
            sheet_errors.append(f"Sheet '{name}' missing or columns mismatched")
            total_diffs += 1
            continue
        if sd.get("missing_ids"):
            sheet_errors.append(f"{name}: missing {len(sd['missing_ids'])} rows")
        if sd.get("extra_ids"):
            sheet_errors.append(f"{name}: {len(sd['extra_ids'])} extra rows")

    status = "PASS" if total_diffs == 0 else "FAIL"

    report = {
        "status": status,
        "total_differences": total_diffs,
        "summary": {
            "ledger_differences": sum(
                len(sd.get("missing_ids", [])) + len(sd.get("extra_ids", [])) + len(sd.get("field_differences", []))
                for sd in ledger_diffs.values() if sd
            ),
            "derived_differences": len(derived_diffs),
            "plan_differences": len(plan_diffs),
            "sheet_errors": sheet_errors,
        },
        "ledger_comparison": {},
        "derived_comparison": derived_diffs,
        "plan_comparison": plan_diffs,
    }

    for name, sd in ledger_diffs.items():
        if sd is None:
            report["ledger_comparison"][name] = {"error": "sheet missing or column mismatch"}
        else:
            report["ledger_comparison"][name] = sd

    return report


def write_markdown(report, output_path):
    """Write a human-readable markdown report."""
    lines = []
    lines.append("# Test harness report")
    lines.append("")
    status = report["status"]
    icon = "PASS" if status == "PASS" else "FAIL"
    lines.append(f"**Status: {icon}**")
    lines.append("")
    s = report["summary"]
    lines.append(f"- Ledger differences: {s['ledger_differences']}")
    lines.append(f"- Derived-figure differences: {s['derived_differences']}")
    lines.append(f"- Plan-state differences: {s['plan_differences']}")
    lines.append(f"- Total: {report['total_differences']}")
    if s.get("sheet_errors"):
        lines.append(f"- Sheet errors: {'; '.join(s['sheet_errors'])}")
    lines.append("")

    # Ledger comparison details
    lines.append("## Ledger comparison")
    lines.append("")
    for sheet_name in ["transactions", "bank_lines", "hours"]:
        sd = report["ledger_comparison"].get(sheet_name, {})
        if "error" in sd:
            lines.append(f"### {sheet_name}: ERROR -- {sd['error']}")
            lines.append("")
            continue
        exp_n = sd.get("expected_count", 0)
        act_n = sd.get("actual_count", 0)
        lines.append(f"### {sheet_name} ({exp_n} expected, {act_n} found)")
        lines.append("")
        if sd.get("missing_ids"):
            lines.append(f"- Missing IDs: {', '.join(sd['missing_ids'])}")
        if sd.get("extra_ids"):
            lines.append(f"- Extra IDs: {', '.join(sd['extra_ids'])}")
        if sd.get("field_differences"):
            lines.append("")
            lines.append("| ID | Field | Expected | Actual |")
            lines.append("|---|---|---|---|")
            for fd in sd["field_differences"]:
                lines.append(f"| {fd['id']} | {fd['field']} | {fd['expected']} | {fd['actual']} |")
        if not (sd.get("missing_ids") or sd.get("extra_ids") or sd.get("field_differences")):
            lines.append("- All rows match.")
        lines.append("")

    # Derived comparison
    lines.append("## Derived figures")
    lines.append("")
    if report["derived_comparison"]:
        lines.append("| Field | Expected | Actual |")
        lines.append("|---|---|---|")
        for d in report["derived_comparison"]:
            lines.append(f"| {d['field']} | {d['expected']} | {d['actual']} |")
    else:
        lines.append("All derived figures match.")
    lines.append("")

    # Plan state
    lines.append("## Plan state")
    lines.append("")
    if report["plan_comparison"]:
        lines.append("| Field | Expected | Actual |")
        lines.append("|---|---|---|")
        for d in report["plan_comparison"]:
            lines.append(f"| {d['field']} | {d['expected']} | {d['actual']} |")
    else:
        lines.append("Plan state correct: P01=15, one change_log row.")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compare workspace outputs against the golden answer key.")
    parser.add_argument("--workspace", type=Path,
                        default=DEFAULT_WORKSPACE,
                        help="Path to the workspace directory")
    parser.add_argument("--answer-key-dir", type=Path,
                        default=DEFAULT_ANSWER_KEY,
                        help="Path to data/answer_key/")
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).parent,
                        help="Where to write report files")
    args = parser.parse_args()

    ws = args.workspace
    ak = args.answer_key_dir
    out = args.output_dir

    # --- Check files exist ---
    # Base paths: the files are <base>_<sheet>.csv.
    ws_ledger_path = ws / "ledger"
    ws_plan_path = ws / "plan" / "plan"
    exp_ledger_path = ak / "ledger"
    calc_path = ak / ".expected_ledger.ref" / "calculation.json"

    errors = []
    if not Path(f"{ws_ledger_path}_transactions.csv").exists():
        errors.append(f"Workspace ledger not found: {ws_ledger_path}")
    if not Path(f"{ws_plan_path}_products.csv").exists():
        errors.append(f"Workspace plan not found: {ws_plan_path}")
    if not Path(f"{exp_ledger_path}_transactions.csv").exists():
        errors.append(f"Expected ledger not found: {exp_ledger_path}")
    if not calc_path.exists():
        errors.append(f"Calculation JSON not found: {calc_path}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        # Still write a minimal report
        report = {"status": "FAIL", "errors": errors, "total_differences": len(errors)}
        (out / "latest_report.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nStatus: FAIL ({len(errors)} file errors)")
        return 1

    # --- Read ---
    print("Reading expected ledger...")
    expected_ledger = read_ledger(exp_ledger_path)

    print("Reading workspace ledger...")
    workspace_ledger = read_ledger(ws_ledger_path)

    print("Reading workspace plan...")
    workspace_plan = read_plan(ws_plan_path)

    print("Reading golden calculation...")
    expected_calc = json.loads(calc_path.read_text(encoding="utf-8"))

    # --- Layer 1: Compare ledger sheets ---
    print("\n--- Layer 1: Ledger sheet comparison ---")
    ledger_diffs = {}

    for sheet_name, id_col, cols in [
        ("transactions", "txn_id", TX_COLS),
        ("bank_lines", "bank_reference", BANK_COLS),
        ("hours", "_key", HOURS_COLS),
    ]:
        exp_rows = expected_ledger[sheet_name]
        act_rows = workspace_ledger[sheet_name]

        if exp_rows is None:
            ledger_diffs[sheet_name] = None
            print(f"  {sheet_name}: ERROR -- expected sheet missing or columns wrong")
            continue
        if act_rows is None:
            ledger_diffs[sheet_name] = None
            print(f"  {sheet_name}: ERROR -- workspace sheet missing or columns wrong")
            continue

        if sheet_name == "hours":
            exp_rows, act_rows = keyed_hours(exp_rows), keyed_hours(act_rows)
        diff = compare_rows(exp_rows, act_rows, id_col, sheet_name,
                            ignore=FREE_TEXT.get(sheet_name, ()))
        ledger_diffs[sheet_name] = diff
        n = (len(diff["missing_ids"]) + len(diff["extra_ids"]) +
             len(diff["field_differences"]))
        print(f"  {sheet_name}: {diff['expected_count']} expected, "
              f"{diff['actual_count']} found, {n} differences")

    # --- Layer 2: Recalculate and compare derived figures ---
    print("\n--- Layer 2: Derived figures ---")
    actual_calc = recalculate(workspace_ledger, workspace_plan)
    derived_diffs = compare_derived(expected_calc, actual_calc)
    if derived_diffs:
        print(f"  {len(derived_diffs)} differences:")
        for d in derived_diffs:
            print(f"    {d['field']}: expected {d['expected']}, got {d['actual']}")
    else:
        print("  All derived figures match.")

    # --- Layer 3: Plan state ---
    print("\n--- Layer 3: Plan state ---")
    plan_diffs = check_plan_state(workspace_plan)
    if plan_diffs:
        print(f"  {len(plan_diffs)} differences:")
        for d in plan_diffs:
            print(f"    {d['field']}: expected {d['expected']}, got {d['actual']}")
    else:
        print("  Plan state correct.")

    # --- Generate report ---
    report = generate_report(ledger_diffs, derived_diffs, plan_diffs,
                             expected_ledger, workspace_ledger)

    report["actual_derived"] = actual_calc  # include for debugging

    # Write files
    (out / "latest_report.json").write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8")
    write_markdown(report, out / "run_report.md")

    # Console summary
    print(f"\n{'='*60}")
    print(f"  STATUS: {report['status']}")
    print(f"  Total differences: {report['total_differences']}")
    print(f"  Reports written to: {out}")
    print(f"{'='*60}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
