# Lembur

> **Kau tidur, kami lembur.** (You sleep, we do the overtime.)

A back office team in a student's chat app. She sends one message and her receipts before bed. In the morning she gets a payslip that shows what she really earned per hour of her time, and drafts of the changes that would earn her more.

Hackerdorm × BuilderX, Track 2 (Agentic Solutions).

---

## How it works

1. **One message before bed**: the student sends the bot a short message with her receipt photos, order screenshots and, on Sunday, her bank statement. She installs nothing.
2. **A plan for the night**: the runner writes down which steps tonight needs and why.
3. **Bookkeeper**: reads the documents, files them and records each transaction.
4. **Reconciliation**: a deterministic tool matches transactions against the bank statement and flags duplicates, gaps and mismatches.
5. **Payroll**: works out the hours from what was sold and what the message says, then the take home and the hourly rate.
6. **Payslip day, Sunday night**: Payroll and the Growth coach argue for opposing changes. The Auditor recomputes the numbers and rules.
7. **Morning**: the bot sends the payslip and the drafted posts and messages waiting for approval.
8. **Loop**: the student replies "approve 2", or replies with a correction that updates the plan for the next night.

## What it does

* **Weekly payslip**: the real hourly rate, in words anyone understands.
* **Hours without a timesheet**: estimated from orders and messages, corrected with one reply.
* **Profit per hour for each product**: shows which product pays and which one costs.
* **Plan versus reality**: every payslip is compared against the plan.
* **Open debate**: agents with conflicting objectives, and an Auditor who rules on the numbers.
* **Drafted actions**: posts and supplier messages are prepared, and nothing is sent without approval.
* **Traceable books**: every ledger row links to the receipt behind it.
* **No estimated numbers**: every figure is calculated by a deterministic tool, never by a model.

## How it is built

* **Three layers**: a chat bot, a runner and deterministic tools (design section 1).
* **Agents act through tools**: each of the four agents works in a short loop. It asks for a tool, the runner runs it, and the agent reads the result and decides the next step (design section 6.4).
* **Two model roles**: one model reasons and one reads images. Both come from the model gateway the organisers provided (design section 6.3).
* **Standard library only**: Python 3.13 with no third party package and no agent framework.
* **WorkBuddy is our build platform**: the code, the dataset and the story were built with it. It is not part of the running product (PLAN section 11).

## Where things stand

* **Built and tested**: the deterministic tools, the tool layer, the model module, the runner, the four agent prompts, the Telegram bot, the payslip command and template, the demo dataset, the answer key and the comparator.
* **Proved with the real models**: the reading model reads a receipt image, one night runs as agents, and the whole demo week replayed through the runner matches the answer key with no difference (PLAN section 12, proofs 1, 2 and 4).
* **Not run yet**: the full round trip through the chat with the real runner, and the recorded run inside WorkBuddy (proofs 3 and 5).
* **Run a night yourself**: copy `.env.example` to `.env`, fill it in, then start the bot with `python -B -m app.bot` from the repository root.

## Read in this order

1. **`docs/PLAN.md`**: product, scope, validation, proofs, roles and schedule.
2. **`docs/SYSTEM_DESIGN.md`**: data, tools, agents, workflows and outputs.

* **Both files are the source of truth**: every tool, prompt and template traces back to them.
* **Not in either file**: ask Law, do not assume.

## Repository layout

```
docs/PLAN.md            master plan
docs/SYSTEM_DESIGN.md   system design
tools/                  deterministic tools and their tests (design section 4)
app/                    model module, tool layer, runner and bot (design section 6.3)
prompts/                one instruction file per agent (design section 6.4)
skills/                 the same four agents as WorkBuddy skills: the fallback, and the source of the prompts
workspace/              one student's files, used by the tests and the demo replay (design section 3.1)
data/demo/              demo inputs: plan files, inbox files, nightly messages (Role B)
data/answer_key/        answer key and expected ledger (Role B)
data/test_harness/      compares a finished run with the answer key, and resets the workspace (Role B)
submission/             payslip template, deck, video script, question and answer sheet, evidence of the build
```

* **`workspace/`**: starts empty. A run fills it with the ledger, payslips, boardroom files and drafts.
* **Plan files, CSV**: `workspace/plan/plan_products.csv`, `workspace/plan/plan_channels.csv`, `workspace/plan/plan_assumptions.csv`, `workspace/plan/plan_change_log.csv`.
* **Ledger files, CSV**: `workspace/ledger_transactions.csv`, `workspace/ledger_bank_lines.csv`, `workspace/ledger_hours.csv`.
* **Demo and answer key**: the same plan file names live in `data/demo/` and the same ledger file names in `data/answer_key/`. These CSV files are the source of truth for the demo data.
* **Check the tools**: `python -B -m unittest discover -s tools/tests -p "test_*.py"` from the repository root. It needs no installed package.
* **Check a run**: `python -B data/test_harness/compare_outputs.py` compares `workspace/` with the answer key (PLAN section 10).

## Team

* Lawrence Lian Anak Matius DIng
* Sharon
* Damian

## Roles

* **A. Builder (Law)**: integration and the final say on the build.
* **B. Data and business (Sharon)**: the demo dataset, the answer key, the comparator, checking every run against the key.
* **C. Design and story (Damian)**: agent identities, the payslip template, the wording of the bot's replies, the deck, the video.
* **The remaining build is three packages** (PLAN section 13)
  1. **Backend**, Sharon, first: `app/tools.py` and `app/model.py`.
  2. **Agent orchestration**, Law: `app/runner.py` and `prompts/`.
  3. **Telegram connection**, Damian: `app/bot.py`.
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
* **No secrets**: the model key and the bot token live in a `.env` file that git ignores. They never appear in a file, a prompt, a log or a commit.
* **Small commits, frequent pulls**: pull `dev` into your branch before opening a pull request, so conflicts surface early.
* **Pull requests go into `dev`**: never into `main`. `main` only receives `dev` after an end to end run.
* **Authors**: the three team members are the only contributors named in commits, files and pull requests. No attribution lines.
* **WorkBuddy is named truthfully**: it is the platform we build with. The docs, slides and video say what it really did, and nothing more.
* **Docs style**: point form, no tables, no dashes in prose.
* **No installs without asking**: a new package or tool needs Law's approval first.
* **Keep it simple**: add no feature, file or field that is not written in the docs. Ask first.
