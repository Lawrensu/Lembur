# Lembur

> **Kau tidur, kami lembur.** (You sleep, we do the overtime.)

An AI back office team on Tencent WorkBuddy that tells student founders what they really earn per hour of their time, before they start (**Day Zero**) and every week after (**Night Shift**), and drafts the changes that would earn them more.

Hackerdorm × BuilderX, Track 2 (Agentic Solutions, Tencent WorkBuddy).

---

## How it works

1. **Day Zero, once**: the student describes the business idea. The agents return a plan file with prices, costs, minutes per unit and a predicted hourly rate.
2. **Every night**: the student sends one Telegram message and drops receipts, order screenshots and the bank statement into a folder.
3. **Bookkeeper**: reads the documents, files them and records each transaction.
4. **Reconciliation**: a deterministic tool matches transactions against the bank statement and flags duplicates, gaps and mismatches.
5. **Payroll**: works out the hours from what was sold and what the message says, then the take home and the hourly rate.
6. **Payslip day, Sunday night**: Payroll and the Growth coach argue for opposing changes. The Auditor rechecks the numbers and rules.
7. **Morning**: the student gets a payslip and a set of drafted posts and messages waiting for approval.
8. **Loop**: the student approves drafts, or replies with a correction that updates the plan for the next night.

## What it does

* **Weekly payslip**: the real hourly rate, in words anyone understands.
* **Hours without a timesheet**: estimated from orders and messages, corrected with one reply.
* **Profit per hour for each product**: shows which product pays and which one costs.
* **Plan versus reality**: every payslip is compared against the Day Zero plan.
* **Open debate**: agents with conflicting objectives, and an Auditor who rules on the numbers.
* **Drafted actions**: posts and supplier messages are prepared, and nothing is sent without approval.
* **Traceable books**: every ledger row links to the receipt behind it.
* **No estimated numbers**: every figure is calculated by a deterministic tool, never by a model.

## Read in this order

1. **`docs/PLAN.md`**: product, scope, validation, roles and schedule.
2. **`docs/SYSTEM_DESIGN.md`**: data, tools, agents, workflows and outputs.

* **Both files are the source of truth**: every skill, tool and template traces back to them.
* **Not in either file**: ask the team, do not assume.

## Repository layout

```
docs/PLAN.md            master plan
docs/SYSTEM_DESIGN.md   system design
skills/                 one folder per agent: bookkeeper, payroll, growth_coach, auditor
workspace/              the folder WorkBuddy reads and writes (design section 3.1)
data/demo/              demo inputs: plan file, inbox files, nightly messages (Role B)
data/answer_key/        answer key and expected ledger (Role B)
submission/             final slides, video and documentation
```

* **`skills/`**: [confirm] where WorkBuddy stores skills and whether they can be exported here, so the team shares one copy.
* **`workspace/`**: starts empty. Runs fill it with the ledger, payslips, boardroom files and drafts.
* **Plan files, CSV**: `workspace/plan/plan_products.csv`, `workspace/plan/plan_channels.csv`, `workspace/plan/plan_assumptions.csv`, `workspace/plan/plan_change_log.csv`.
* **Ledger files, CSV**: `workspace/ledger_transactions.csv`, `workspace/ledger_bank_lines.csv`, `workspace/ledger_hours.csv`.
* **Demo and answer key**: Sharon delivers the same plan file names in `data/demo/` and ledger file names in `data/answer_key/`. CSV is decided; the adapter retains `.xlsx` support for later.

## Team

* Lawrence Lian Anak Matius DIng
* Sharon
* Damian

## Roles

* **A. Builder (Law)**: WorkBuddy workflow, agent skills and instructions, receipt extraction, reconciliation, trigger, payslip and deck output.
* **B. Data and business (Sharon)**: persona, demo dataset, answer key, expected ledger, hand written plan file, Day Zero (confirmed owner), documentation.
* **C. Design and story (Damian)**: agent identities, payslip and board meeting look, pitch slides, video script, recording and editing.
* **Order of work and checkpoints**: PLAN sections 13 and 14.


## Branches

* **`main`**: production. Only receives merges from `dev`.
* **`dev`**: integration. Everyone's work merges here first, and it must run end to end before it goes to `main`.
* **`dev-law`, `dev-sharon`, `dev-damian`**: personal working branches. Pull from `dev` often and open a pull request back into `dev`.

Getting started:

```
git clone https://github.com/Lawrensu/Lembur.git
cd Lembur
git checkout dev-<your name>
```

## Repo rules

* **Demo data only**: no real receipts, bank statements or personal details go in this repository.
* **No secrets**: API keys and account tokens stay out of the repository.
* **Small commits, frequent pulls**: pull `dev` into your branch before opening a pull request, so conflicts surface early.
