# Lembur: System Design

How the system works: conventions, data, tools, agents, workflows and outputs.

---

## 0. How to use this file

* **Source of truth for behaviour and data**: every skill, tool and template implements this file.
* **`PLAN.md`**: covers the product, scope, roles, validation and schedule. Read it first.
* **If the two files disagree**: this file wins on behaviour and data, `PLAN.md` wins on scope and schedule. Report the conflict to the team.
* **Not written here**: ask the team, do not assume.
* **[confirm]**: not agreed yet. Do not build on it.
* **[pending check N]**: waits on a first hour check (PLAN section 12).

---

## 1. Overview

* **Two modes, one engine**
  * Day Zero plans a new business. The Night Shift runs an existing one.
  * Both use the same four agents and the same plan file.
  * Day Zero writes the four plan CSV files in `plan/` (section 3.2). The Night Shift reads them and compares every payslip against the plan.
* **Build dependency**: the Night Shift needs the plan file, not Day Zero. It is built first against a hand written plan file.
* **Stop rule**: if Day Zero needs its own agents or its own data shapes, stop and redesign. That would be two products.
* **Agents read and argue, tools count**
  * Agents read documents and messages, decide unclear cases and write recommendations.
  * Every match, total, hours figure and rate comes from a deterministic tool (section 4).
* **Night Shift in one line**: message and inbox → Bookkeeper → reconciliation tool → ledger → Payroll (hours, numbers) → on payslip day: recommendations, ruling, payslip, drafts → morning message → the student approves or corrects.

---

## 2. Conventions

* **Dates**: `YYYY-MM-DD`, Malaysia time.
* **Week**: Monday to Sunday, written as an ISO week. `2026-W41` is 5 to 11 October 2026. Used wherever a path shows `<week>`.
* **Month folder**: `YYYY-MM`, wherever a path shows `<year_month>`.
* **Payslip day**: Sunday night. It closes that week.
* **Money**: ringgit with two decimals in files. Tools calculate in whole sen.
* **Time**: whole minutes in files and tools. Hours exist only on display.
* **Rounding**
  * Applied at display only, with one exception in section 4.3 (channel fees).
  * Halves round away from zero: 304.5 becomes 305.
  * Hours show one decimal, money two decimals, percentages whole numbers.
  * Python `round()` and Excel `ROUND` treat halves differently. Tools must apply the rule above explicitly.
* **Empty cell**: means not known or not applicable. Never write 0 or "n/a" in its place.
* **IDs**: `P01` for products, `T0001` for transactions, `H0001` for hours entries. A transaction ID is never reused.
* **Person**: `person_1` is the student.
* **Assumption reference**: names one plan value.
  * `products.<product_id>.<column>`, for example `products.P01.minutes_per_unit`
  * `channels.<channel>.<column>`
  * `assumptions.<column>`
* **Message reference**: `message.<date>` names the nightly message of that date, saved at `receipts/<year_month>/message_<date>.txt`.

---

## 3. Data model

### 3.1 Folder layout

`workspace/` is the folder WorkBuddy is authorised to read and write.

```
workspace/
  inbox/                    student drops files here
  plan/plan_products.csv    baseline products
  plan/plan_channels.csv    baseline channels
  plan/plan_assumptions.csv baseline assumptions
  plan/plan_change_log.csv  corrections
  ledger_transactions.csv  transactions
  ledger_bank_lines.csv    bank statement lines
  ledger_hours.csv         hours
  receipts/<year_month>/    filed source documents and saved nightly messages
  boardroom/<week>/         payroll.md, growth.md, ruling.md
  audit/<week>/             numbers.json, audit_report.md, intake_log.md, review_items.md
  payslips/<week>.html      weekly payslip, filled from the template (section 7)
  payslips/<week>.pdf       the same payslip as a PDF [pending check 11]
  approvals/<week>/         drafted posts and messages, one file per draft
  approvals/<week>/approved/  drafts the student has approved
```

* **Why this layout**: the Auditor traces numbers to receipts, judges open a ledger row and see the receipt behind it, and the folder is the handoff package if the student moves to accounting software.
* **File format**: CSV, decided by Law at 13:42 on 10 October. One file per sheet, named `<book>_<sheet>.csv`, with the same columns. `openpyxl` is not installed; the adapter retains `.xlsx` support for later.
* **Pinned format**: every entry point passes `fmt="csv"` to `sheets.load_book` and `sheets.save_book`, never `auto`: installing a library must not silently change which files are read.
* **Sheets**: each CSV represents one logical sheet; row 1 holds the column names exactly as written below, in the order listed.

### 3.2 Plan CSV files

* **Files in `plan/`**: `plan_products.csv`, `plan_channels.csv`, `plan_assumptions.csv`, `plan_change_log.csv`.

* **`products`**: one row per product.
  * `product_id`
  * `name`
  * `price_rm`: selling price per unit
  * `material_cost_rm`: per unit
  * `packaging_cost_rm`: per unit
  * `minutes_per_unit`: production time per unit
* **`channels`**: one row per sales channel. Role B defines the rows.
  * `channel`: short lowercase name
  * `fee_percent`: share of the sale amount the channel takes; 0 where none
  * `fee_per_order_rm`: 0 where none
  * `shipping_cost_per_order_rm`: shipping the student pays per order; 0 where none
  * `fulfilment_minutes_per_order`: packing and handover time per order; 0 where none
* **`assumptions`**: one row.
  * `admin_hours_per_week`
  * `planned_margin_percent`
  * `target_hourly_rate_rm`
* **`change_log`**: one row per correction. Rows are only ever added.
  * `changed_at`: date of the student's correction message
  * `field`: assumption reference of the value changed
  * `old_value`
  * `new_value`
  * `reason`: the student's words
  * `source`: message reference
* **Value in force on a date**: the `old_value` of the earliest `change_log` row for that field with `changed_at` later than the date. If there is none, the value now in the plan sheet.

### 3.3 Ledger CSV files

* **Files**: `ledger_transactions.csv`, `ledger_bank_lines.csv`, `ledger_hours.csv`.

* **`transactions`**: one row per sale or expense.
  * `txn_id`
  * `date`: the date on the document
  * `type`: `income` or `expense`
  * `category`: `sales`, `materials`, `packaging`, `platform_fees`, `shipping` or `other_expenses`
  * `description`: what was sold or bought
  * `product_id`: sales rows only
  * `quantity`: units sold, sales rows only
  * `amount_rm`: always positive; empty only when it cannot be read
  * `channel`: sales rows only; must equal a `channel` in the plan file
  * `payment_method`: `cash` or `bank_transfer`
  * `counterparty`: customer or supplier as written on the document
  * `reference`: payment reference printed on the document
  * `source_file`: workspace path of the filed document or saved message; empty for rows created from a bank line
  * `reconciliation_status`: one of the six values in section 4.1
  * `bank_reference`: reference of the bank line this row is paired with
  * `notes`: the reason for any decision or flag
* **Rules for `transactions`**
  * `sales` is always `income`. Every other category is `expense`.
  * One sales row is one order of one product.
  * Required on every row: `date`, `type`, `category`, `amount_rm`, `payment_method`.
  * Also required on sales rows: `product_id`, `quantity`, `channel`.
* **`bank_lines`**: one row per bank statement line.
  * `date`
  * `description`
  * `type`: `income` for money in, `expense` for money out
  * `amount_rm`: always positive
  * `bank_reference`: unique per line
* **`hours`**: one row per hours line. Built by the hours tool (section 4.2).
  * `entry_id`
  * `date`
  * `person`
  * `activity`: `production`, `fulfilment`, `event` or `admin`
  * `product_id`: production and fulfilment lines only
  * `quantity`: units for production, orders for fulfilment, empty otherwise
  * `minutes`
  * `source`: `estimate`, `stated` or `corrected`
  * `assumption_ref`: assumption reference for `estimate` and `corrected`, message reference for `stated`

---

## 4. Deterministic tools

* **Mechanism**: a Python script in `tools/`, run by a skill. Confirmed by check 6 on 10 October, so the spreadsheet formula fallback is not used.
* **Boundary**: agents pass in what they have read (rows, event durations, corrections). They never calculate.
* **Counted row**: a transaction row counts towards totals and hours unless its status is `duplicate` or its `amount_rm` is empty.
* **Entry point**: `python -B tools/lembur.py <command> --workspace workspace`. Commands return JSON on standard output, exit 0 on success and 1 on failure, without tracebacks. Batch input is a JSON array read with `--input <file>` or `--input -` for standard input.
* **Issued week**: either `payslips/<week>.html` or `payslips/<week>.pdf` marks the week as issued. It blocks `hours`, `numbers` and `close-week` for that week, not intake. The payslip is HTML filled from a template; PDF comes later. No payslip command is built at this stage.

### 4.1 Reconciliation tool

* **Transaction intake, `add-transactions`**: accepts incomplete schema rows in Bookkeeper intake order and assigns IDs after the highest stored transaction ID. IDs are never reused; the entry point has no row deletion command.
  * Refuses a batch carrying `txn_id` or `bank_reference`, even empty, or a `reconciliation_status` other than empty or `needs_review`.
  * Refuses the whole batch if any nonempty `source_file` is already in the ledger and lists those paths. Several rows from one message in the same new batch are allowed. Reason: retrying cash intake would otherwise count the sales twice.
* **Statement intake, `add-bank-lines`**: an identical stored line is skipped and reported. The same `bank_reference` with different content refuses the whole batch. References must be nonempty and unique after intake.
* **Commands**: `reconcile` prints ambiguous row IDs with candidate bank lines; `resolve --txn-id --bank-reference --reason` records a choice, or an empty reference for an undecided row. A reason is required.
* **Classification, `classify --txn-id --category --reason`**: works on any row the classification gate names, including empty, unknown or type inconsistent categories. The new category must be known and agree with the row's type. The reason is required and appended to `notes`.
* **Status values**
  * `matched`: one bank line agrees with the row
  * `ambiguous_resolved`: several bank lines fitted; the Bookkeeper chose one and wrote why
  * `unmatched`: no bank line for this row, or no document for this bank line
  * `duplicate`: a copy of an earlier row
  * `needs_review`: a required field is missing, the amount disagrees with the bank, or the Bookkeeper could not decide
  * `cash_declared`: a cash row; no bank evidence is expected
* **A bank line is used**: when any transaction row carries its `bank_reference`.
* **Steps, in order**. Each row takes the first status that applies.
  1. **Intake and defensive validation**: a row already `needs_review` is left untouched. Before matching an eligible row, the tool sets `needs_review` with a reason if a required field is missing, the category is unknown, category and type disagree, or the payment method is unknown. The Bookkeeper still checks at intake: a mechanical check must not depend on a model.
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
  7. **Leftover bank lines**, on payslip day only: `close-week --week` converts only unused bank lines dated inside that week into new transaction rows. It does not issue the payslip.
     * Copied from the bank line: `date`, `type`, `amount_rm`, `description`, `bank_reference`.
     * `payment_method` is `bank_transfer`, `source_file` is empty, status is `unmatched`, `notes` says no document was found.
     * Income becomes `sales` with `product_id` empty. An expense is created with an empty `category`; the Bookkeeper must classify it from the description before running the numbers tool. An unclear expense becomes `other_expenses` with a note explaining the uncertainty. No silent expense category default.
* **Review list**: every row with status `unmatched`, `duplicate` or `needs_review`, plus every line of `audit/<week>/review_items.md`. Payroll appends one line per nontransaction item, containing its date, what is unclear and the message reference. No new sheet.
* **Running again**: each run tests rows that are not cash and have an empty status, or are `unmatched` with an empty `bank_reference`. Settled rows are never changed.
* **Known limits**
  * A document that arrives after step 7 turned its bank line into a row is not paired automatically. Intake remains open even after the week is issued; the late document gets a new row, stays `unmatched` and is on review. It does not overwrite the bank created row.
  * A copy of a mismatched receipt arriving on a later run is not caught as a duplicate: the original row's amount was replaced by the bank amount, so the duplicate key no longer agrees. The later copy is `unmatched` and counted. A copy in the same run is caught.

### 4.2 Hours tool

* **Command**: `hours --week <week> [--input <events JSON>] [--payslip-day]` rebuilds the open week using events as read. Input is optional on nights without an event. It appends every returned warning to `audit/<week>/review_items.md`, never repeating an existing line.
* **Plan correction command**: `correct-plan --field --new-value --changed-at --reason` applies the correction through the plan tool.
* **Formula**: week hours = production + fulfilment + events + admin, summed from the `hours` lines dated in the week.
* **Lines**
  * **Production**: one line per date and product, from counted sales rows.
    * `quantity` is the units sold.
    * `minutes` = `quantity` × `minutes_per_unit` in force on that date.
    * `assumption_ref` is `products.<product_id>.minutes_per_unit`.
  * **Fulfilment**: one line per date, product and channel, from counted sales rows.
    * `quantity` is the number of orders (rows).
    * `minutes` = `quantity` × `fulfilment_minutes_per_order` in force on that date.
    * `assumption_ref` is `channels.<channel>.fulfilment_minutes_per_order`.
    * No line is written when the minutes are zero.
  * **Event**: one line per event stated in a nightly message.
    * The agent passes the date, plus either start and end as 24 hour times or the stated hours as written. The hours tool computes whole minutes. For "Bazaar 4 to 9", the agent passes `16:00` and `21:00`; the tool returns 300. Choosing am or pm is reading and remains with the agent.
    * When a message gives both clock times and a total, the agent passes the clock times only. The hours tool rejects an event carrying both forms.
    * `source` is `stated`. `assumption_ref` is the message reference.
  * **Admin**: one line per week, dated that week's Sunday, written on payslip day.
    * `minutes` = `admin_hours_per_week` in force on that date × 60.
    * `assumption_ref` is `assumptions.admin_hours_per_week`.
* **`source` on production, fulfilment and admin lines**: `corrected` only when a `change_log` row for the line's field has `changed_at` on or before the line date. Earlier lines stay `estimate`, even when their value in force is recovered from a later correction's `old_value`.
* **Sales rows without `product_id` or `quantity`**: produce no lines.
* **Why production counts units sold, not units made**: it mirrors how accounting attaches cost to goods when they sell. A big production weekend does not distort one week's rate.
* **Events**: Payroll passes what it read, never a calculated duration. A missing or unreadable event date returns one review warning and writes no line, without raising an exception. An end time not after the start, or a duration that cannot be read, also produces no hours line and a warning. Payroll appends the available date, what is unclear and the message reference to `audit/<week>/review_items.md`.
* **Event input limits**: durations use clock times or plain numeric hours. Text such as "2h30", "half an hour" or "2 jam" goes to review.
* **Event rerun limits**: an event reread with a different duration on a rerun adds a second line. Two separate events with the same date, message reference and duration become one line.
* **Stated hours for anything other than events**: not applied. Payroll appends the item to `audit/<week>/review_items.md`. Stated production time describes units made while estimates count units sold, so applying it would double count.
* **Corrections**
  * The student replies with a correction, for example "keychains take me 15 minutes".
  * Payroll updates the plan cell and adds a `change_log` row.
  * The new value applies to lines dated on or after `changed_at`. Earlier lines keep the old value.
  * Only three values can be corrected: `minutes_per_unit`, `fulfilment_minutes_per_order`, `admin_hours_per_week`.
* **Running again**: production, fulfilment and admin lines of the open week are rebuilt from the ledger on every run. An event line is written once per stated event. Only open week lines are renumbered; lines of every other week retain their IDs. An ID is stable once its week's payslip is issued.
* **Answer key comparison**: match hours lines by date, activity, product and assumption reference, never by `entry_id`.
* **Worked example** (illustration only; real numbers come from the answer key)
  * Keychains sold: 30 × 20 minutes = 600
  * Bracelets sold: 6 × 35 minutes = 210
  * Online orders packed: 10 × 5 minutes = 50
  * Bazaars, stated: 360
  * Admin: 2 hours = 120
  * Total: 1,340 minutes, shown as 22.3 hours
  * Hourly rate: RM68.00 ÷ 1,340 × 60 = RM3.04

### 4.3 Numbers tool

All figures use counted rows and hours lines dated in the week.

* **Classification gate**: `business_numbers.compute` raises `ValueError` while any counted row has an empty category, an unknown category, or a category that disagrees with its type. `sales` requires `income`; the five expense categories require `expense`. The Bookkeeper must finish classification first. Rows that are not counted, including duplicates and rows with an empty amount, never block this gate.
* **Entry point warnings**: both `hours` and `numbers` append every returned warning to `audit/<week>/review_items.md`, including warnings about missing products or channels. Each warning occupies one line; an existing identical line is never repeated. Do not change the figures to hide a warning.
* **Commands**: `numbers --week` saves exactly the compute return value; `numbers-check --week` reruns without writing any file and reports equality or differing top level keys, exiting 1 on a mismatch. Classification refusal prints the affected row IDs and reasons. `review --week` prints the week's transaction review rows and every saved review item.
* **Saved numbers**: Payroll writes exactly the numbers tool return value to `audit/<week>/numbers.json`. Payroll, the Growth coach and the Auditor copy figures only from this file. The Auditor reruns the tool without writing and records the comparison with the saved file in `audit_report.md`.
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
* **Shared hours**: event plus admin minutes. They are not allocated to any product, because any split would be arbitrary. They appear as their own payslip line.
* **Plan versus reality**
  * **Margin**: take home ÷ sales total × 100, against `planned_margin_percent`. Not shown when sales are zero.
  * **Hourly rate**: against `target_hourly_rate_rm`.

---

## 5. Agents

### 5.1 Rules for every agent

* **No invented numbers**: every figure traces to a ledger row, an hours line or a plan value.
* **No arithmetic**: figures come from the tools in section 4 and are copied, never recalculated. Payroll, the Growth coach and the Auditor copy figures only from `audit/<week>/numbers.json`.
* **Nothing leaves the building**: drafts go to `approvals`. The system never posts or sends a draft. The student sends an approved draft herself.
* **Uncertain means flag, not guess**: anything unclear goes on the review list.
* **Why only four agents**: an agent exists only where it needs different tools, different context or a conflicting objective. Timekeeping is part of Payroll. Reconciliation is a tool.

### 5.2 Bookkeeper

* **Purpose**: turn messy inputs into clean records.
* **Reads**: files in `inbox`, the nightly message.
* **Does**
  * Saves the nightly message to `receipts/<year_month>/message_<date>.txt`.
  * Reads inbox files in file name order, then adds rows that come only from the message. Transaction IDs follow that order.
  * Makes a transaction row from the message only when the message states an amount and no document in the same batch covers it.
  * Extracts bank statement lines into `bank_lines`.
  * Files each document into `receipts/<year_month>/`, using the month of the document date, or of the intake date when the date cannot be read. `inbox` ends empty.
  * Sets `needs_review` on any row with a required field missing. An unreadable receipt still gets a row holding whatever could be read.
  * Runs the reconciliation tool, resolves the ambiguous rows, and sets the category of rows created from bank lines.
* **Writes**: `transactions` and `bank_lines` rows, `audit/<week>/intake_log.md`.
* **Why a separate agent**: it is the only agent that reads images and raw documents.

### 5.3 Payroll

* **Purpose**: hours, take home, hourly rate, payslip.
* **Reads**: ledger, plan file, nightly message.
* **Does**
  * Reads event durations and corrections from the message.
  * Applies corrections to the plan file.
  * Runs the hours tool, then the numbers tool, saving exactly its return value to `audit/<week>/numbers.json`.
  * Appends every hours tool and numbers tool warning, plus stated hours that are not events, to `audit/<week>/review_items.md`.
  * On payslip day, writes its recommendation, then builds the payslip once after the ruling. There is no draft payslip.
  * Includes both transaction review rows and every line of `review_items.md` in the payslip review list.
* **Writes**: `hours` lines, plan corrections, `audit/<week>/numbers.json`, `audit/<week>/review_items.md`, `boardroom/<week>/payroll.md`, `payslips/<week>.html`, and a PDF in a later step.
* **Objective**: maximise the student's hourly rate.

### 5.4 Growth coach

* **Purpose**: raise plan and drafted actions.
* **Reads**: ledger, `audit/<week>/numbers.json`, plan file.
* **Does**
  * Proposes changes to pricing, product mix, channels and schedule.
  * Writes its recommendation.
  * After the ruling, drafts posts and supplier messages. Each draft is one file whose name starts with its number, for example `01_instagram_post.md`.
* **Writes**: `boardroom/<week>/growth.md`, drafts in `approvals/<week>/`.
* **Objective**: grow revenue and sales.
* **Why a separate agent**: its objective conflicts with Payroll's. That conflict is the debate.

### 5.5 Auditor

* **Purpose**: check everyone's work and rule on disagreements.
* **Reads**: ledger, saved numbers file at `audit/<week>/numbers.json`, both recommendations, and `audit/<week>/review_items.md`.
* **Does**
  * Runs the numbers tool again without writing and compares the result with the saved numbers file. Reports the comparison in `audit_report.md`.
  * Confirms every row with status `unmatched`, `duplicate` or `needs_review`, plus every line of `review_items.md`, is on the final review list.
  * After the payslip is built at step 8, confirms both review sources reached it. No draft payslip is created.
  * Confirms every hours line traces to its source:
    * `estimate`: the plan value named by `assumption_ref`
    * `corrected`: the latest `change_log` row for that field with `changed_at` on or before the line date
    * `stated`: the saved message named by `assumption_ref`
  * Rejects any recommendation argument that does not cite figures.
  * Writes a ruling with reasons.
* **Writes**: `audit/<week>/audit_report.md`, `boardroom/<week>/ruling.md`, the final review list on the payslip.
* **Why a separate agent**: the work is verified by an agent that did not produce it.

---

## 6. Workflows

### 6.1 Night Shift

* **Trigger**: the student sends one Telegram text message and drops files into `inbox`. A voice note is wanted as well [pending check 2]; the fallback is a typed message.
* **Every night**
  1. **Intake**, Bookkeeper: transactions extracted, documents filed.
  2. **Reconcile**, reconciliation tool then Bookkeeper: a status on every row.
  3. **Ledger update**, Bookkeeper: ledger rows with source links.
  4. **Hours**, Payroll: hours lines.
  5. **Numbers**, Payroll: take home, hourly rate, profit per hour by product. Save exactly the tool return value to `audit/<week>/numbers.json`.
* **Payslip day adds**
  6. **Recommendations**, Payroll and Growth coach in parallel: `payroll.md`, `growth.md`.
  7. **Audit and ruling**, Auditor: rerun the numbers tool without writing, compare with the saved numbers file, and write `audit_report.md` and `ruling.md`.
  8. **Payslip**, Payroll: fill the template to build `payslips/<week>.html` once, after the ruling, using the saved numbers file. PDF is a later step. The Auditor then confirms both review sources reached the payslip.
  9. **Drafts**, Growth coach: posts and supplier messages in `approvals`.
  10. **Morning message**, WorkBuddy messaging: "Your board meeting is ready" plus the approval list.
* **Approval**: the student approves each draft individually, by reply.
  * "approve 2" moves draft 2 from `approvals/<week>/` into `approvals/<week>/approved/`. "skip 2" leaves it where it is. The agent confirms either way.
  * The reply works the same from Telegram or typed inside WorkBuddy.
  * It is a file move written into the skill instructions. There is no approval command.
  * Nothing is posted or sent by the system in this version. Posting through a connector is future work.

### 6.2 Day Zero

* **Trigger**: the student describes the business idea in one message.
* **Steps**
  1. **Costing**, Bookkeeper: material, packaging, fee and shipping cost per unit and per channel.
  2. **Pricing and launch**, Growth coach: prices, launch post drafts, supplier research.
  3. **Time and predicted rate**, Payroll: minutes per unit labelled as assumptions, break even point, predicted hourly rate.
  4. **Check**, Auditor: arithmetic checked, every assumption labelled.
  5. **Plan files**, Payroll: `plan/plan_products.csv`, `plan/plan_channels.csv`, `plan/plan_assumptions.csv` and `plan/plan_change_log.csv` in the format of section 3.2.
* **Output to the student**: a plan summary with the predicted hourly rate, plus the plan file.

---

## 7. Outputs

* **Payslip**, top to bottom
  1. Week and date range
  2. Hourly rate, as the headline
  3. Take home, with totals by category
  4. Hours by activity, with the total
  5. Shared hours (section 4.3)
  6. Profit per hour by product, with any product that loses money marked
  7. Plan versus reality
  8. Debate summary and the Auditor's ruling
  9. Raise plan: the recommendations the ruling upheld, each pointing to its draft in `approvals`
  10. Needs your review list
* **Payslip rules**: wording and look belong to Role C. Every number is copied from `audit/<week>/numbers.json`. The review list includes transaction rows with status `unmatched`, `duplicate` or `needs_review` and every line of `audit/<week>/review_items.md`.
* **Payslip format**, decided by Law on 10 October
  * **Template**: `submission/payslip_template.html`, owned by Role C. One self contained HTML file: styles inside the file, no scripts, no fonts or images loaded from the internet. Reason: it must look the same offline and when turned into a PDF.
  * **Filling**: a script fills the template and writes `payslips/<week>.html`. No model types a figure into the payslip.
  * **PDF**: wanted. WorkBuddy turns that file into `payslips/<week>.pdf` [pending check 11]. Fallback: the HTML file is the payslip.
  * **Single values**: `{{name}}`, where the name is a key of `audit/<week>/numbers.json`, with a dot for a nested key. Examples: `{{week}}`, `{{date_from}}`, `{{hourly_rate_rm}}`, `{{take_home_rm}}`, `{{category_totals_rm.sales}}`, `{{hours.production}}`, `{{hours.total}}`, `{{shared_hours}}`, `{{plan_versus_reality.margin_percent}}`.
  * **Repeating rows**: everything between `<!-- each products -->` and `<!-- end products -->` is repeated once per item, and inside it `{{name}}` is a field of that item. The blocks are:
    * `products`: `product_id`, `name`, `units_sold`, `revenue_rm`, `unit_costs_rm`, `channel_costs_rm`, `profit_rm`, `direct_hours`, `profit_per_hour_rm`, `loses_money` (filled as `true` or `false`, so it can drive a style class).
    * `review_rows`: `txn_id`, `date`, `reconciliation_status`, `amount_rm`, `description`, `notes`, one per transaction row on the review list.
    * `review_items`: `text`, one per line of `audit/<week>/review_items.md`.
    * `raise_plan`: `text` and `draft_file`, one per recommendation the ruling upheld.
  * **Text sections**: `{{debate_summary}}` and `{{ruling}}`, copied from `boardroom/<week>/ruling.md`.
  * **A figure that is not shown**: its placeholder is filled with nothing. The wording around it belongs to Role C.
  * **All field names**: the keys of `numbers.json` are the return value of the numbers tool (section 4.3). No field outside this list may be added to the template without asking.
* **`payroll.md` and `growth.md`**: each recommendation states the change and cites the figures it rests on, copied only from `audit/<week>/numbers.json`.
* **`ruling.md`**: for each disagreement, which side is upheld and why, citing figures.
* **`audit_report.md`**: each check in section 5.5 with pass or fail and the rows concerned.
* **`intake_log.md`**: each file read, where it was filed and the rows it produced.

---

## 8. Open items

* **Agreed as designs, not built**: Law agreed the two designs below on 10 October. Neither is built until Law says so: the raise projection after the first full run, Day Zero after the midnight checkpoint. Until then recommendations cite current figures only, and the hand written plan stands in for Day Zero (PLAN section 15).

* **Tool mechanism and location in the repository, decided**: Python scripts in `tools/`, run by a skill with the managed Python 3.13. Check 6 passed.
* **Runtime module naming, decided and done**: renamed `tools/numbers.py` to `tools/business_numbers.py` and updated the remaining loader reference. The probe no longer needs `-P`: the local module no longer shadows Python's standard library `numbers` module.
* **File format, decided**: CSV, check 7. Every entry point explicitly passes `fmt="csv"`; the adapter retains `.xlsx` support for later.
* **Payslip format, decided**: an HTML template filled by a script (section 7). The PDF step waits on check 11.
* **Day Zero formulas**, design agreed: break even point and predicted hourly rate need an expected sales volume, and the plan file has no column for one.
  * **A planned week**: a new `planned_sales` sheet in the plan file (`product_id`, `channel`, `units_per_week`) holds the student's own expected volume, one unit per order.
  * **Predicted figures**: the hours tool and the product profit rules of section 4.3 run over that planned week. Planned take home is the total of the product profits. Predicted hourly rate and `planned_margin_percent` come out of the same tools.
  * **Break even**, optional: the model has no fixed costs, so the classic break even point does not exist. It becomes the multiple of planned sales at which the hourly rate reaches `target_hourly_rate_rm`, or "not reachable at these prices".
* **Raise plan projections**, design agreed: a claim such as "this would earn you RM2 more an hour" needs a deterministic calculation. Until it is built, recommendations cite current figures only.
  * **Replay the week**: the numbers tool runs again on the same week with one change: a new price for one product, with the same units sold. A change in units is not part of the design.
  * **Projected figures**: take home plus the change in that product's profit, over the same week minutes. A price change does not change minutes.
  * **Label**: every projection states the assumption it replays, for example "same units sold at RM18". The Auditor rejects any projection that is not tool output.
