"""Tests for app/runner.py with a scripted model: no key and no network.

They follow docs/SYSTEM_DESIGN.md sections 6.1, 6.3 and 6.4.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import runner  # noqa: E402

SUMMARY_KEYS = {"week", "payslip_day", "steps", "figures", "payslip", "drafts", "review", "failed"}


def scripted(by_step):
    """A model that answers each step from a list of replies, then says finished."""
    seen = []

    def ask(role, messages, images=None):
        first = messages[0]["content"]
        if first.startswith("You plan one night"):
            return json.dumps({"steps": [], "skip": []})
        task = messages[1]["content"]
        step = task.split('"')[1]
        agent_turn = sum(1 for m in messages if m["role"] == "assistant")
        seen.append((step, agent_turn))
        replies = by_step.get(step, [])
        if agent_turn < len(replies):
            reply = replies[agent_turn]
            return reply if isinstance(reply, str) else json.dumps(reply)
        return json.dumps({"finished": True, "report": "done"})

    ask.seen = seen
    return ask


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.workspace = Path(tempfile.mkdtemp())
        (self.workspace / "plan").mkdir()
        (self.workspace / "inbox").mkdir()
        for source in sorted((ROOT / "data" / "demo").glob("plan_*.csv")):
            shutil.copyfile(source, self.workspace / "plan" / source.name)

    def tearDown(self):
        shutil.rmtree(self.workspace, ignore_errors=True)

    def night(self, date, by_step):
        return runner.run_night(self.workspace, date, "Nothing sold today.", ask=scripted(by_step))

    def save_message(self, date):
        return {"actions": [{"tool": "write_file", "args": {
            "path": "receipts/%s/message_%s.txt" % (date[:7], date), "text": "Nothing sold today."}}], "why": "save"}

    def command(self, name, **options):
        return {"actions": [{"tool": "lembur", "args": {"command": name, "options": options}}], "why": name}

    def script(self, date, **extra):
        """A night in which every step runs its own command and nothing else."""
        steps = {"intake": [self.save_message(date)],
                 "reconcile": [self.command("reconcile")],
                 "hours": [self.command("hours", week="2026-W41")],
                 "numbers": [self.command("numbers", week="2026-W41")]}
        steps.update(extra)
        return steps

    def test_summary_always_has_every_key(self):
        summary = self.night("2026-10-05", {})
        self.assertEqual(set(summary), SUMMARY_KEYS)
        self.assertEqual(set(summary["figures"]), {"hourly_rate_rm", "take_home_rm", "hours_total"})

    def test_a_step_that_says_finished_without_its_work_is_sent_back_once_then_fails(self):
        ask = scripted({})
        summary = runner.run_night(self.workspace, "2026-10-05", "Nothing sold today.", ask=ask)
        self.assertEqual(summary["failed"]["step"], 1)
        self.assertEqual([s["status"] for s in summary["steps"]],
                         ["failed", "skipped", "skipped", "skipped", "skipped"])
        self.assertEqual(sum(1 for step, turn in ask.seen if step == "intake" and turn == 0), 1 + runner.SEND_BACKS)

    def test_an_ordinary_night_runs_steps_one_to_five_and_writes_the_plan(self):
        summary = self.night("2026-10-05", self.script("2026-10-05"))
        self.assertEqual(summary["failed"], "")
        self.assertEqual([(s["step"], s["name"]) for s in summary["steps"]],
                         [(1, "intake"), (2, "reconcile"), (3, "corrections"), (4, "hours"), (5, "numbers")])
        self.assertEqual(summary["week"], "2026-W41")
        self.assertIs(summary["payslip_day"], False)
        plan = (self.workspace / "audit" / "2026-W41" / "plan_2026-10-05.md").read_text(encoding="utf-8")
        self.assertIn("Added back by the rules", plan)
        self.assertIn("Outcome**: done", plan)
        self.assertTrue((self.workspace / "audit" / "2026-W41" / "numbers.json").is_file())

    def test_payslip_day_adds_the_later_steps_in_the_design_order(self):
        summary = self.night("2026-10-11", {})
        self.assertIs(summary["payslip_day"], True)
        self.assertEqual([s["name"] for s in summary["steps"]],
                         ["intake", "reconcile", "close_week", "corrections", "hours", "numbers",
                          "recommendation", "recommendation", "audit", "drafts", "payslip", "confirm_payslip"])

    def test_one_bare_action_is_accepted_and_text_that_is_not_json_gets_a_reminder(self):
        bare = self.save_message("2026-10-05")["actions"][0]
        summary = self.night("2026-10-05", self.script("2026-10-05", intake=["I will start now.", bare]))
        self.assertEqual(summary["failed"], "")

    def test_a_message_that_starts_with_a_date_runs_as_that_night(self):
        ask = scripted(self.script("2026-10-06"))
        summary = runner.run_night(self.workspace, "2026-12-25", "2026-10-06: Nothing sold today.", ask=ask)
        self.assertEqual(summary["week"], "2026-W41")
        self.assertTrue((self.workspace / "audit" / "2026-W41" / "plan_2026-10-06.md").is_file())

    def test_a_step_that_skips_its_command_is_sent_back_and_then_fails(self):
        summary = self.night("2026-10-05", self.script("2026-10-05", reconcile=[]))
        self.assertEqual(summary["failed"]["step"], 2)
        self.assertIn("reconcile", summary["failed"]["reason"])

    def test_no_payslip_and_no_week_closing_on_an_ordinary_night(self):
        early = {"actions": [
            {"tool": "lembur", "args": {"command": "payslip", "options": {"week": "2026-W41"},
                                        "input": {"debate_summary": "x", "ruling": "y", "raise_plan": []}}},
            {"tool": "lembur", "args": {"command": "hours", "options": {"week": "2026-W41", "payslip-day": True}}}],
            "why": "too early"}
        summary = self.night("2026-10-05", self.script(
            "2026-10-05", numbers=[self.command("numbers", week="2026-W41"), early]))
        self.assertEqual(summary["payslip"], "")
        self.assertFalse((self.workspace / "payslips" / "2026-W41.html").exists())
        hours = (self.workspace / "ledger_hours.csv").read_text(encoding="utf-8")
        self.assertNotIn("admin", hours)

    def test_an_agent_cannot_reach_a_tool_that_is_not_its_own(self):
        forbidden = {"actions": [{"tool": "lembur", "args": {"command": "add-transactions", "input": []}}], "why": "try"}
        self.night("2026-10-05", self.script("2026-10-05", corrections=[forbidden]))
        trace = (self.workspace / "audit" / "2026-W41" / "trace_2026-10-05.jsonl").read_text(encoding="utf-8")
        refused = [json.loads(line) for line in trace.splitlines() if '"corrections"' in line and '"results"' in line]
        self.assertIs(refused[0]["results"][0]["ok"], False)


if __name__ == "__main__":
    unittest.main()
