"""Compare two separate calculations and render the draft answer key."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json
import openpyxl

ROOT = Path(__file__).resolve().parents[3]
base = ROOT / "data/answer_key"
a = json.loads((base/".expected_ledger.ref/calculation.json").read_text())
b = json.loads((base/".independent.ref/independent_result.json").read_text())
w = openpyxl.load_workbook(base/"expected_ledger.xlsx", data_only=True)
tables = {s.title:[dict(zip(next(s.values),row)) for row in list(s.values)[1:]] for s in w}
checks = []
def same(label, left, right):
    if left != right:
        raise AssertionError(f"STOP FOR SHARON: {label}: {left!r} != {right!r}")
    checks.append(label)

n = b["numbers"]
for key, other in [("category_sen","category_totals_sen"),("take_home_sen","take_home_sen"),("total_minutes","total_minutes"),("display_hours","total_hours_display"),("activity_minutes","minutes_by_activity"),("shared_minutes","shared_minutes")]:
    same(key,a[key],n[other])
same("hourly_rate",a["hourly_rate"],n["hourly_rate_rm"]["display"])
same("margin_percent",a["margin_percent"],n["margin_percent"]["display"])
same("review_ids",a["review_ids"],[r["txn_id"] for r in b["review_list"]])
same("hours_count",len(tables["hours"]),len(b["hours"]))
for h, other in zip(tables["hours"], b["hours"]):
    same(h["entry_id"], h, {k:other[k] for k in h})
for p in b["products"]:
    original = a["products"][p["product_id"]]
    for key, other in [("units","units"),("revenue_sen","revenue_sen"),("unit_cost_sen","unit_costs_sen"),("channel_cost_sen","channel_costs_sen"),("profit_sen","profit_sen"),("direct_minutes","direct_minutes"),("loses_money","loses_money")]:
        same(f"{p['product_id']}.{key}",original[key],p[other])
    same(f"{p['product_id']}.profit_per_hour",original["profit_per_hour"],p["profit_per_hour_rm"]["display"])
for r, other in zip(tables["transactions"],b["reconciliation_audit"]):
    same(f"{r['txn_id']}.status",r["reconciliation_status"],other["derived_status"])
    same(f"{r['txn_id']}.bank",r["bank_reference"],other["derived_bank_reference"])
    amount = None if r["amount_rm"] is None else int(Decimal(str(r["amount_rm"]))*100)
    same(f"{r['txn_id']}.amount",amount,other["derived_amount_sen"])
assert b["audit"]["all_consistency_checks_pass"]
assert not b["conflicts"]

report = {"status":"PASS", "comparison_count":len(checks), "differences":[], "compared":checks}
(base/".expected_ledger.ref/cross_check.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
def rm(sen): return str((Decimal(sen)/100).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP))

lines = ["# Answer key - 2026-W41", "", "- Status: independently verified draft; awaiting Sharon's business sign-off. Do not treat as an approved release yet.",
"- Synthetic demonstration only. Aisyah and all customers and suppliers are fictional. Channel costs are approved scenario assumptions, not statements of platform pricing.",
"- Dates: Monday 2026-10-05 through Sunday 2026-10-11, Malaysia time.",
"- Sources of truth: docs/PLAN.md section 10; docs/SYSTEM_DESIGN.md sections 2 to 4.",
"- Fixture: 20 transactions, 14 bank lines, 20 hours lines; 14 separate single-product sales orders.",
"- Money uses integer sen; time uses integer minutes; display uses half-away-from-zero rounding. Never divide by rounded displayed hours.",
"", "## Validation and limitations", "",
f"- Primary and independent calculations: {len(checks)} exact comparisons passed; zero differences, including all hours fields, money, statuses and bank references.",
"- Independent calculator received only the two source-of-truth docs, baseline plan, messages, and isolated transactions/bank_lines sheets. It did not receive expected hours, the first calculator, or this answer key.",
"- Rule checker covers every planted problem and every dataset rule. See .expected_ledger.ref/rule_check.md for results and visual-inspection limitations.",
"- This validates the fixture, not Law's extraction workflow, model OCR accuracy, trigger reliability, or an observed end-to-end run. Those remain to be tested against this key.",
"- The blurry expense has an unknown amount, not a zero expense. Take home and hourly rate are provisional known-amount results; true earnings may be lower once the receipt is readable.",
"- No projected raise or Day Zero formula is used. Both design-section-8 proposals remain unapproved.",
"", "## Ledger totals by category", ""]
for category, total in a["category_sen"].items():
    ids = [r["txn_id"] for r in tables["transactions"] if r["category"] == category and r["reconciliation_status"] != "duplicate" and r["amount_rm"] is not None]
    lines.append(f"- {category}: RM{rm(total)}; counted rows: {', '.join(ids) or 'none'}.")
lines += [f"- Total counted expenses: RM{n['expense_total_rm']}.",
f"- Take home: RM{rm(a['category_sen']['sales'])} minus RM{n['expense_total_rm']} = RM{rm(a['take_home_sen'])}.",
f"- Hourly rate: RM{rm(a['take_home_sen'])} / {a['total_minutes']} minutes * 60 = RM{a['hourly_rate']}/hour.",
f"- Margin: take home / sales * 100 = {a['margin_percent']}% displayed; plan {n['planned_margin_percent']}%.",
f"- Hourly-rate comparison: RM{a['hourly_rate']} actual against RM{n['target_hourly_rate_rm']} target.",
"", "## Planted problems and final review list", "",
"- T0004, duplicate receipt: duplicate of T0003; both document amounts RM18.00, same date, counterparty and reference DEMO-OUT-001. Keep both images filed; exclude T0004 from totals and hours. Review: confirm the second upload is a copy.",
"- T0012, blurry receipt: needs_review; amount_rm stays empty. Intake flag takes precedence over cash_declared. Exclude from totals; retain receipts/2026-10/receipt_thread_blurred.png. Review: request a legible original, do not estimate the amount.",
"- T0019, amount mismatch: needs_review; document RM5.00 and bank RM4.50 share DEMO-IN-010. Keep both amounts in notes, use RM4.50 in totals, and count the single sold keychain for hours. Review: confirm whether the difference is an underpayment or another error.",
"- T0020, missing receipt: unmatched; bank DEMO-OUT-004 identifies Demo Bead Nook and bead materials. Sunday leftover-bank row is a materials expense of RM9.00, included in totals, with source_file empty. Review: request the missing receipt.",
f"- Final review IDs, exactly: {', '.join(a['review_ids'])}.",
"- Bestseller that loses money: P01; see product results below. It is a product warning, not a new reconciliation status.",
"- Event: H0017; Saturday 10am to 6pm gives 480 stated minutes; message.2026-10-10.",
"- Correction: Wednesday's one reply changes products.P01.minutes_per_unit from 20 to 15. Sales exist before and after the effective date.",
"", "## Correction and plan state", "",
"- The input data/demo/plan.xlsx is the baseline: P01=20 and change_log has headers only.",
"- The run's workspace/plan/plan.xlsx ends with P01=15 and exactly one change_log row: changed_at=2026-10-07; field=products.P01.minutes_per_unit; old_value=20; new_value=15; reason=I timed myself today, keychains take 15 minutes not 20; source=message.2026-10-07.",
"- Sharon-approved clarification of design wording: pre-correction P01 lines use 20 and source=estimate; on/after October 7 use 15 and source=corrected. Historical baseline values are not retroactively labelled corrected. Shared source-of-truth docs have not been edited.",
"- Other production, fulfilment and admin lines remain estimate. Only the bazaar event is stated. No extra stated production hours are added.",
"", "## Every expected hours line", ""]
for h in tables["hours"]:
    lines.append(f"- {h['entry_id']}: {h['date']}; {h['activity']}; product={h['product_id'] or 'empty'}; quantity={h['quantity'] if h['quantity'] is not None else 'empty'}; {h['minutes']} minutes; source={h['source']}; assumption_ref={h['assumption_ref']}.")
for activity, mins in a["activity_minutes"].items(): lines.append(f"- {activity} total: {mins} minutes.")
lines += [f"- Week total: {a['total_minutes']} minutes; {a['display_hours']} hours displayed.",
f"- Shared event plus admin: {a['shared_minutes']} minutes; not allocated to products.",
"", "## Product profit and direct hourly earnings", ""]
for p in b["products"]:
    lines += [f"- {p['product_id']} - {p['name']}:",
              f"  - Units sold: {p['units']}; revenue RM{p['revenue_rm']}.",
              f"  - Unit costs: RM{p['unit_costs_rm']}; channel costs: RM{p['channel_costs_rm']}.",
              f"  - Profit: RM{p['profit_rm']}; loses money: {'yes' if p['loses_money'] else 'no'}.",
              f"  - Direct time: {p['direct_minutes_by_activity']['production']} production + {p['direct_minutes_by_activity']['fulfilment']} fulfilment = {p['direct_minutes']} minutes.",
              f"  - Profit / direct minutes * 60: RM{p['profit_per_hour_rm']['display']}/hour."]
lines += ["- Two bases, on purpose: take home uses actual ledger purchases; product profit uses plan per-unit costs and per-order channel costs. Product profits do not add up to take home; shared time is excluded from product hourly rates.",
"", "## Expected Auditor direction", "",
f"- Uphold Payroll against expanding the existing keychain mix merely because P01 sold {a['products']['P01']['units']} units. P01 loses RM{rm(-a['products']['P01']['profit_sen'])}; its direct hourly profit is RM{a['products']['P01']['profit_per_hour']}.",
f"- Support prioritising bracelet promotion: P02 earns RM{rm(a['products']['P02']['profit_sen'])} and RM{a['products']['P02']['profit_per_hour']} per direct hour. Do not present this as the whole-business hourly rate.",
"- Support moving low-priced keychains to campus pickup/bazaar or reviewing delivered pricing before more promotion. Draft changes for approval; do not send or post.",
"- Reject unsupported claims about future demand or a precise hourly raise. A positive product profit alone does not justify expanding an eight-hour event.",
"- Preserve all four review entries and the unknown-expense caveat in the payslip.",
"", "## Bank matching and every transaction status", "",
"- Dana and Mira have same-amount nearby bank candidates and no printed references. Resolve by the fictional customer name in the bank description. Both are ambiguous_resolved; reference-bearing transfers match directly."]
for r in tables["transactions"]:
    amount = "empty (unknown)" if r["amount_rm"] is None else "RM"+rm(int(Decimal(str(r["amount_rm"]))*100))
    lines.append(f"- {r['txn_id']}: {r['date']}; {r['reconciliation_status']}; {amount}; bank_reference={r['bank_reference'] or 'empty'}; source_file={r['source_file'] or 'empty'}.")
lines += ["", "## Reproduction and handoff", "",
"- Run the scripts using a Python environment with openpyxl and Pillow installed; paths below are relative to the repository root. No runtime app or skills are installed by this fixture.",
"- Baseline workbook: data/demo/.plan.ref/build.py.",
"- Expected ledger and primary numbers: data/answer_key/.expected_ledger.ref/build.py.",
"- Derived sources: render_receipts.py, render_orders.py and render_bank.py in data/answer_key/.expected_ledger.ref/.",
"- Nightly text and intake batches: data/demo/messages.md.",
"- Independent rebuild: data/answer_key/.independent.ref/independent_calc.py, using its isolated two-sheet input. Refresh that isolated input from transactions and bank_lines if the fixture changes; never include expected hours or primary calculation code.",
"- Rule checks: data/answer_key/.expected_ledger.ref/check_rules.py.",
"- Exact comparison and this draft: data/answer_key/.expected_ledger.ref/verify_and_write_key.py.",
"- Run inputs only: copy baseline plan and each day's inbox batch/message into workspace. Never copy data/answer_key into workspace or give it to the production agents during the demo.",
"- Next gate: Sharon signs off on the story and answer key. Later, compare Law's real outputs row-by-row, including amounts to the sen, statuses, sources and minutes. No observed-run comparison has happened yet."]
(base/"answer_key.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(f"PASS: {len(checks)} exact comparisons, zero differences; wrote draft answer_key.md")
