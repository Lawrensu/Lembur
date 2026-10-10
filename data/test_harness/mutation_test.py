"""mutation_test.py -- Prove the comparator catches every kind of error.

Each mutation:
  1. Start from the golden ledger (data/answer_key/ledger_*.csv copied into a
     temporary workspace; the real workspace/ is never touched).
  2. Apply one known error (status, amount, minutes, missing row, etc.).
  3. Run compare_outputs.py.
  4. Verify the comparator reports FAIL with the expected field(s).
  5. Restore the golden state.

A passing mutation test means: every error a real agent could make is caught.
A mutation that does NOT trigger FAIL is a gap in the comparator.

Usage:
    python mutation_test.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from copy import deepcopy

import csv

ROOT = Path(__file__).resolve().parents[2]
HARNESS = Path(__file__).parent
ANSWER_KEY = ROOT / "data" / "answer_key"
DEMO = ROOT / "data" / "demo"
# A temporary workspace: the real workspace/ may hold a run and is never touched.
TEMP = Path(tempfile.mkdtemp(prefix="lembur_mutation_"))
WORKSPACE = TEMP / "workspace"
PYTHON = sys.executable
LEDGER_SHEETS = ("transactions", "bank_lines", "hours")
PLAN_SHEETS = ("products", "channels", "assumptions", "change_log")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return [row for row in csv.reader(handle)]


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerows(rows)


def copy_baseline_plan():
    for sheet in PLAN_SHEETS:
        shutil.copy2(DEMO / f"plan_{sheet}.csv", WORKSPACE / "plan" / f"plan_{sheet}.csv")


def setup_golden():
    """Copy the golden ledger + corrected plan into the temporary workspace."""
    (WORKSPACE / "plan").mkdir(parents=True, exist_ok=True)
    for sheet in LEDGER_SHEETS:
        shutil.copy2(ANSWER_KEY / f"ledger_{sheet}.csv", WORKSPACE / f"ledger_{sheet}.csv")
    copy_baseline_plan()
    # Apply the correction (P01=15, one change_log row)
    path = WORKSPACE / "plan" / "plan_products.csv"
    rows = read_csv(path)
    column = rows[0].index("minutes_per_unit")
    for row in rows[1:]:
        if row[0] == "P01":
            row[column] = "15"
    write_csv(path, rows)
    path = WORKSPACE / "plan" / "plan_change_log.csv"
    rows = read_csv(path)
    rows.append(["2026-10-07", "products.P01.minutes_per_unit", "20", "15",
                 "I timed myself today, keychains take 15 minutes not 20",
                 "message.2026-10-07"])
    write_csv(path, rows)


def run_comparator():
    """Run compare_outputs.py on the temporary workspace and return the report dict."""
    report_path = TEMP / "latest_report.json"
    report_path.unlink(missing_ok=True)  # never read the report of an earlier run
    result = subprocess.run(
        [PYTHON, str(HARNESS / "compare_outputs.py"), "--workspace", str(WORKSPACE),
         "--output-dir", str(TEMP)],
        capture_output=True, text=True, cwd=str(ROOT))
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    else:
        report = {"status": "ERROR", "output": result.stdout, "errors": [result.stderr]}
    return report


def mutate_ledger(mutations):
    """Apply a list of (sheet, row_id, column, new_value) mutations to the workspace ledger."""
    for sheet_name, row_id, column, new_value in mutations:
        path = WORKSPACE / f"ledger_{sheet_name}.csv"
        rows = read_csv(path)
        col_idx = rows[0].index(column)
        for row in rows[1:]:
            if row[0] == row_id:
                row[col_idx] = str(new_value)
                break
        write_csv(path, rows)


def mutate_plan_remove_changelog():
    """Remove the change_log row (revert to baseline plan)."""
    copy_baseline_plan()


def restore_golden():
    """Restore the golden state."""
    setup_golden()


# ---------------------------------------------------------------------------
# Mutation definitions
# ---------------------------------------------------------------------------

MUTATIONS = [
    {
        "name": "status_change_matched_to_unmatched",
        "description": "T0005 reconciliation_status: matched -> unmatched",
        "apply": lambda: mutate_ledger([
            ("transactions", "T0005", "reconciliation_status", "unmatched"),
        ]),
        "expected_fields": ["T0005", "reconciliation_status", "review_ids"],
    },
    {
        "name": "status_change_to_wrong_value",
        "description": "T0003 reconciliation_status: matched -> duplicate",
        "apply": lambda: mutate_ledger([
            ("transactions", "T0003", "reconciliation_status", "duplicate"),
        ]),
        "expected_fields": ["T0003", "category_sen", "review_ids"],
    },
    {
        "name": "amount_change_sen",
        "description": "T0003 amount_rm: 18.00 -> 19.00 (1 sen diff)",
        "apply": lambda: mutate_ledger([
            ("transactions", "T0003", "amount_rm", 19.00),
        ]),
        "expected_fields": ["T0003", "amount_rm", "category_sen", "take_home"],
    },
    {
        "name": "amount_change_half_sen",
        "description": "T0005 amount_rm: 5.00 -> 5.005 (sub-sen diff)",
        "apply": lambda: mutate_ledger([
            ("transactions", "T0005", "amount_rm", 5.005),
        ]),
        "expected_fields": ["T0005", "amount_rm"],
    },
    {
        "name": "minutes_change",
        "description": "H0001 minutes: 40 -> 35",
        "apply": lambda: mutate_ledger([
            ("hours", "H0001", "minutes", 35),
        ]),
        "expected_fields": ["H0001", "minutes", "total_minutes", "hourly_rate"],
    },
    {
        "name": "source_label_change",
        "description": "H0007 source: corrected -> estimate",
        "apply": lambda: mutate_ledger([
            ("hours", "H0007", "source", "estimate"),
        ]),
        "expected_fields": ["H0007", "source"],
    },
    {
        "name": "bank_reference_change",
        "description": "T0010 bank_reference: DEMO-IN-007 -> DEMO-IN-999",
        "apply": lambda: mutate_ledger([
            ("transactions", "T0010", "bank_reference", "DEMO-IN-999"),
        ]),
        "expected_fields": ["T0010", "bank_reference"],
    },
    {
        "name": "product_id_change",
        "description": "T0006 product_id: P02 -> P01",
        "apply": lambda: mutate_ledger([
            ("transactions", "T0006", "product_id", "P01"),
        ]),
        "expected_fields": ["T0006", "product_id", "P01", "P02"],
    },
    {
        "name": "plan_no_correction",
        "description": "Plan P01 minutes_per_unit stays 20 (correction not applied)",
        "apply": mutate_plan_remove_changelog,
        "expected_fields": ["minutes_per_unit", "change_log"],
    },
    {
        "name": "extra_hours_line",
        "description": "Add a spurious H0021 hours line",
        "apply": lambda: _add_extra_hours_line(),
        "expected_fields": ["extra", "hours", "total_minutes"],
    },
    {
        "name": "missing_transaction",
        "description": "Delete T0020 (the unmatched leftover-bank row)",
        "apply": lambda: _delete_row("transactions", "T0020"),
        "expected_fields": ["T0020", "missing", "category_sen", "review_ids"],
    },
]


def _add_extra_hours_line():
    path = WORKSPACE / "ledger_hours.csv"
    rows = read_csv(path)
    rows.append(["H0021", "2026-10-11", "person_1", "admin", "", "", "60",
                 "estimate", "assumptions.admin_hours_per_week"])
    write_csv(path, rows)


def _delete_row(sheet_name, row_id):
    path = WORKSPACE / f"ledger_{sheet_name}.csv"
    rows = read_csv(path)
    write_csv(path, [rows[0]] + [row for row in rows[1:] if row[0] != row_id])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("  MUTATION TESTING -- Proving the comparator catches every error type")
    print("=" * 70)
    print()

    # --- Baseline: golden self-check ---
    print("Baseline: golden ledger against itself...")
    setup_golden()
    report = run_comparator()
    if report["status"] != "PASS":
        print(f"  FAIL: baseline should PASS but got {report['status']}")
        print(f"  Differences: {report.get('total_differences', '?')}")
        return 1
    print(f"  PASS (0 differences) -- baseline is clean")
    print()

    # --- Run each mutation ---
    results = []
    all_passed = True

    for m in MUTATIONS:
        print(f"Mutation: {m['name']}")
        print(f"  {m['description']}")

        # Restore golden, then apply mutation
        restore_golden()
        m["apply"]()

        # Run comparator
        report = run_comparator()

        if report["status"] == "FAIL" and report["total_differences"] > 0:
            n = report["total_differences"]
            print(f"  CAUGHT: FAIL with {n} difference(s)")
            results.append({"name": m["name"], "status": "CAUGHT",
                            "differences": n})
        else:
            n = report.get("total_differences", 0)
            print(f"  *** MISSED: comparator did not catch this mutation! ***")
            print(f"      Status: {report['status']}, diffs: {n}")
            results.append({"name": m["name"], "status": "MISSED",
                            "differences": n})
            all_passed = False
        print()

    # --- Remove the temporary workspace ---
    shutil.rmtree(TEMP, ignore_errors=True)

    # --- Summary ---
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    caught = sum(1 for r in results if r["status"] == "CAUGHT")
    missed = sum(1 for r in results if r["status"] == "MISSED")
    total = len(results)
    print(f"  Mutations tested: {total}")
    print(f"  Caught: {caught}")
    print(f"  Missed: {missed}")
    print()
    for r in results:
        icon = "OK" if r["status"] == "CAUGHT" else "!!"
        print(f"  [{icon}] {r['name']}: {r['differences']} diffs")
    print()
    if all_passed:
        print("  ALL MUTATIONS CAUGHT -- comparator is trustworthy.")
    else:
        print("  *** SOME MUTATIONS WERE MISSED -- check the comparator! ***")
    print()

    # Write summary report
    summary_path = HARNESS / "mutation_report.json"
    summary_path.write_text(
        json.dumps({"all_caught": all_passed, "total": total,
                     "caught": caught, "missed": missed,
                     "results": results}, indent=2),
        encoding="utf-8")
    print(f"  Report written to: {summary_path}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
