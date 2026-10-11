"""replay_week.py -- Replay the demo week through the runner with the real models.

Reads data/demo/messages.md for the seven dated messages, resets the inbox to
each day's files, saves the message as receipts/<year_month>/message_<date>.txt,
then calls app.runner.run_night once per night.

It repeats the replay of proof 4 (PLAN section 12). It starts each night
from the fixture, not from the chat, so it never touches Telegram.

Usage:
    python -B data/test_harness/replay_week.py
    python -B data/test_harness/replay_week.py --workspace workspace
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app import runner  # noqa: E402

DEMO = ROOT / "data" / "demo"

# The seven nights, in order, from data/demo/messages.md.
DAYS = [
    {
        "date": "2026-10-05",
        "files": ["order_2026-10-05_dana.png", "order_2026-10-05_mira.png",
                  "receipt_beads.png", "receipt_beads_copy.png"],
        "message": ("Two Instagram keychain orders today, Dana and Mira. I bought a small "
                    "bead restock. I dropped the order screenshots and the receipt photos "
                    "into the folder. Please sort them out."),
    },
    {
        "date": "2026-10-06",
        "files": ["order_2026-10-06_farah.png", "order_2026-10-06_hana.png",
                  "order_2026-10-06_nisa.png"],
        "message": ("Farah and Nisa ordered one keychain each on Instagram. Hana ordered one "
                    "bracelet on Instagram. Their order screenshots are in the folder."),
    },
    {
        "date": "2026-10-07",
        "files": ["order_2026-10-07_iman.png", "receipt_pouches.png"],
        "message": ("Iman ordered a keychain on Instagram. I bought a small pouch restock. "
                    "I timed myself today, keychains take 15 minutes not 20."),
    },
    {
        "date": "2026-10-08",
        "files": ["order_2026-10-08_lina.png", "order_2026-10-08_rina.png",
                  "receipt_thread_blurred.png"],
        "message": ("Lina ordered one keychain on Instagram. Rina ordered one bracelet on "
                    "Telegram for campus pickup. I also paid cash for thread, but the total "
                    "on that receipt is blurred and I cannot read it. Please flag it rather "
                    "than guess."),
    },
    {
        "date": "2026-10-09",
        "files": ["order_2026-10-09_suri.png", "receipt_shipping.png"],
        "message": ("Suri ordered one Instagram keychain. I paid the courier for nine parcel "
                    "labels for this week's Instagram orders, including the label I will use "
                    "over the weekend. The courier payment covers those labels; it is not "
                    "another sale. Telegram buyers collect on campus."),
    },
    {
        "date": "2026-10-10",
        "files": [],
        "message": ("I ran the campus bazaar today from 10:00am to 6:00pm, eight hours in "
                    "total. Cash orders, all separate: Aina bought one P01 beaded keychain "
                    "for RM5.00; Bella bought one P01 beaded keychain for RM5.00; Citra bought "
                    "one P01 beaded keychain for RM5.00; Dina bought one P02 beaded bracelet "
                    "for RM18.00. All four orders were at the bazaar. I handed them over at "
                    "the stall. Please record each once from this message."),
    },
    {
        "date": "2026-10-11",
        "files": ["order_2026-10-11_zahra.png", "bank_statement_2026-W41_SYNTHETIC.csv"],
        "message": ("Zahra ordered one keychain on Instagram today; the order screenshot is "
                    "in the folder. Here is my statement for the week. I cannot find the "
                    "receipt for the small bead top-up at Demo Bead Nook today. Please close "
                    "the week, show me what needs checking, and prepare my payslip. Keychains "
                    "feel like my bestseller, but am I actually earning enough for my time?"),
    },
]


def reset_inbox(workspace: Path, files: list) -> None:
    """Empty workspace/inbox and copy only this day's files into it."""
    inbox = workspace / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    for item in inbox.iterdir():
        if item.is_file() and not item.name.startswith("."):
            item.unlink()
    for name in files:
        source = DEMO / "inbox" / name
        if source.exists():
            shutil.copy2(source, inbox / name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay the demo week through the runner.")
    parser.add_argument("--workspace", type=Path, default=ROOT / "workspace")
    args = parser.parse_args()
    workspace = args.workspace.resolve()

    for day in DAYS:
        date = day["date"]
        reset_inbox(workspace, day["files"])

        # Save the message as a receipt, per data/demo/messages.md.
        year_month = date[:7]
        receipts = workspace / "receipts" / year_month
        receipts.mkdir(parents=True, exist_ok=True)
        (receipts / ("message_%s.txt" % date)).write_text(day["message"], encoding="utf-8")

        print("=" * 72)
        print("Night %s  (%d inbox file(s))" % (date, len(day["files"])))
        print("=" * 72)

        summary = runner.run_night(workspace=str(workspace), date=date, message=day["message"])

        failed = summary.get("failed") or {}
        figures = summary.get("figures") or {}
        print("  week:        %s" % summary.get("week", ""))
        print("  payslip day: %s" % summary.get("payslip_day"))
        print("  payslip:     %s" % (summary.get("payslip") or "(none)"))
        print("  figures:     hourly RM%s  take home RM%s  hours %s" % (
            figures.get("hourly_rate_rm", ""),
            figures.get("take_home_rm", ""),
            figures.get("hours_total", "")))
        for step in summary.get("steps", []):
            print("    %s. %-14s %-13s %s" % (
                step.get("step", "?"), step.get("name", ""), step.get("status", ""),
                (step.get("note") or "")[:70]))
        if failed:
            print("  FAILED: step %s -- %s" % (failed.get("step"), failed.get("reason")))
        print()

    print("Replay finished. Now run:")
    print("  python -B data/test_harness/compare_outputs.py --workspace %s" % workspace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
