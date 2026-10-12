# System Design for Lembur

This document describes the purpose, architecture and rules of Lembur, a back office team in a student's chat app.

* **Part one, the story**: [Problem](#problem), [Positioning](#positioning), [Tool Stack](#tool-stack), [Repository Structure](#repository-structure), [System Functionality](#system-functionality), [Application Layers](#application-layers), [Flow](#flow), [Key Decisions](#key-decisions).
* **Part two, the rules**: [Conventions](#conventions), [Data Model](#data-model), [Deterministic Tools](#deterministic-tools), [Agents](#agents), [Runtime](#runtime), [Outputs](#outputs). The code and the tests implement these exactly.
* **Part three, the evidence**: [Validation](#validation), [Proofs](#proofs), [How WorkBuddy Was Used](#how-workbuddy-was-used).
* **What is left**: [TODO (future)](#todo-future), [Open Questions](#open-questions).
* **To run it**: [Getting started](GETTING_STARTED.md).

Lembur consists of:

* **Bot**: `app/bot.py`, the front door in Telegram, see [Chat](#chat).
* **Runner**: `app/runner.py`, `app/tools.py`, `app/model.py` and `prompts/`, see [Runtime](#runtime).
* **Tools**: `tools/`, the deterministic commands, see [Deterministic Tools](#deterministic-tools).

---

## Problem

* **The user**: a student running a side business while studying. She sells through Instagram, Telegram and campus bazaars, and is paid in cash and bank transfers with screenshots as proof.
* **The pain**: she does not know whether the business makes money, least of all per hour of her time.
* **Why it happens**: the data is scattered and informal, nobody does data entry at 2am, and nobody tracks their own hours.
* **The brief**: Hackerdorm × BuilderX, Track 2 (Agentic Solutions). How can AI agents solve real world problems by understanding goals, planning workflows, using tools and delivering complete end to end outcomes?
* **Our answer**: she sends one message and her receipts before bed. In the morning she gets a payslip that shows what she earned per hour, always paired with a raise plan.
* **What the brief asks of an agent, and where Lembur shows it**
  * **Understanding the goal**: the Bookkeeper and Payroll read the nightly message.
  * **Planning tasks**: the plan for the night.
  * **Executing actions**: agents act through tools.
  * **Collaborating and validating**: Payroll argues against the Growth coach, and the Auditor rules.
  * **Integrating results**: the payslip.
  * **Delivering the final outcome**: the morning message with the payslip file.
* **What the brief rewards**: real user value, an agentic workflow, meaningful use of WorkBuddy, end to end execution, and usable, verifiable results.
* **Design principle**: turn business numbers into human truths. Write "RM3.10 an hour", not "18% margin".
* **The name**: Lembur is Malay for working overtime. The agents do the overtime while the student sleeps.
* **Result**: first runner up at the hackathon.

## Positioning

* **Alongside, not against**: Lembur runs beside the order, accounting and payment tools a small business already uses. Books can live anywhere. We own time and decisions.
* **Plumbing, not pitch**: receipt reading, reconciliation and chat input exist everywhere. We build them because the product needs them.
* **What is ours**: hours inferred from orders and messages, a payslip anyone understands, agents with conflicting objectives debating in the open, plan versus reality, and actions drafted for approval.
* **Not a general assistant**: a general assistant does money arithmetic with the model, needs set up, and gives an hourly rate only to someone who knows to ask. Lembur never lets a model count, installs nothing, and has an opinion.
* **Honest limits**: hours are estimates, only as good as the minutes per unit in the plan. Unplanned time, such as failed batches or supply runs, is missed.

## Tool Stack

* **Product**
  * Python 3.12 or newer, standard library only: nothing to install, no agent framework.
  * Telegram Bot API over plain HTTPS: the bot asks Telegram for new messages, so it needs no public address.
  * CSV files: the ledger and the plan, one file per sheet, readable in any spreadsheet.
  * One HTML template: the payslip, self contained so it looks the same offline.
* **AI**
  * Model gateway from the organisers: one HTTPS address for every model call.
  * Reasoning model (`GPT-OSS 120B` in the demo): drives the four agents.
  * Reading model (`Qwen 27B` in the demo): turns one image into text.
  * Which model fills which role: configuration, not code.
* **Build**
  * `unittest`: 242 tests that need no key and no network.
  * WorkBuddy: the platform the team built with. It is not part of the running product.

## Repository Structure

```
app/
  bot.py        Telegram front door
  runner.py     plan for the night, agent loop, order of steps
  tools.py      tool layer: runs a tool for an agent, checks who may use what
  model.py      the only code that calls a language model
  tests/        tests with a scripted model
prompts/        one instruction file per agent
tools/          deterministic commands (lembur.py) and their tests
workspace/      one student's files, used by the tests and the demo replay
data/
  demo/         demo inputs: plan files, inbox files, nightly messages
  answer_key/   expected ledger and expected figures
  test_harness/ replay, comparator, reset and mutation test
submission/     payslip template, story notes, evidence of the build
docs/           this file and getting started
```

## System Functionality

* **Student**
  * Send receipt photos, order screenshots and, on Sunday, a bank statement as files.
  * Send one message about the day, including any event hours.
  * Get a payslip every Sunday night with the real hourly rate.
  * Ask for `payslip` or `review` at any time.
  * Reply `approve N` or `skip N` to each drafted post or message.
  * Correct an assumption with one reply, for example "keychains take me 15 minutes".
* **System, every night**
  * Read each document and record one row per sale or expense.
  * File each document so every ledger row links to its receipt.
  * Match rows against the bank statement and flag duplicates, gaps and mismatches.
  * Estimate hours from what was sold and what the message says.
  * Compute take home, hourly rate and profit per hour by product.
* **System, on payslip day**
  * Turn leftover bank lines into rows, so a missing receipt is not lost.
  * Payroll and the Growth coach argue for opposing changes.
  * The Auditor recomputes the numbers and rules.
  * Draft the posts and supplier messages the ruling upheld.
  * Build the payslip and send it with the drafts.

Notes:

* **Not built**: Day Zero (planning a new business), the payslip as a PDF, WhatsApp, voice notes, automatic posting, hosting. See [TODO (future)](#todo-future).
* **Out of scope**: a web app or dashboard, late payment tracking, helper features, integrations with accounting or order tools.

## Application Layers

Cross sectional view of the application:

1. **Telegram**: the whole interface. The student needs only a chat app.
2. **Bot**, `app/bot.py`: receives text and files, sends replies and files. It never calls a model.
3. **Runner**, `app/runner.py`: writes the plan for the night and runs the four agents in order.
4. **Agents**, `prompts/`: Bookkeeper, Payroll, Growth coach and Auditor. Each works by asking for tools.
5. **Tool layer**, `app/tools.py`: runs a tool for an agent and checks which agent may use what.
6. **Tools**, `tools/lembur.py`: the only code that calculates or writes a figure.
7. **Workspace**: one folder per student with the ledger, the plan, the receipts and every output.
8. **Model gateway**, through `app/model.py`: the reasoning model and the reading model.

* **Agents read and argue, tools count**: agents read documents, decide unclear cases and write recommendations. Every match, total, hours figure and rate comes from a deterministic tool.
* **Enforced by the code, not by trust**: an agent has no other way to act than the tools the runner gives it.

## Flow

### Every night

0. **Trigger**: the student sends her files and one text message. The bot saves each file into `inbox/` and replies that the night shift is starting.
1. **Plan for the night**: the runner asks the reasoning model which steps tonight needs and why, then checks the answer against the rules. A step the model left out is added back. The plan is saved as `audit/<week>/plan_<date>.md`.
2. **Step 1, intake**, Bookkeeper: the message is saved, each document is read, its rows are recorded and it is filed.
3. **Step 2, reconcile**, Bookkeeper: the reconciliation tool gives every row a status.
4. **Step 3, corrections**, Payroll: a correction in the message is applied to the plan.
5. **Step 4, hours**, Payroll: the hours tool builds the hours lines.
6. **Step 5, numbers**, Payroll: take home, hourly rate and profit per hour are saved to `audit/<week>/numbers.json`.
7. **Reply**: the bot reports the figures so far, labelled as partial for the week.

### Payslip day

The Sunday that closes the week adds steps 6 to 11.

1. **Step 6, close the week**, Bookkeeper: leftover bank lines become rows and are classified. It runs after step 2 and before step 4, so the hours and the numbers include those rows.
2. **Step 7, recommendations**, Payroll and Growth coach: `payroll.md` argues for the hourly rate, `growth.md` argues for sales.
3. **Step 8, audit and ruling**, Auditor: the numbers are recomputed and compared with the saved file, the hours are traced, then `audit_report.md` and `ruling.md` are written.
4. **Step 9, drafts**, Growth coach: posts and supplier messages go to `approvals/<week>/`. They come before the payslip because the payslip points to them.
5. **Step 10, payslip**, Payroll: `payslips/<week>.html` is built once from the saved numbers. The Auditor then confirms the review list reached it.
6. **Step 11, morning message**, bot: "Your board meeting is ready", the hourly rate, the payslip file, the draft files and the review list.

### Approval and correction

* **Approve**: "approve 2" moves draft 2 from `approvals/<week>/` into `approvals/<week>/approved/`. "skip 2" leaves it where it is. The bot confirms either way.
* **A file move, nothing more**: no agent and no model is involved. The system never posts or sends a draft. The student sends an approved draft herself.
* **Correct**: a reply such as "keychains take me 15 minutes" updates the plan on the next night, from that date forward.

### When something goes wrong

* **A step fails**: the runner stops the night at that step, records the reason in the plan and in `audit/<week>/review_items.md`, and the bot tells the student in plain words. Nothing is guessed to keep going.
* **A week already issued**: once the payslip exists, only intake and reconciliation stay open for that week.
* **Unclear means flagged**: anything an agent cannot decide goes on the review list, not into the totals as a guess.

## Key Decisions

* **Our own chat bot, not hosted in WorkBuddy**: the organisers relaxed the rule on 10 October, and a student will not install an assistant.
* **Telegram first**: the bot asks for new messages, so the demo needs no public address. WhatsApp needs a business account.
* **The chat is the whole interface**: a web app pulls build time into screens and logins.
* **Models never count**: every figure comes from a tested tool and is checked against an answer key.
* **Four agents only**: an agent exists only where it needs different tools, different context or a conflicting objective. Timekeeping is part of Payroll. Reconciliation is a tool.
* **Our own runner, standard library only**: no agent framework and no third party package, so the product depends only on what the organisers provided.
* **Two model roles from one gateway**: swapping a model is a change to `.env`.
* **A written plan each night**: it is the record of what was decided and done.
* **A step is checked, not trusted**: models answer differently from run to run, so the runner confirms each step's command passed and its file exists.
* **CSV, not spreadsheets**: it works with the standard library and opens in Excel.
* **Weeks run Monday to Sunday**: the Sunday payslip closes the week and the folders sort.
* **Whole sen and whole minutes inside tools**: rounding happens at display only, halves away from zero, because Python rounds halves differently.
* **Amounts are always positive, with a `type` column**: extraction copies what the receipt shows, and an expense cannot match a sale of the same amount.
* **`cash` and `bank_transfer` only**: an e wallet sale would never appear on the bank statement.
* **A `cash_declared` status**: cash never reaches the bank, and without it every cash sale would bury the real flags.
* **Match by reference, then by amount within one day**: many sales share one price, so a wider window creates ambiguity.
* **Missing receipts surface on payslip day only**: a late receipt is not flagged early.
* **No silent category default**: an expense created from a bank line must be classified by the Bookkeeper.
* **Production counts units sold, not units made**: it mirrors how accounting attaches cost to goods when they sell, so a big production weekend does not distort one week's rate.
* **Stated hours for events only**: stated production time describes units made, so applying it would double count.
* **Two bases for money, on purpose**: take home uses what was paid, product profit uses plan costs, because a bulk receipt cannot be split by product.
* **Shared hours are not allocated to products**: any split would be arbitrary.
* **The payslip is built once**: there is no draft payslip. The Auditor compares a recomputation with the saved numbers.
* **An HTML payslip filled by a command**: no model types a figure into it.
* **Approval is a reply and a file move**: nothing leaves without the student.
* **Demo inputs live outside `workspace/`**: the workspace is wiped before each recorded run.
* **The answer key was checked twice**: a second, independent calculation had to agree before anyone built against it.
* **Agent style**: professional colleagues with role titles, decided by Damian.

---

# Rules

The exact rules behind the story above. A rule changes here first, then in the code.

## Conventions

* **Dates**: `YYYY-MM-DD`, Malaysia time.
* **Week**: Monday to Sunday, written as an ISO week. `2026-W41` is 5 to 11 October 2026. Used wherever a path shows `<week>`.
* **Month folder**: `YYYY-MM`, wherever a path shows `<year_month>`.
* **Payslip day**: Sunday night. It closes that week.
* **Money**: ringgit with two decimals in files. Tools calculate in whole sen.
* **Time**: whole minutes in files and tools. Hours exist only on display.
* **Rounding**
  * Applied at display only, with one exception in [Numbers](#numbers) (channel fees).
  * Halves round away from zero: 304.5 becomes 305.
  * Hours show one decimal, money two decimals, percentages whole numbers.
  * Python `round()` treats halves differently. Tools apply the rule above explicitly.
* **Empty cell**: means not known or not applicable. Never write 0 or "n/a" in its place.
* **IDs**: `P01` for products, `T0001` for transactions, `H0001` for hours entries. A transaction ID is never reused.
* **Person**: `person_1` is the student.
* **Assumption reference**: names one plan value.
  * `products.<product_id>.<column>`, for example `products.P01.minutes_per_unit`
  * `channels.<channel>.<column>`
  * `assumptions.<column>`
* **Message reference**: `message.<date>` names the nightly message of that date, saved at `receipts/<year_month>/message_<date>.txt`.

## Data Model

### Folder layout

Each student has one workspace folder: `workspaces/<chat_id>/` when the bot runs, and `workspace/` for the tests and the demo replay. The layout is the same in both.

```
workspace/
  inbox/                    files the student sent, waiting for intake
  plan/plan_products.csv    baseline products
  plan/plan_channels.csv    baseline channels
  plan/plan_assumptions.csv baseline assumptions
  plan/plan_change_log.csv  corrections
  ledger_transactions.csv   transactions
  ledger_bank_lines.csv     bank statement lines
  ledger_hours.csv          hours
  receipts/<year_month>/    filed source documents and saved nightly messages
  boardroom/<week>/         payroll.md, growth.md, ruling.md
  audit/<week>/             numbers.json, audit_report.md, intake_log.md, review_items.md,
                            plan_<date>.md, trace_<date>.jsonl
  payslips/<week>.html      weekly payslip, filled from the template
  approvals/<week>/         drafted posts and messages, one file per draft
  approvals/<week>/approved/  drafts the student has approved
```

* **Why this layout**: the Auditor traces numbers to receipts, a reader opens a ledger row and sees the receipt behind it, and the folder is the handoff package if the student moves to accounting software.
* **File format**: CSV only. One file per sheet, named `<book>_<sheet>.csv`. `sheets.load_book` and `sheets.save_book` refuse any other format.
* **Sheets**: row 1 holds the column names exactly as written below, in the order listed.

### Plan files

* **`products`**, one row per product: `product_id`, `name`, `price_rm`, `material_cost_rm`, `packaging_cost_rm`, `minutes_per_unit`. Price, costs and minutes are per unit.
* **`channels`**, one row per sales channel: `channel`, `fee_percent`, `fee_per_order_rm`, `shipping_cost_per_order_rm`, `fulfilment_minutes_per_order`.
  * `channel` is a short lowercase name.
  * `fee_percent` is the share of the sale amount the channel takes.
  * The other three are per order. A value is 0 where there is none.
* **`assumptions`**, one row: `admin_hours_per_week`, `planned_margin_percent`, `target_hourly_rate_rm`.
* **`change_log`**, one row per correction, only ever added: `changed_at`, `field`, `old_value`, `new_value`, `reason`, `source`.
  * `changed_at` is the date of the student's correction message.
  * `field` is the assumption reference of the value changed.
  * `reason` is the student's words. `source` is the message reference.
* **Value in force on a date**: the `old_value` of the earliest `change_log` row for that field with `changed_at` later than the date. If there is none, the value now in the plan sheet.

### Ledger files

* **`transactions`**, one row per sale or expense: `txn_id`, `date`, `type`, `category`, `description`, `product_id`, `quantity`, `amount_rm`, `channel`, `payment_method`, `counterparty`, `reference`, `source_file`, `reconciliation_status`, `bank_reference`, `notes`.
  * `date` is the date on the document.
  * `type` is `income` or `expense`.
  * `category` is `sales`, `materials`, `packaging`, `platform_fees`, `shipping` or `other_expenses`. `sales` is always `income`. Every other category is `expense`.
  * `product_id`, `quantity` and `channel` are for sales rows only. One sales row is one order of one product. `channel` must equal a `channel` in `plan_channels.csv`.
  * `amount_rm` is always positive, and empty only when it cannot be read.
  * `payment_method` is `cash` or `bank_transfer`.
  * `counterparty` and `reference` are copied as written on the document.
  * `source_file` is the workspace path of the filed document or saved message. It is empty for rows created from a bank line.
  * `reconciliation_status` is one of the six values in [Reconciliation](#reconciliation). `bank_reference` names the bank line the row is paired with.
  * `notes` holds the reason for any decision or flag.
  * **Required on every row**: `date`, `type`, `category`, `amount_rm`, `payment_method`. Sales rows also need `product_id`, `quantity` and `channel`.
* **`bank_lines`**, one row per bank statement line: `date`, `description`, `type`, `amount_rm`, `bank_reference`.
  * `type` is `income` for money in and `expense` for money out. `amount_rm` is always positive. `bank_reference` is unique per line.
* **`hours`**, one row per hours line, built by the hours tool: `entry_id`, `date`, `person`, `activity`, `product_id`, `quantity`, `minutes`, `source`, `assumption_ref`.
  * `activity` is `production`, `fulfilment`, `event` or `admin`.
  * `product_id` is for production and fulfilment lines only.
  * `quantity` is units for production and orders for fulfilment, empty otherwise.
  * `source` is `estimate`, `stated` or `corrected`.
  * `assumption_ref` is an assumption reference for `estimate` and `corrected`, and a message reference for `stated`.

## Deterministic Tools

* **Mechanism**: Python scripts in `tools/`. The runner gives the commands of `tools/lembur.py` to the agents as the `lembur` tool.
* **Boundary**: agents pass in what they have read (rows, event durations, corrections). They never calculate.
* **Entry point**: `python -B tools/lembur.py <command> --workspace <workspace folder>`, run from the repository root. Commands return JSON on standard output, exit 0 on success and 1 on failure, without tracebacks. Batch input is a JSON array read with `--input <file>` or `--input -` for standard input.
* **Counted row**: a transaction row counts towards totals and hours unless its status is `duplicate` or its `amount_rm` is empty.
* **Issued week**: either `payslips/<week>.html` or `payslips/<week>.pdf` marks the week as issued. It blocks `hours`, `numbers` and `close-week` for that week, not intake.
* **Review list**: every row dated in the week with status `unmatched`, `duplicate` or `needs_review`, plus every line of `audit/<week>/review_items.md`. `review --week` prints both.
* **Warnings**: `hours` and `numbers` append every returned warning to `audit/<week>/review_items.md`, one line each, never repeating an existing line. A figure is never changed to hide a warning.
* **Payslip command**: `payslip --week <week> --input <JSON file> [--template <file>]` fills the template from `audit/<week>/numbers.json` and writes `payslips/<week>.html`.
  * The input is one JSON object in a file with exactly three keys: `debate_summary`, `ruling` and `raise_plan`.
  * The command adds the review list itself.
  * It works once: it refuses when the payslip already exists.
  * The template defaults to `submission/payslip_template.html`.

### Reconciliation

* **Transaction intake, `add-transactions`**: accepts incomplete rows in Bookkeeper intake order and assigns IDs after the highest stored ID. There is no row deletion command.
  * Refuses a batch carrying `txn_id` or `bank_reference`, even empty, or a `reconciliation_status` other than empty or `needs_review`.
  * Refuses the whole batch if any nonempty `source_file` is already in the ledger, and lists those paths. Several rows from one message in the same new batch are allowed. Reason: retrying cash intake would otherwise count the sales twice.
* **Statement intake, `add-bank-lines`**: an identical stored line is skipped and reported. The same `bank_reference` with different content refuses the whole batch. References must be nonempty and unique.
* **Matching, `reconcile`**: prints ambiguous row IDs with candidate bank lines.
* **Choosing, `resolve --txn-id --bank-reference --reason`**: records a choice, or an empty reference for an undecided row. A reason is required.
* **Classifying, `classify --txn-id --category --reason`**: works on any row the classification gate names. The new category must be known and agree with the row's type. The reason is appended to `notes`.
* **Status values**
  * `matched`: one bank line agrees with the row
  * `ambiguous_resolved`: several bank lines fitted; the Bookkeeper chose one and wrote why
  * `unmatched`: no bank line for this row, or no document for this bank line
  * `duplicate`: a copy of an earlier row
  * `needs_review`: a required field is missing, the amount disagrees with the bank, or the Bookkeeper could not decide
  * `cash_declared`: a cash row; no bank evidence is expected
* **A bank line is used**: when any transaction row carries its `bank_reference`.
* **Reconciliation steps, in order**: each row takes the first status that applies.
  1. **Validation**: a row already `needs_review` is left untouched. Otherwise the tool sets `needs_review` with a reason if a required field is missing, the category is unknown, category and type disagree, or the payment method is unknown. A mechanical check must not depend on a model.
  2. **Cash**: `payment_method` is `cash` → `cash_declared`.
  3. **Duplicate**: the row equals an earlier row (lower `txn_id`) on `date`, `type`, `amount_rm`, `counterparty` and `reference` → `duplicate`. `notes` names the original row.
  4. **Reference match**: `reference` equals the `bank_reference` of an unused bank line of the same `type`.
     * Amounts equal → `matched`.
     * Amounts differ → `needs_review`. `amount_rm` is set to the bank amount and `notes` keeps both amounts.
     * Either way `bank_reference` is filled.
  5. **Amount match**: candidates are unused bank lines with the same `type`, the same amount, and a date within one day either side of the row's date.
     * Exactly one candidate, and that line is a candidate for no other row → `matched`.
     * No candidate → `unmatched`.
     * Anything else → handed to the Bookkeeper as ambiguous.
  6. **Ambiguous rows**: the Bookkeeper picks a bank line using `counterparty` and `description` → `ambiguous_resolved`, reason in `notes`. If it cannot decide → `needs_review`.
  7. **Leftover bank lines**, on payslip day only: `close-week --week` converts unused bank lines dated inside that week into new transaction rows.
     * Copied from the bank line: `date`, `type`, `amount_rm`, `description`, `bank_reference`.
     * `payment_method` is `bank_transfer`, `source_file` is empty, status is `unmatched`, `notes` says no document was found.
     * Income becomes `sales` with `product_id` empty.
     * An expense is created with an empty `category`. The Bookkeeper classifies it from the description before the numbers tool runs. An unclear expense becomes `other_expenses` with a note.
* **Running again**: each run tests rows with an empty status, and rows that are `unmatched` with an empty `bank_reference`. Settled rows are never changed.
* **Known limits**
  * A document that arrives after step 7 turned its bank line into a row is not paired automatically. The late document gets a new row, stays `unmatched` and is on review.
  * A copy of a mismatched receipt arriving on a later run is not caught as a duplicate: the original row's amount was replaced by the bank amount, so the duplicate key no longer agrees. A copy in the same run is caught.

### Hours

* **Command**: `hours --week <week> [--input <events JSON>] [--payslip-day]` rebuilds the open week. Input is optional on nights without an event.
* **Formula**: week hours = production + fulfilment + events + admin, summed from the `hours` lines dated in the week.
* **Production line**: one per date and product, from counted sales rows.
  * `quantity` is the units sold.
  * `minutes` = `quantity` × `minutes_per_unit` in force on that date.
  * `assumption_ref` is `products.<product_id>.minutes_per_unit`.
* **Fulfilment line**: one per date, product and channel, from counted sales rows.
  * `quantity` is the number of orders (rows).
  * `minutes` = `quantity` × `fulfilment_minutes_per_order` in force on that date.
  * `assumption_ref` is `channels.<channel>.fulfilment_minutes_per_order`.
  * No line is written when the minutes are zero.
* **Event line**: one per event stated in a nightly message.
  * The agent passes the date, plus either start and end as 24 hour times or the stated hours as written. The tool computes whole minutes. For "Bazaar 4 to 9" the agent passes `16:00` and `21:00` and the tool returns 300.
  * Choosing am or pm is reading and stays with the agent.
  * When a message gives both clock times and a total, the agent passes the clock times only. The tool rejects an event carrying both forms.
  * An optional `message_date` names the message the event came from. It defaults to the event date.
  * `source` is `stated`. `assumption_ref` is the message reference.
* **Admin line**: one per week, dated that week's Sunday, written with `--payslip-day`.
  * `minutes` = `admin_hours_per_week` in force on that date × 60.
  * `assumption_ref` is `assumptions.admin_hours_per_week`.
* **`source` on production, fulfilment and admin lines**: `corrected` only when a `change_log` row for the line's field has `changed_at` on or before the line date. Earlier lines stay `estimate`.
* **Sales rows without `product_id` or `quantity`**: produce no lines.
* **Events that cannot be used**: a missing or unreadable date, an end time not after the start, a duration that cannot be read, or a date outside the week writes no line and returns one review warning.
* **Event wording**: durations use clock times or plain numeric hours. Text such as "2h30", "half an hour" or "2 jam" goes to review.
* **Stated hours for anything other than events**: not applied. Payroll appends the item to `audit/<week>/review_items.md`.
* **Corrections, `correct-plan --field --new-value --changed-at --reason`**
  * Payroll updates the plan cell and a `change_log` row is added.
  * The new value applies to lines dated on or after `changed_at`. Earlier lines keep the old value.
  * Only three values can be corrected: `minutes_per_unit`, `fulfilment_minutes_per_order`, `admin_hours_per_week`.
* **Running again**: production and fulfilment lines of the open week are rebuilt from the ledger on every run. The admin line is rebuilt only with `--payslip-day`. An event line is written once per stated event. Only open week lines are renumbered, so an ID is stable once its week's payslip is issued.
* **Known limits**: an event reread with a different duration on a rerun adds a second line. Two separate events with the same date, message reference and duration become one line.
* **Worked example** (illustration only)
  * Keychains sold: 30 × 20 minutes = 600
  * Bracelets sold: 6 × 35 minutes = 210
  * Online orders packed: 10 × 5 minutes = 50
  * Bazaars, stated: 360
  * Admin: 2 hours = 120
  * Total: 1,340 minutes, shown as 22.3 hours
  * Hourly rate: RM68.00 ÷ 1,340 × 60 = RM3.04

### Numbers

All figures use counted rows and hours lines dated in the week.

* **Commands**: `numbers --week` saves exactly the computed result to `audit/<week>/numbers.json`. `numbers-check --week` reruns without writing any file and reports equality or the differing top level keys, exiting 1 on a mismatch.
* **Classification gate**: the tool refuses to run while any counted row has an empty category, an unknown category, or a category that disagrees with its type. It prints the affected row IDs and reasons. Rows that are not counted never block the gate.
* **Saved numbers**: Payroll, the Growth coach and the Auditor copy figures only from `numbers.json`.
* **Category totals**: the sum of `amount_rm` for each category.
* **Take home**: sales total minus the totals of the five expense categories.
* **Hourly rate**: take home ÷ week minutes × 60. Not shown when the week has no minutes.
* **Product profit**, for each product
  * **Revenue**: the sum of its sales rows.
  * **Unit costs**: units sold × (`material_cost_rm` + `packaging_cost_rm`).
  * **Channel costs**: for each of its sales rows, `amount_rm` × `fee_percent` ÷ 100 (rounded to the sen on each row) + `fee_per_order_rm` + `shipping_cost_per_order_rm`, using the row's channel.
  * **Profit**: revenue minus unit costs minus channel costs.
  * **Direct minutes**: its production and fulfilment lines.
  * **Profit per hour**: profit ÷ direct minutes × 60.
  * **Loses money**: profit is below zero.
* **Two bases, on purpose**
  * Take home uses ledger rows: what was actually paid, traceable to a receipt.
  * Product profit uses plan costs: a bulk materials receipt cannot be split by product.
  * Product profits therefore do not add up to take home. Do not try to reconcile them.
* **Shared hours**: event plus admin minutes. They are not allocated to any product and appear as their own payslip line.
* **Plan versus reality**
  * **Margin**: take home ÷ sales total × 100, against `planned_margin_percent`. Not shown when sales are zero.
  * **Hourly rate**: against `target_hourly_rate_rm`.

## Agents

### Rules for every agent

* **No invented numbers**: every figure traces to a ledger row, an hours line or a plan value.
* **No arithmetic**: figures are copied from `audit/<week>/numbers.json`, never recalculated. A plan value, such as a price, may be cited as written.
* **Acts only through tools**: an agent changes nothing except through the tools the runner gives it. Its instructions are `prompts/<agent>.md`.
* **Nothing leaves the building**: drafts go to `approvals`. The system never posts or sends a draft.
* **Uncertain means flag, not guess**: anything unclear goes on the review list.

### Bookkeeper

* **Purpose**: turn messy inputs into clean records. It is the only agent that reads images and raw documents.
* **Intake order**: inbox files in file name order, then rows that come only from the message. Transaction IDs follow that order.
* **A row from the message**: only when the message states an amount and no document in the same batch covers it.
* **Filing**: the message is saved to `receipts/<year_month>/message_<date>.txt`. Each document goes to `receipts/<year_month>/`, using the month of the document date, or of the intake date when the date cannot be read. `inbox` ends empty.
* **Unreadable receipt**: it still gets a row holding whatever could be read, marked `needs_review`.
* **Reconciliation**: runs the tool, resolves the ambiguous rows, and classifies rows created from bank lines.
* **Writes**: `transactions` and `bank_lines` rows, `audit/<week>/intake_log.md`.

### Payroll

* **Purpose**: hours, take home, hourly rate, payslip.
* **Objective**: maximise the student's hourly rate.
* **Every night**: reads event durations and corrections from the message, applies corrections, runs the hours tool, then the numbers tool.
* **Stated hours that are not events**: appended to `audit/<week>/review_items.md`.
* **Payslip day**: writes its recommendation, then builds the payslip once, after the ruling and the drafts.
* **Writes**: `hours` lines, plan corrections, `numbers.json`, `review_items.md`, `boardroom/<week>/payroll.md`, `payslips/<week>.html`.

### Growth coach

* **Purpose**: the raise plan and the drafted actions.
* **Objective**: grow revenue and sales. It conflicts with Payroll's, and that conflict is the debate.
* **Recommendation**: proposes changes to pricing, product mix, channels and schedule.
* **Drafts**: after the ruling, one file per post or supplier message, with its number at the start of the name, for example `01_instagram_post.md`.
* **Writes**: `boardroom/<week>/growth.md`, drafts in `approvals/<week>/`.

### Auditor

* **Purpose**: check everyone's work and rule on disagreements. The work is verified by an agent that did not produce it.
* **Recompute**: runs `numbers-check` and reports the comparison with the saved file.
* **Trace every hours line to its source**
  * `estimate`: the plan value named by `assumption_ref`
  * `corrected`: the latest `change_log` row for that field with `changed_at` on or before the line date
  * `stated`: the saved message named by `assumption_ref`
* **Rule**: rejects any argument that does not cite figures, then writes a ruling with reasons.
* **After the payslip is built**: confirms every review row and every line of `review_items.md` reached it.
* **Writes**: `audit/<week>/audit_report.md`, `boardroom/<week>/ruling.md`. It has no tool that changes the ledger or the plan.

## Runtime

* **Where it runs**: on the team's machine for the demo. It is a service, so the student's device needs nothing.
* **One workspace per student**: `workspaces/<chat_id>/`. Tests and the demo replay use `workspace/`.
* **Configuration and secrets**: environment variables loaded from a `.env` file that git ignores. See [Getting started](GETTING_STARTED.md). A key never appears in the repository, a prompt, a log or a reply.

### Seams

Fixed so that three people could build at once. A seam changes in this file first, then in the code.

* **Bot to runner**: `run_night(workspace, date, message, ask=None)` returns the night summary. Nothing changes the ledger or the plan except a night started through `run_night`.
* **Runner to tool layer**: `run_tool(workspace, agent, name, args, ask=None)` returns a dict.
* **Runner and tool layer to model**: `ask(role, messages, images=None)` returns the model's text. `role` is `reason` or `read`.
* **Tool layer to tools**: the commands of `tools/lembur.py`, with their JSON in and out.
* **Arguments**: `workspace` is the path of one student's folder. `date` is the night's date as `YYYY-MM-DD`. `message` is the student's text.
* **Night summary**: every key is always present.
  * `week`: the ISO week of the night.
  * `payslip_day`: `true` or `false`.
  * `steps`: a list in run order. Each item has `step` (the number in [Flow](#flow)), `name`, `agent`, `status` (`done`, `failed` or `skipped`) and `note`.
  * `figures`: `hourly_rate_rm`, `take_home_rm` and `hours_total`, copied as text from `numbers.json`. Empty text when there is no value.
  * `payslip`: the workspace path of the payslip, or empty text.
  * `drafts`: a list. Each item has `number` and `file`.
  * `review`: the review list as a list of lines.
  * `failed`: empty, or a dict with `step` and `reason` in plain words.
* **`ask`**
  * `messages` is a list of dicts with `role` (`system`, `user` or `assistant`) and `content` (text).
  * `images` is a list of file paths, used only with the role `read`.
  * It returns text only. Reading an agent's JSON out of that text belongs to the runner.
  * It raises `ModelError` when the gateway still fails after its retries.
* **The gateway**: one HTTPS address. The key goes in the `x-user-id` header and the model name in the `x-model` header. The reply is JSON with the text in `message`. An image is sent as an image part of the last user message.
* **Tests use a scripted model**: `run_night` and `run_tool` take an optional `ask`. A test passes a function that returns scripted answers, so the whole week replays without a key or a network.

### How an agent acts

* **One agent, one step, one short loop**: the runner gives the agent its prompt, the step it must finish and the facts it needs. The agent answers with the tools it wants run. The runner runs them and returns the results. This repeats until the agent says it is finished or 16 turns have passed.
* **The agent's reply is one JSON object**, either
  * `{"actions": [{"tool": "<name>", "args": {...}}, ...], "why": "<one sentence>"}`, or
  * `{"finished": true, "report": "<short report in plain words>"}`.
* **The tools an agent may ask for**: every path is relative to the student's workspace, and a path that leaves it is refused.
  * `lembur`: `command`, `options` and `input`. This is the only way to add rows, reconcile, build hours, save numbers or build the payslip.
    * `options` is a dict of the command's options without the dashes, for example `{"week": "2026-W41"}` or `{"payslip-day": true}`.
    * `input` is the JSON for a command that takes `--input`. The tool layer adds `--workspace` and writes the file the command reads.
    * `input_file` may replace `input`: the workspace path of a CSV file whose rows are passed as the JSON array. It is for a bank statement that already has the five column names of `bank_lines`, so no model retypes an amount. Giving both is refused.
  * `read_document`: `path`, a file in `inbox/` or `receipts/`. Returns `text`. An image is read by the `read` model. A text or CSV file is returned as it is.
  * `list_files`: `folder`. Returns `files`, in file name order.
  * `read_file`: `path`. Returns `text`.
  * `write_file`: `path`, `text` and an optional `append`. It refuses the ledger and plan CSV files, `numbers.json` and the payslip, so those change only through `lembur`.
  * `move_file`: `from` and `to`.
  * `calendar`: `date`. Returns `week`, `week_start`, `payslip_day` and `is_payslip_day`. Agents never work a date out themselves.
* **What `run_tool` returns**: always a dict with `ok`. When `ok` is `false`, `error` says why in plain words. A mistake by an agent never raises an exception.
  * **For `lembur`**: `result` holds the JSON the command printed, whether it passed or failed, so the agent can read the details and adapt.
  * **Loadable alone**: `app/tools.py` loads with no key and no network. It reaches for `app/model.py` only when `ask` is left out and an image has to be read.
* **Which agent may use what**: the tool layer checks this on every call.
  * **Bookkeeper**: `read_document`, `list_files`, `read_file`, `write_file`, `move_file`, `calendar`, and the commands `add-transactions`, `add-bank-lines`, `reconcile`, `resolve`, `classify`, `close-week` and `review`.
  * **Payroll**: `list_files`, `read_file`, `write_file`, `calendar`, and the commands `correct-plan`, `hours`, `numbers`, `review` and `payslip`.
  * **Growth coach**: `list_files`, `read_file`, `write_file`, and the command `review`.
  * **Auditor**: `list_files`, `read_file`, `write_file`, and the commands `numbers-check` and `review`.
* **Checks the runner makes**
  * **Loose replies**: a reply that is not the agreed JSON gets up to two reminders, then the step fails. One bare action is read as a list of one, and a command named as the tool is read as the `lembur` tool.
  * **A tool error is data**: it is returned to the agent, which is expected to read it and adapt. For example, classify the rows the numbers tool refused, then run it again.
  * **A step is checked, not trusted**: when an agent answers finished, the runner checks that the step's command passed and its file exists. If not, the step is sent back, up to twice, with what is missing. Then the step fails.
  * **Out of turn**: the payslip is built only in the payslip step and the week is closed only in its own step, both on payslip day.
  * **Giving up too early**: a row is not sent to review while exactly one free bank line names its counterparty.
  * **Filing**: a document the Bookkeeper leaves in `inbox/` after its rows are in the ledger is moved to its `source_file` path by the runner.
  * **Figure check**: every money and hours figure in the recommendations and the ruling must appear in `numbers.json` or the plan files. A text that still holds an untraced figure after one send back is put on the review list. It does not stop the night.
  * **Trace**: every reply of an agent and every tool result is kept in `audit/<week>/trace_<date>.jsonl`.

### Chat

* **Channel**: Telegram. The bot asks Telegram for new messages, so it needs no public address.
* **What the bot does with a message**
  * **A file or photo**: saved into `inbox/` under its original file name when there is one, otherwise a name made from the date and time received.
  * **`payslip`**: sends the latest payslip file and the hourly rate.
  * **`review`**: sends the review list.
  * **`approve N` and `skip N`**: act on the latest week that has drafts. The number is the one at the start of the draft's file name.
  * **`/start`, `help` or a greeting**: a short welcome that says what the bot does and which words it understands. No night starts.
  * **Anything else**: it is tonight's message. The bot says the night shift is starting, calls `run_night` and reports back.
* **Fixed words only**: the words are matched by the code. A short ask that names `payslip` or `review`, such as "show me my payslip", counts as that word. The bot does not use a model to guess what the student meant.
* **A new student**: the first message from a chat creates `workspaces/<chat_id>/`. Day Zero is not built, so the bot copies the hand written plan, `data/demo/plan_*.csv`, into its `plan/` folder.
* **The night's date**: today's date in Malaysia time. A message that starts with a date written `YYYY-MM-DD` runs as the night of that date, so the recorded week can be replayed in one sitting.
* **What the bot says**: fixed sentences with figures copied from `numbers.json`. The bot calculates nothing.
* **What the bot sends on payslip day**: the payslip file, then each draft file, then the message.
* **One night at a time**: while a night is running for a student, a second message from her waits.

## Outputs

* **Payslip**, top to bottom
  1. Week and date range
  2. Hourly rate, as the headline
  3. Take home, with totals by category
  4. Hours by activity, with the total
  5. Shared hours
  6. Profit per hour by product, with any product that loses money marked
  7. Plan versus reality
  8. Debate summary and the Auditor's ruling
  9. Raise plan: the recommendations the ruling upheld, each pointing to its draft in `approvals`
  10. Needs your review list
* **Payslip template**: `submission/payslip_template.html`. One self contained HTML file with styles inside the file, no scripts, and no fonts or images loaded from the internet.
  * **Single values**: `{{name}}`, where the name is a key of `numbers.json`, with a dot for a nested key. Examples: `{{week}}`, `{{hourly_rate_rm}}`, `{{category_totals_rm.sales}}`, `{{hours.total}}`.
  * **All single value names**: `week`, `date_from`, `date_to`, `hourly_rate_rm`, `take_home_rm`, `shared_minutes`, `shared_hours`; `category_totals_rm.` followed by `sales`, `materials`, `packaging`, `platform_fees`, `shipping` or `other_expenses`; `minutes.` and `hours.` each followed by `production`, `fulfilment`, `event`, `admin` or `total`; `plan_versus_reality.` followed by `margin_percent`, `planned_margin_percent`, `hourly_rate_rm` or `target_hourly_rate_rm`.
  * **Repeating rows**: everything between `<!-- each products -->` and `<!-- end products -->` is repeated once per item, and inside it `{{name}}` is a field of that item.
    * `products`: `product_id`, `name`, `units_sold`, `revenue_rm`, `unit_costs_rm`, `channel_costs_rm`, `profit_rm`, `direct_hours`, `profit_per_hour_rm`, `loses_money` (filled as `true` or `false`, so it can drive a style class).
    * `review_rows`: `txn_id`, `date`, `reconciliation_status`, `amount_rm`, `description`, `notes`.
    * `review_items`: `text`, one per line of `review_items.md`, exactly as saved.
    * `raise_plan`: `text` and `draft_file`, one per recommendation the ruling upheld.
  * **Text sections**: `{{debate_summary}}` and `{{ruling}}`, from the payslip input that Payroll writes. `ruling` is taken from `ruling.md` with its figures unchanged.
  * **A figure that is not shown**: its placeholder is filled with nothing.
  * **No conditions**: the template cannot show or hide a line depending on a value.
  * **No new field**: nothing outside these names and blocks is added to the template without a change here first.
* **Plan for the night**: `audit/<week>/plan_<date>.md`. Each step, why tonight needs it, and its outcome.
* **`payroll.md` and `growth.md`**: each recommendation states the change and cites the figures it rests on.
* **`ruling.md`**: for each disagreement, which side is upheld and why, citing figures.
* **`audit_report.md`**: each of the Auditor's checks with pass or fail and the rows concerned.
* **`intake_log.md`**: each file read, where it was filed and the rows it produced.
* **`review_items.md`**: one line per item that is not a transaction row, with its date, what is unclear and the message reference.

---

# Validation

* **Pass condition**: a run's outputs match the answer key exactly (statuses, minutes, and money to the sen). A mismatch is a bug to fix, not something to explain away.
* **Planted problems and the expected result of each**
  * **Duplicate receipt**: the second copy is `duplicate`, left out of totals, and on the review list.
  * **Missing receipt**: a bank line with no document becomes a row with status `unmatched`, counted in totals, and on the review list.
  * **Amount that does not match the bank statement**: `needs_review`, the bank amount is used, and both amounts are in `notes`.
  * **Blurry receipt**: `needs_review`, amount empty, left out of totals, document still filed.
  * **Bestseller that loses money**: the product with the most units sold has a profit below zero after fees and shipping.
  * **Event hours**: one nightly message states an event with its duration.
  * **Correction**: one reply corrects a `minutes_per_unit` value mid week, with sales of that product both before and after it.
* **Rules the demo dataset follows**
  * **One week**: Monday to Sunday.
  * **One product per order**: so per order fees, shipping and packing time belong to one product.
  * **Bank statement**: CSV or a text PDF, never a photo. Every line has a unique reference.
  * **Duplicate receipt**: not cash, identical to the original on the five duplicate fields, and not a copy of the mismatched receipt.
  * **Mismatched amount**: the receipt and its bank line share the same reference.
  * **Missing receipt**: an expense whose bank description names the supplier, so the category is clear.
  * **Bank transfer sales**: every sale has a distinct counterparty or a reference. Otherwise two sales with the same date and amount read as a duplicate.
  * **Materials purchases**: restock size, so one receipt does not swamp the week's take home.
  * **Stated hours**: for events only, written as clock times or plain numeric hours.
* **Where the files live**
  * `data/demo/plan_*.csv`: the hand written plan, copied to `workspace/plan/` before a run.
  * `data/demo/inbox/`: the documents the student sends.
  * `data/demo/messages.md`: each nightly message and the correction reply, with its date.
  * `data/answer_key/ledger_*.csv`: the expected ledger.
  * `data/answer_key/answer_key.md`: every other expected figure and flag.
  * `data/answer_key/.expected_ledger.ref/` and `.independent.ref/`: the records of the two calculations that had to agree. The comparator reads `calculation.json` from the first, so that folder stays.
* **How to check a run**: the scripts in `data/test_harness/`. The commands are in [Getting started](GETTING_STARTED.md).
  * `compare_outputs.py`: compares `workspace/` with the answer key and prints PASS or FAIL. It checks every ledger row, recalculates the figures on its own, and checks that the plan correction was applied.
  * `replay_week.py`: replays the seven nights through the runner with the real models.
  * `reset_workspace.py`: empties `workspace/` before a run.
  * `mutation_test.py`: proves the comparator catches eleven kinds of error.
* **Not compared**: the `notes` and `description` columns of transactions, because an agent words them itself. Hours lines are matched by date, activity, product and assumption reference, never by `entry_id`.

## Proofs

Each proof answered one question before the team built on the answer.

1. **The reading model accepts an image through the gateway**: pass, 11 October 07:14. One order screenshot was sent as an image part of the message. The model returned the date, the amount, the customer and the payment reference correctly.
2. **The reasoning model can run one night as an agent**: pass, 11 October 07:20. The night of 2026-10-05 ran through the runner in about 20 seconds: four rows, T0004 marked `duplicate`, `numbers.json` saved, no manual help.
3. **The bot receives a message and a photo and replies with a file**: pass. A photo sent from a phone landed in the inbox of that chat's workspace on 11 October 06:46. The full round trip, with a night run by the real runner and the payslip arriving in the chat, ran before submission.
4. **The whole demo week passes the comparator**: pass, twice on 11 October (07:45 and an independent replay at 08:10). Seven nights with the real models took about five minutes. The comparator printed PASS with no difference: 20 transactions, 14 bank lines, 20 hours lines, take home RM39.50, 15.6 hours, RM2.53 an hour.

* **What to know**: the models do not answer the same way every time. Four earlier replays differed from the key in one step each. Each cause was closed with a check in the runner or a clearer line in a prompt. One passing run is not a guarantee, so every recorded run is compared again.

# How WorkBuddy Was Used

WorkBuddy is the platform the team built with. It is not part of the running product.

* **The rule**: the organisers said on 10 October that WorkBuddy does not have to be part of the final solution. Teams show proof that they used it while building, and explain how, where and in what scenarios.
* **How**: each teammate worked with WorkBuddy as the builder in their own checkout. It was given the docs as the source of truth, it wrote the code or the content, and the result was checked before it was merged.
* **Where and in what scenarios**
  * **The engine**: the reconciliation, hours and numbers tools, the command line and the payslip filler, with their tests.
  * **The tool layer and the bot**: `app/tools.py` and `app/bot.py`, with their tests.
  * **The dataset**: the synthetic receipts, orders, bank statement, nightly messages and the answer key, with a second independent calculation that had to agree with the first.
  * **The story**: agent identities, the payslip template, the deck outline, the video script and the question and answer sheet.
  * **The agents' instructions**: before the redesign, the four agents were instruction files that WorkBuddy ran as skills. That is where the prompts were first shaped.
* **Evidence**: `submission/evidence/`, with screenshots of the sessions.
* **What we say**: only what WorkBuddy really did. Work done or checked by other means is not presented as WorkBuddy's.

---

# TODO (future)

* **Day Zero**: plan a new business from one message, with the same four agents and the same plan files. Design agreed, not built. The hand written plan stands in for it.
  * **Steps**: costing (Bookkeeper), pricing and launch drafts (Growth coach), time and predicted rate (Payroll), check (Auditor), then the four plan files.
  * **A planned week**: a new plan file `plan_planned_sales.csv` (`product_id`, `channel`, `units_per_week`) holds the student's expected volume.
  * **Predicted figures**: the hours tool and the product profit rules run over that planned week.
  * **Stop rule**: if Day Zero needs its own agents or its own data shapes, stop and redesign. That would be two products.
* **Raise plan projections**: a claim such as "this would earn you RM2 more an hour" needs a deterministic calculation. Design agreed, not built.
  * **Replay the week**: the numbers tool runs again on the same week with a new price for one product and the same units sold.
  * **Label**: every projection states the assumption it replays. The Auditor rejects any projection that is not tool output.
* **Payslip as a PDF**: a headless browser prints the HTML file to `payslips/<week>.pdf`. The conversion was proved by hand.
* **More ways in**: WhatsApp beside Telegram, voice notes, a hosted service with a container file. Each is a new channel or a deployment, not a new engine.
* **Posting through a connector**: sending an approved draft for the student.
* **Growth path**: a first helper (hours logged per person, the `person` field is ready), then reading from accounting or order software once the student adopts it.

# Open Questions

* **The date at the start of a message**: it exists for the demo replay. Decide whether a real student may use it.
* **Parallel recommendations**: Payroll and the Growth coach write step 7 one after the other. Running them at the same time is not built.
