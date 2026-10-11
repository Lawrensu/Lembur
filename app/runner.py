"""Plan the night and run the four agents (docs/SYSTEM_DESIGN.md sections 6.1, 6.3 and 6.4).

run_night(workspace, date, message, ask=None) is the only entry point. Each agent
works in a short loop: it asks for tools as one JSON object, the tool layer runs
them, and the agent reads the results and decides what to do next.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import tools as tool_layer  # noqa: E402

PROMPTS = ROOT / "prompts"
TURN_LIMIT = 16
REMINDERS = 2
COMMANDS = ("add-transactions", "add-bank-lines", "reconcile", "resolve", "classify", "close-week",
            "correct-plan", "hours", "numbers", "numbers-check", "review", "payslip")
SEND_BACKS = 2

# (number in design section 6.1, name, agent, payslip day only, what it is for)
STEPS = (
    (1, "intake", "bookkeeper", False, "save the message, read the documents, record and file them"),
    (2, "reconcile", "bookkeeper", False, "give every row a status against the bank lines"),
    (6, "close_week", "bookkeeper", True, "turn leftover bank lines into rows and classify them"),
    (3, "corrections", "payroll", False, "apply a correction in the message to the plan"),
    (4, "hours", "payroll", False, "build the hours lines"),
    (5, "numbers", "payroll", False, "save take home, hourly rate and profit per hour"),
    (7, "recommendation", "payroll", True, "argue for the change that raises the hourly rate"),
    (7, "recommendation", "growth_coach", True, "argue for the change that grows sales"),
    (8, "audit", "auditor", True, "recompute the numbers, trace the hours and rule"),
    (9, "drafts", "growth_coach", True, "draft the posts and messages the ruling upheld"),
    (10, "payslip", "payroll", True, "build the payslip once from the saved numbers"),
    (10, "confirm_payslip", "auditor", True, "confirm the review list reached the payslip"),
)

REMINDER = ('Reply with exactly one JSON object and no other text: either '
            '{"actions": [{"tool": "<name>", "args": {}}], "why": "<one sentence>"} '
            'or {"finished": true, "report": "<short report>"}.')
DATE_PREFIX = re.compile(r"\s*(\d{4}-\d{2}-\d{2})\s*[:,]?\s+(.*)", re.S)
MONEY = re.compile(r"RM\s?(-?\d[\d,]*(?:\.\d+)?)")
HOURS = re.compile(r"(-?\d+(?:\.\d+)?)\s*(?:hours|hour|minutes|minute)\b")


def _default_ask():
    from app import model
    return model.ask


def _read_json(text: str):
    """The first JSON object in the model's text, or None."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", text).strip()
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else None
    except ValueError:
        pass
    start = text.find("{")
    while start != -1:
        try:
            value, _ = json.JSONDecoder().raw_decode(text[start:])
            if isinstance(value, dict):
                return value
        except ValueError:
            pass
        start = text.find("{", start + 1)
    return None


def _trace(workspace, facts, agent, entry):
    """Keep what the agent asked for and what it got back, one JSON line per turn."""
    path = Path(workspace) / "audit" / facts["week"] / ("trace_%s.jsonl" % facts["date"])
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(entry, agent=agent, step=facts["step"]), ensure_ascii=True) + "\n")


def _run_agent(workspace, agent, facts, ask):
    """One agent, one step. Returns (status, note, the commands that passed)."""
    prompt = (PROMPTS / (agent + ".md")).read_text(encoding="utf-8")
    if facts.get("unfinished"):
        task = ("You are in the step named \"%s\". You answered finished, but this is still missing: %s. "
                "Do not start the step again. Do only what is missing, check each result, then reply finished. "
                "Facts: %s" % (facts["step"], facts["unfinished"], json.dumps(facts, ensure_ascii=True)))
    else:
        task = ("Do only the step named \"%s\" now. Follow the section \"Step: %s\" of your instructions "
                "from its first line to its last, then reply finished. Do not do any other step. Facts: %s"
                % (facts["step"], facts["step"], json.dumps(facts, ensure_ascii=True)))
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": task}]
    reminded = 0
    ran = set()
    for _ in range(TURN_LIMIT):
        try:
            text = ask("reason", messages)
        except Exception as error:  # a model failure stops the step, never the program
            if "empty answer" in str(error) and reminded < REMINDERS:
                reminded += 1
                messages.append({"role": "user", "content": "Your last reply was empty. " + REMINDER})
                continue
            return "failed", "the model could not answer: %s" % (str(error) or type(error).__name__), ran
        reply = _read_json(text)
        if reply and "tool" in reply and "actions" not in reply:
            reply = {"actions": [reply]}  # one bare action is read as a list of one
        actions = reply.get("actions") if reply else None
        _trace(workspace, facts, agent, {"reply": reply if reply else text})
        if reply and reply.get("finished") in (True, "true"):
            return "done", str(reply.get("report", "")).strip(), ran
        if not isinstance(actions, list) or not actions:
            if reminded >= REMINDERS:
                return "failed", "the agent did not answer in the agreed format", ran
            reminded += 1
            messages += [{"role": "assistant", "content": text},
                         {"role": "user", "content": REMINDER}]
            continue
        results = []
        for action in actions:
            if not isinstance(action, dict):
                results.append({"ok": False, "error": "an action must be an object"})
                continue
            args = action.get("args") if isinstance(action.get("args"), dict) else {}
            tool = action.get("tool")
            if tool in COMMANDS:  # a command named as the tool is read as the lembur tool
                args = dict(args, command=tool)
                if "options" not in args:
                    args["options"] = {key: args.pop(key) for key in list(args)
                                       if key not in ("command", "input", "input_file")}
                tool = "lembur"
            result = tool_layer.run_tool(workspace, agent, tool, args, ask=ask)
            if tool == "lembur" and result.get("ok"):
                ran.add(str(args.get("command")))
            results.append(result)
        _trace(workspace, facts, agent, {"results": results})
        messages += [{"role": "assistant", "content": text},
                     {"role": "user", "content": json.dumps({"results": results}, ensure_ascii=True)}]
    return "failed", "the agent did not finish within %d turns" % TURN_LIMIT, ran


def _plan(steps, facts, ask):
    """Ask the model why tonight needs each step. The rules decide which steps run."""
    listing = [{"name": name, "agent": agent, "purpose": purpose} for _, name, agent, _, purpose in steps]
    system = ("You plan one night of back office work for a student's small business. "
              "From the facts, say in one short sentence why tonight needs each step, "
              "or put it under skip if tonight has nothing for it. "
              'Reply with one JSON object and no other text: '
              '{"steps": [{"name": "<step name>", "agent": "<agent>", "why": "<one sentence>"}], '
              '"skip": [{"name": "<step name>", "agent": "<agent>", "why": "<one sentence>"}]}')
    try:
        reply = _read_json(ask("reason", [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps({"facts": facts, "steps": listing}, ensure_ascii=True)}]))
    except Exception:
        reply = None
    reasons, source = {}, "the fixed list of steps (the model gave no usable plan)"
    if reply and isinstance(reply.get("steps"), list):
        source = "the reasoning model, checked against the rules"
        for item in reply["steps"] + (reply.get("skip") if isinstance(reply.get("skip"), list) else []):
            if isinstance(item, dict):
                reasons[(item.get("name"), item.get("agent"))] = str(item.get("why", "")).strip()
        planned = {(i.get("name"), i.get("agent")) for i in reply["steps"] if isinstance(i, dict)}
        for _, name, agent, _, _ in steps:
            if (name, agent) not in planned:
                reasons[(name, agent)] = (reasons.get((name, agent), "") +
                                          " Added back by the rules: this step runs every time.").strip()
    return reasons, source


def _write_plan(path, date, week, payslip_day, source, rows):
    lines = ["# Plan for the night of %s" % date, "",
             "* **Week**: %s" % week,
             "* **Payslip day**: %s" % ("yes" if payslip_day else "no"),
             "* **Written by**: %s" % source, ""]
    for row in rows:
        lines.append("%d. **%s**, %s: %s" % (row["step"], row["name"], row["agent"], row["why"] or "needed every night"))
        lines.append("   * **Outcome**: %s%s" % (row["status"], (". " + row["note"]) if row["note"] else ""))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _known_figures(workspace, week):
    """Every figure an agent may cite: the saved numbers and the plan values."""
    known = set()

    def walk(value):
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif value not in (None, "", True, False):
            known.add(_plain(str(value)))

    numbers = workspace / "audit" / week / "numbers.json"
    if numbers.is_file():
        walk(json.loads(numbers.read_text(encoding="utf-8")))
    for path in sorted((workspace / "plan").glob("plan_*.csv")):
        with open(path, encoding="utf-8-sig", newline="") as handle:
            for row in csv.reader(handle):
                for cell in row:
                    known.add(_plain(cell))
    return known


def _plain(text: str) -> str:
    """12.50, 12.5 and RM12.50 compare equal; a word stays as it is."""
    text = text.strip().replace(",", "")
    try:
        number = float(text)
    except ValueError:
        return text
    return ("%.2f" % number).rstrip("0").rstrip(".")


def _untraced(workspace, week, files):
    known = _known_figures(workspace, week)
    found = []
    for name in files:
        path = workspace / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for figure in MONEY.findall(text) + HOURS.findall(text):
            if _plain(figure) not in known and figure not in found:
                found.append(figure)
    return found


def _left_in_inbox(workspace):
    return sorted(item.name for item in (workspace / "inbox").iterdir()
                  if item.is_file() and not item.name.startswith("."))


MUST_RUN = {"reconcile": "reconcile", "close_week": "close-week", "hours": "hours",
            "numbers": "numbers", "audit": "numbers-check", "payslip": "payslip"}


def _without_status(workspace):
    path = workspace / "ledger_transactions.csv"
    if not path.is_file():
        return []
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return [row["txn_id"] for row in csv.DictReader(handle) if not row.get("reconciliation_status")]


def _missing(workspace, facts, name, agent, ran):
    """What a finished step should have done and did not. Empty text when all is there."""
    week, date = facts["week"], facts["date"]
    expected = {
        ("intake", "bookkeeper"): ["receipts/%s/message_%s.txt" % (facts["year_month"], date)],
        ("numbers", "payroll"): ["audit/%s/numbers.json" % week],
        ("recommendation", "payroll"): ["boardroom/%s/payroll.md" % week],
        ("recommendation", "growth_coach"): ["boardroom/%s/growth.md" % week],
        ("audit", "auditor"): ["boardroom/%s/ruling.md" % week, "audit/%s/audit_report.md" % week],
        ("payslip", "payroll"): ["payslips/%s.html" % week],
    }.get((name, agent), [])
    gaps = ["%s does not exist yet" % path for path in expected if not (workspace / path).is_file()]
    command = MUST_RUN.get(name)
    if command and command not in ran:
        gaps.append("the lembur command %s has not passed in this step. Run it now with the lembur tool "
                    "and read its result before you answer finished" % command)
    if name == "drafts":
        folder = workspace / "approvals" / week
        if not any(re.match(r"\d+", item.name) for item in folder.iterdir() if item.is_file()):
            gaps.append("no draft was written. Write one file per upheld recommendation into approvals/%s/, "
                        "each name starting with a two digit number, such as 01_instagram_post.md" % week)
    if name == "reconcile":
        open_rows = _without_status(workspace)
        if open_rows:
            gaps.append("these rows still have no status: %s. Resolve each ambiguous row with the resolve command"
                        % ", ".join(open_rows))
    if name == "intake":
        left = _left_in_inbox(workspace)
        statements = [item for item in left if item.lower().endswith(".csv") and "bank_reference" in
                      (workspace / "inbox" / item).read_text(encoding="utf-8-sig", errors="replace")[:200]]
        if statements and "add-bank-lines" not in ran:
            gaps.append("the bank statement has not been added. Send the lembur tool with command add-bank-lines "
                        "and input_file inbox/%s, and check that the result is ok" % statements[0])
        if left and not ({"add-transactions", "add-bank-lines"} & ran):
            gaps.append("no rows were added for the files in inbox (%s). Read each one with read_document "
                        "and add its rows with the lembur tool" % ", ".join(left))
    return "; ".join(gaps)


def _file_leftovers(workspace, facts):
    """Filing is mechanical, so it does not depend on a model: move what intake left in inbox."""
    targets = {}
    ledger = workspace / "ledger_transactions.csv"
    if ledger.is_file():
        with open(ledger, encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                source = (row.get("source_file") or "").replace("\\", "/")
                if source.startswith("receipts/") and ".." not in source:
                    targets[source.rsplit("/", 1)[-1]] = source
    moved = []
    for name in _left_in_inbox(workspace):
        target = workspace / targets.get(name, "receipts/%s/%s" % (facts["year_month"], name))
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            (workspace / "inbox" / name).replace(target)
            moved.append(name)
    return moved


def _append_review(workspace, week, line):
    path = workspace / "audit" / week / "review_items.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
    if line not in existing:
        path.write_text("\n".join(existing + [line]) + "\n", encoding="utf-8")


def _summary(workspace, week, payslip_day, rows, failed):
    figures = {"hourly_rate_rm": "", "take_home_rm": "", "hours_total": ""}
    numbers = workspace / "audit" / week / "numbers.json"
    if numbers.is_file():
        saved = json.loads(numbers.read_text(encoding="utf-8"))
        figures["hourly_rate_rm"] = str(saved.get("hourly_rate_rm") or "")
        figures["take_home_rm"] = str(saved.get("take_home_rm") or "")
        figures["hours_total"] = str((saved.get("hours") or {}).get("total") or "")
    payslip = "payslips/%s.html" % week
    drafts = []
    folder = workspace / "approvals" / week
    if folder.is_dir():
        for item in sorted(folder.iterdir()):
            match = re.match(r"(\d+)", item.name)
            if item.is_file() and match:
                drafts.append({"number": int(match.group(1)), "file": "approvals/%s/%s" % (week, item.name)})
    review = []
    listed = tool_layer.run_tool(workspace, "bookkeeper", "lembur",
                                 {"command": "review", "options": {"week": week}})
    if listed.get("ok"):
        for row in listed["result"].get("transactions", []):
            amount = ("RM" + row["amount_rm"]) if row.get("amount_rm") else "amount not readable"
            review.append("%s, %s, %s, %s: %s" % (row.get("txn_id", ""), row.get("date", ""),
                                                 row.get("reconciliation_status", ""), amount,
                                                 row.get("description", "")))
        review += [line.lstrip("* ").strip() for line in listed["result"].get("review_items", []) if line.strip()]
    return {
        "week": week,
        "payslip_day": payslip_day,
        "steps": [{key: row[key] for key in ("step", "name", "agent", "status", "note")} for row in rows],
        "figures": figures,
        "payslip": payslip if (workspace / payslip).is_file() else "",
        "drafts": drafts,
        "review": review,
        "failed": failed,
    }


def run_night(workspace, date, message, ask=None):
    """Run one night for one student and return the night summary."""
    workspace = Path(workspace)
    ask = ask or _default_ask()
    message = message if isinstance(message, str) else ""
    prefixed = DATE_PREFIX.fullmatch(message)
    if prefixed:  # demo replay: a message that starts with a date runs as that night
        date, message = prefixed.group(1), prefixed.group(2)

    day = tool_layer.run_tool(workspace, "bookkeeper", "calendar", {"date": date})
    if not day.get("ok"):
        return {"week": "", "payslip_day": False, "steps": [],
                "figures": {"hourly_rate_rm": "", "take_home_rm": "", "hours_total": ""},
                "payslip": "", "drafts": [], "review": [],
                "failed": {"step": 0, "reason": "The date of the night could not be read."}}
    week, payslip_day = day["week"], bool(day["is_payslip_day"])
    year_month = date[:7]
    for folder in ("inbox", "plan", "payslips", "receipts/" + year_month,
                   "audit/" + week, "boardroom/" + week, "approvals/" + week):
        (workspace / folder).mkdir(parents=True, exist_ok=True)

    inbox = [("inbox/" + item.name) for item in sorted((workspace / "inbox").iterdir())
             if item.is_file() and not item.name.startswith(".")]
    facts = {"date": date, "week": week, "year_month": year_month, "payslip_day": payslip_day,
             "message": message, "inbox_files": inbox}
    steps = [step for step in STEPS if payslip_day or not step[3]]
    issued = any((workspace / "payslips" / (week + suffix)).is_file() for suffix in (".html", ".pdf"))
    if issued:  # the week's payslip is out: only intake and reconciliation stay open (section 4)
        steps = [step for step in STEPS if step[1] in ("intake", "reconcile")]

    reasons, source = _plan(steps, facts, ask)
    rows = [{"step": number, "name": name, "agent": agent, "why": reasons.get((name, agent), ""),
             "status": "waiting", "note": ""} for number, name, agent, _, _ in steps]
    plan_path = workspace / "audit" / week / ("plan_%s.md" % date)
    _write_plan(plan_path, date, week, payslip_day, source, rows)

    failed = ""
    for row in rows:
        if failed:
            row["status"] = "skipped"
            continue
        step_facts = dict(facts, step=row["name"])
        status, note, ran = _run_agent(workspace, row["agent"], step_facts, ask)
        gap = _missing(workspace, step_facts, row["name"], row["agent"], ran) if status == "done" else ""
        for _ in range(SEND_BACKS):  # the step said finished but its work is not there
            if not gap:
                break
            status, note, again = _run_agent(workspace, row["agent"], dict(step_facts, unfinished=gap), ask)
            ran |= again
            gap = _missing(workspace, step_facts, row["name"], row["agent"], ran) if status == "done" else ""
        if gap and row["name"] == "drafts":
            note = (note + " No draft was written.").strip()
        elif gap:
            status, note = "failed", "the step ended without its result: " + gap
        if status == "done" and row["name"] == "intake":
            moved = _file_leftovers(workspace, step_facts)
            if moved:
                note = (note + " The runner filed: " + ", ".join(moved) + ".").strip()
        if status == "done" and row["name"] in ("recommendation", "audit"):
            files = {"payroll": ["boardroom/%s/payroll.md" % week],
                     "growth_coach": ["boardroom/%s/growth.md" % week],
                     "auditor": ["boardroom/%s/ruling.md" % week]}[row["agent"]]
            wrong = _untraced(workspace, week, files)
            if wrong:  # sent back once to the agent that wrote it
                status, note, _ = _run_agent(workspace, row["agent"], dict(
                    facts, step=row["name"], fix_figures=wrong,
                    instruction="These figures are not in numbers.json or the plan. Rewrite the file "
                                "using only figures copied from audit/%s/numbers.json or the plan files." % week), ask)
                still = _untraced(workspace, week, files)
                if status == "done" and still:
                    _append_review(workspace, week, "* %s: %s cites a figure that could not be traced to the saved numbers: %s"
                                   % (date, files[0], ", ".join(still)))
                    note = (note + " Untraced figures put on the review list.").strip()
        row["status"], row["note"] = status, note
        if status == "failed":
            failed = {"step": row["step"],
                      "reason": "The %s could not finish the step \"%s\". Nothing was guessed, and what was "
                                "recorded before it is saved. Send your message again to retry."
                                % (row["agent"].replace("_", " ").capitalize(), row["name"].replace("_", " "))}
            _append_review(workspace, week, "* %s: the night stopped at %s (%s): %s" % (date, row["name"], row["agent"], note))
        _write_plan(plan_path, date, week, payslip_day, source, rows)

    _write_plan(plan_path, date, week, payslip_day, source, rows)
    return _summary(workspace, week, payslip_day, rows, failed)
