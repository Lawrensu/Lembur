# Lembur skills

One folder per agent. Each holds a `SKILL.md` with that agent's instructions, written so that WorkBuddy can run the agent as a skill. The design behind them is `docs/SYSTEM_DESIGN.md`, sections 5 and 6.

* **What this folder is now**: the product runs the agents from `prompts/` through its own runner (design section 6.4). These skill files are where those instructions were first shaped and rehearsed.
* **Why it stays**: it is the fallback if the runner is not ready (PLAN section 15), and it is what the recorded WorkBuddy run uses (PLAN section 12, proof 5).
* **When it goes**: after the runner passes the comparator (design section 8).

* `bookkeeper/`: reads the message and the inbox, files documents, adds and reconciles rows.
* `payroll/`: applies corrections, builds hours and numbers, writes its recommendation, builds the payslip.
* `growth_coach/`: writes the growth recommendation, drafts posts and messages, handles "approve N". In the product the bot handles "approve N".
* `auditor/`: rechecks the numbers, traces the hours, rules, confirms the payslip.

## Order of a Night Shift run in WorkBuddy

Every command is run from the repository root. `workspace/` is the only folder the agents write to, apart from input files in the system temporary folder. The roles run one after another in the same task, and the files in `workspace/` are the handover between them.

* **Every night**
  1. **Bookkeeper**: intake, filing, reconciliation.
  2. **Payroll**: corrections, hours, numbers.
* **Payslip day adds**, the Sunday that closes the week
  1. **Bookkeeper**: closes the week and classifies the new rows, before Payroll starts.
  2. **Payroll and the Growth coach**, at the same time: `payroll.md` and `growth.md`.
  3. **Auditor**: numbers check, hours trace, `ruling.md`, `audit_report.md`.
  4. **Growth coach**: the drafts in `approvals/<week>/`. They come before the payslip because the payslip points to them.
  5. **Payroll**: the payslip, once.
  6. **Auditor**: confirms the review list reached the payslip.
  7. **Morning message**: the last reply of the run. It says "Your board meeting is ready", gives the hourly rate copied from `numbers.json`, says where the payslip is, and lists the drafts waiting for "approve N".

## Starting a run

* **What a run needs**: the night's date, the student's message, and that night's files in `workspace/inbox/`.
* **Before the first night**: `python -B data/test_harness/reset_workspace.py --clean-only` empties the workspace. Then copy the plan files into `workspace/plan/`. For the demo they are `data/demo/plan_*.csv`.
* **After the last night**: `python -B data/test_harness/compare_outputs.py` compares the run with the answer key.

## Installing the skills in WorkBuddy

On Law's machine WorkBuddy reads skills from the user folder `.workbuddy-ai/skills/<name>/SKILL.md`. Copy each of the four folders there, named after the `name` at the top of its `SKILL.md`. A skill run of one of our scripts passed there on 10 October. The four agent skills have not been run inside WorkBuddy yet: that is proof 5 in PLAN section 12.
