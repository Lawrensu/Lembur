"""reset_workspace.py -- Clean the workspace and reload baseline demo inputs.

Before each recorded run, the workspace must be wiped and refilled so
that every run starts from the same state (system design, Validation:
"the workspace can be wiped and refilled before each recorded run").

Modes:
    --full          Clean everything, copy plan + all 16 inbox files.
    --day YYYY-MM-DD  Clean everything, copy plan + only that day's files.
    --clean-only    Just clean; don't copy anything (for manual setup).

The day-to-file mapping is derived from data/demo/messages.md.

Usage:
    python reset_workspace.py                # default: --full
    python reset_workspace.py --full
    python reset_workspace.py --day 2026-10-05
    python reset_workspace.py --clean-only
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "workspace"
DEMO = ROOT / "data" / "demo"

# Subdirectories that hold runtime outputs (cleaned on reset)
RUNTIME_DIRS = [
    "inbox",
    "receipts",
    "boardroom",
    "audit",
    "approvals",
    "payslips",
    "plan",
]

# Top-level workspace files to remove
RUNTIME_FILES = ["ledger_transactions.csv", "ledger_bank_lines.csv", "ledger_hours.csv"]

# The baseline plan: one CSV file per sheet (SYSTEM_DESIGN, Folder layout)
PLAN_FILES = ["plan_products.csv", "plan_channels.csv", "plan_assumptions.csv",
              "plan_change_log.csv"]

# Day-to-file mapping (from messages.md daily "Files:" lines)
DAY_FILES = {
    "2026-10-05": [
        "order_2026-10-05_dana.png",
        "order_2026-10-05_mira.png",
        "receipt_beads.png",
        "receipt_beads_copy.png",
    ],
    "2026-10-06": [
        "order_2026-10-06_farah.png",
        "order_2026-10-06_hana.png",
        "order_2026-10-06_nisa.png",
    ],
    "2026-10-07": [
        "order_2026-10-07_iman.png",
        "receipt_pouches.png",
    ],
    "2026-10-08": [
        "order_2026-10-08_lina.png",
        "order_2026-10-08_rina.png",
        "receipt_thread_blurred.png",
    ],
    "2026-10-09": [
        "order_2026-10-09_suri.png",
        "receipt_shipping.png",
    ],
    "2026-10-10": [],  # bazaar day: no inbox files, cash orders from message
    "2026-10-11": [
        "order_2026-10-11_zahra.png",
        "bank_statement_2026-W41_SYNTHETIC.csv",
    ],
}

# All inbox files in order
ALL_INBOX = []
for day in sorted(DAY_FILES):
    ALL_INBOX.extend(DAY_FILES[day])


def clean_workspace():
    """Remove all runtime files from workspace/, keeping .gitkeep stubs."""
    removed = 0
    for item in WORKSPACE.iterdir():
        if item.name == ".gitkeep":
            continue
        if item.is_file():
            item.unlink()
            removed += 1
        elif item.is_dir():
            for child in item.rglob("*"):
                if child.is_file() and child.name != ".gitkeep":
                    child.unlink()
                    removed += 1
            # Remove empty subdirectories (but not the .gitkeep'd top level)
            for child in sorted(item.rglob("*"), reverse=True):
                if child.is_dir() and not any(child.iterdir()):
                    child.rmdir()
    return removed


def copy_plan():
    """Copy the baseline plan CSV files to workspace/plan/."""
    missing = [name for name in PLAN_FILES if not (DEMO / name).exists()]
    if missing:
        print(f"ERROR: baseline plan files not found in {DEMO}: {', '.join(missing)}")
        return False
    (WORKSPACE / "plan").mkdir(parents=True, exist_ok=True)
    for name in PLAN_FILES:
        shutil.copy2(DEMO / name, WORKSPACE / "plan" / name)
    return True


def copy_inbox_files(filenames):
    """Copy the given inbox files from data/demo/inbox/ to workspace/inbox/."""
    src_dir = DEMO / "inbox"
    dst_dir = WORKSPACE / "inbox"
    dst_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    missing = []
    for fname in filenames:
        src = src_dir / fname
        if not src.exists():
            missing.append(fname)
            continue
        shutil.copy2(src, dst_dir / fname)
        copied += 1
    if missing:
        print(f"WARNING: {len(missing)} files not found in demo inbox:")
        for m in missing:
            print(f"  {m}")
    return copied


def main():
    parser = argparse.ArgumentParser(
        description="Clean workspace and reload baseline demo inputs.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--full", action="store_true",
                      help="Copy plan + all inbox files (default)")
    mode.add_argument("--day", type=str, metavar="YYYY-MM-DD",
                      help="Copy plan + only that day's inbox files")
    mode.add_argument("--clean-only", action="store_true",
                      help="Just clean; don't copy anything")
    args = parser.parse_args()

    # Default to --full
    if not args.full and not args.day and not args.clean_only:
        args.full = True

    # --- Clean ---
    print("Cleaning workspace...")
    removed = clean_workspace()
    print(f"  Removed {removed} runtime file(s)")

    if args.clean_only:
        print("\nDone. Workspace is clean (plan and inbox not copied).")
        return 0

    # --- Copy plan ---
    print("Copying baseline plan...")
    if not copy_plan():
        print("\nABORT: cannot proceed without plan file")
        return 1
    print("  plan_*.csv -> workspace/plan/")

    # --- Copy inbox files ---
    if args.day:
        if args.day not in DAY_FILES:
            print(f"ERROR: unknown day '{args.day}'. "
                  f"Known days: {', '.join(sorted(DAY_FILES))}")
            return 1
        files = DAY_FILES[args.day]
        print(f"Copying inbox files for {args.day}...")
        if not files:
            print("  (no inbox files for this day -- bazaar cash orders "
                  "come from the message)")
        copied = copy_inbox_files(files)
        print(f"  Copied {copied} file(s)")
    else:
        print("Copying all inbox files...")
        copied = copy_inbox_files(ALL_INBOX)
        print(f"  Copied {copied} file(s)")

    # --- Summary ---
    print(f"\nWorkspace ready. Next step:")
    if args.day:
        next_days = [d for d in sorted(DAY_FILES) if d > args.day]
        if next_days:
            print(f"  Run agents for {args.day}, then reset --day {next_days[0]}")
        else:
            print(f"  Run agents for {args.day} (final day), "
                  "then run compare_outputs.py")
    else:
        print("  Run agents (full week), then run compare_outputs.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
