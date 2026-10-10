# Submission Q&A sheet

## Draft status

* Point-form rehearsal answers for the hackathon submission, not a claim that the project has passed an end-to-end run.
* Use source-based answers below; replace evidence placeholders only after the relevant approvals and actual-run checks.
* The merged answer key is independently verified but still awaits Sharon's business sign-off. Its calculations validate the fixture, not Law's extraction or workflow execution.
* CSV is the chosen format, using the standard library. The four plan files are `plan_products.csv`, `plan_channels.csv`, `plan_assumptions.csv` and `plan_change_log.csv`; the three ledger files are `ledger_transactions.csv`, `ledger_bank_lines.csv` and `ledger_hours.csv`. The demo and answer-key CSV files are authoritative; old workbook references in `answer_key.md` and `messages.md` await Sharon's update.
* Final submission wording belongs to Damian. Do not invent user research, pricing, costs, guarantees or traction absent from the source docs.
* Source authority: README, then PLAN, then SYSTEM_DESIGN. SYSTEM_DESIGN governs behaviour and data; PLAN governs scope and schedule.

## What problem are you solving?

* Student founders have scattered business records and rarely track their time. Sales alone do not tell them whether the work is worthwhile.
* Lembur's intended output is a weekly payslip showing take home, earnings per hour based on estimated/stated time, product economics and practical draft actions for review.
* Evidence of actual user benefit: `{verified_user_value_evidence}`. Do not imply a real user study has happened.
* Sources: PLAN section 2; DESIGN section 7.

## What is genuinely different?

* Receipt reading, reconciliation and chat input already exist elsewhere. They are necessary plumbing, not the innovation claim.
* Our intended distinction is correctable hours, a payslip anyone can understand, conflicting objectives debated openly, plan versus reality and action drafts awaiting approval.
* This is product positioning, not proof that no other product offers these features.
* Source: PLAN section 3.

## Could a larger platform copy this?

* Yes. A large platform could add an hourly-rate view.
* Our stated defence is the focused student audience, experience and working alongside their existing tools. We do not claim an established technical moat or validated market advantage.
* Source: PLAN section 3.

## Are the hours measured?

* No. Production uses units sold and the time assumption in force on each date. Fulfilment uses order counts and channel time assumptions. Admin uses a weekly assumption; events use clear stated durations.
* Calculating those inputs deterministically does not make them measured working time.
* Accuracy depends on the student's assumptions. The correction loop makes them adjustable, not perfect.
* Sources: PLAN section 3; DESIGN section 4.2.

## What time do you miss?

* Unplanned work such as failed batches and supply runs can be missed.
* Production is attached to units sold, not units made; this is not a complete timesheet of when labour happened.
* Stated non-event hours are not applied automatically; they go to review. Unclear event durations also go to review without a guessed hours line.
* Sources: PLAN section 3; DESIGN section 4.2.

## What can the student correct?

* Only `minutes_per_unit`, `fulfilment_minutes_per_order` and `admin_hours_per_week` are permitted time corrections.
* Each correction updates the plan and appends a dated change-log row. It applies from the correction date onward; earlier lines retain their earlier assumption.
* This does not support arbitrary retrospective time entries or automatically recover failed-batch hours.
* The source-label rule is now incorporated in DESIGN section 4.2. Production, fulfilment and admin lines before the first correction to their field retain `source=estimate`, even when their old value is recovered from a later change-log row. A line is `corrected` only when its field has a correction dated on or before the line date.
* Source: DESIGN section 4.2.

## Why trust Day Zero estimates?

* They are predictions based on assumptions, and the plan explicitly admits they tend to be optimistic. Weekly comparisons are intended to expose that optimism.
* The design is agreed: `planned_sales` holds the student's expected product/channel volume; a planned week uses the same hours and product-profit engine. Optional break-even means the sales multiple needed to reach the target hourly rate, or not reachable at these prices, not classic fixed-cost break-even.
* Sharon owns Day Zero. Building waits for Law's authorisation after the midnight checkpoint; agreed formulas are not generated or validated Day Zero output.
* Night Shift can read a hand-prepared baseline plan. PLAN section 15 already fixes that fallback and the cut order; it is not an open decision.
* Sources: PLAN sections 3, 4, 13 and 15; DESIGN sections 1 and 8.

## How do you handle missing or conflicting evidence?

* A duplicate is excluded from totals and reviewed. A referenced bank/receipt mismatch uses the bank amount, keeps both amounts in notes and is reviewed.
* An unreadable amount remains empty, not zero. The document is retained and the item is reviewed.
* On payslip day, an unused bank line becomes an unmatched transaction and is counted when its amount is known; it remains on the review list.
* These are specified behaviours. Actual-run evidence: `{verified_reconciliation_output}`.
* Sources: PLAN section 10; DESIGN sections 4 and 4.1.

## Why are the displayed earnings provisional?

* The blurry expense has an unknown amount. The known-amount take home and hourly rate exclude it, so true earnings may be lower once it is readable.
* Keep that caveat beside the headline and take-home amount; request a clearer receipt rather than estimate the expense.
* Fixture values are expected results, not proof of true measured earnings or an observed run.
* Sources: DESIGN sections 2 and 4; draft answer key “Validation and limitations”.

## What evidence supports cash sales?

* Cash rows are `cash_declared`; no bank evidence is expected. They may come from documents or the student's saved message, but are not bank-verified.
* Cash classification precedes duplicate matching in the specified rules. The planted duplicate uses a non-cash receipt, so that test does not establish cash-duplicate detection.
* Sources: DESIGN sections 4.1 and 5.2; PLAN section 10.

## What happens if a receipt arrives late?

* There is a known limit: after a leftover bank line has become a transaction on payslip day, a later document is not paired automatically. It appears unmatched for the student to resolve.
* Do not promise seamless late-document reconciliation or silently hide unresolved evidence.
* Source: DESIGN section 4.1.

## Why do product profits not add up to take home?

* Take home uses counted ledger income and paid expenses. Product profit uses plan-based unit costs and channel costs, because bulk purchases cannot be reliably assigned by product.
* Product hourly profit uses direct production and fulfilment time. Whole-business hourly earnings include event and admin time as well.
* Those intentionally different money and time bases mean product profits do not sum to take home. Shared time is not arbitrarily allocated to products.
* Source: DESIGN section 4.3.

## Why four agents?

* Each agent has different tools, context or objectives. Bookkeeper handles raw inputs; Payroll owns time and earnings; Growth coach owns revenue/sales recommendations and drafts; Auditor independently verifies and rules.
* Timekeeping is part of Payroll. Reconciliation is a deterministic tool, not a fifth agent.
* Agents interpret evidence and write recommendations. Tools calculate matches, totals, minutes and rates.
* The four skills are written in the repository's `skills/` directory at commit `541ef89`. PLAN section 13's 16:30 snapshot saying they are not built is stale on that point. Written files do not establish installation or a visible team run; Law's check 5 remains unrecorded. No real agent run outputs were present in this local `workspace/` at the time of this refresh; this does not establish what exists on another teammate's machine.
* Sources: DESIGN sections 1, 4 and 5; PLAN sections 12 and 13; current repository skills.

## What makes the debate more than theatre?

* Payroll prioritises hourly earnings; Growth coach prioritises revenue and sales. Their conflicting objectives must be visible through recommendations supported by current figures.
* Every numerical recommendation figure is copied only from `workspace/audit/<week>/numbers.json`, not directly from plan values or any other tool output. Amount citations in transaction review notes remain valid review evidence, not an alternative recommendation source.
* The Auditor reruns numbers without writing, compares against the saved file, checks source traceability, rejects unsupported arguments and rules with reasons.
* Full review coverage is required by both the design and Auditor instructions: every transaction with status `unmatched`, `duplicate` or `needs_review`, plus every line of `review_items.md`, must reach the final payslip. Coverage in a real output still needs verification.
* Actual evidence: `{payroll_file}`, `{growth_file}`, `{audit_report}` and `{ruling_file}`. An expected ruling direction in the key is not a completed debate.
* The Growth skill permits upheld recommendations needing no customer or supplier message to have no draft; DESIGN section 7 says each upheld recommendation points to a draft. Confirm that mapping with Law rather than fabricate drafts.
* This verification design does not guarantee perfect document reading or measured hours.
* Sources: DESIGN sections 4.3, 5.3 to 5.5 and 7; Growth coach and Auditor skill instructions.

## Can you promise the raise plan will earn more?

* No guaranteed improvement. The agreed projection design replays a price change for one product with the same units sold and the same week minutes; it does not predict demand.
* Building waits for Law's word after the first full run. Current skills reject all projections until implementation and instructions are verified; quote no projected gains now.
* Recommendations cite current figures only, copied from `workspace/audit/<week>/numbers.json`. Do not invent future demand or a precise hourly raise.
* Sources: DESIGN sections 4.3, 5.1, 7 and 8; Growth coach and Auditor skill instructions.

## Does it send posts or supplier messages automatically?

* No. The current system never sends or posts a draft, even after approval. The student sends an approved draft herself; connector-based posting is future work only.
* Drafts wait for the student's individual approval. Approval of one draft does not approve every draft.
* `approve N` moves that numbered draft from `workspace/approvals/<week>/` into `workspace/approvals/<week>/approved/` and confirms by reply. `skip N` leaves it pending in place, not rejected, and also confirms by reply. This is a file move in the skill instructions, not an approval command or automatic delivery.
* Evidence: `{verified_individual_approval_and_file_move}`. Do not infer exercised approval controls from draft files alone.
* Sources: PLAN section 4; DESIGN sections 5.1 and 6.1; Growth coach skill instructions.

## How is WorkBuddy doing meaningful work?

* Judging criterion: Meaningful use of WorkBuddy, following PLAN section 1 and Damian's approved naming decision.
* The source plan requires WorkBuddy to perform real task execution: authorised file processing, agent tasks, deterministic calculation, verification and generated deliverables, not merely chat.
* Show `{verified_execution_evidence}` and `{generated_output_references}`. Claim only the features confirmed by the recorded check results and actual run.
* Automated scheduling, parallel tasks or external messaging need their own evidence; a manually started sequential run proves none of them. A morning result notification is distinct from sending a draft, which is excluded.
* Sources: PLAN sections 1, 11 and 12; DESIGN section 6.1.

## Have you validated the project?

* The independent comparison and rule-check reports validate the prepared demo fixture. Unit tests and CLI fixture replay are not OCR accuracy, agent collaboration or end-to-end workflow validation.
* The independent CSV `compare_outputs.py` harness uses the standard library, compares ledger fields, recalculates figures and checks plan corrections. It is not a byte comparison: transaction `notes` and `description` are excluded, and hours lines are keyed by date, activity, product and `assumption_ref`, never `entry_id`.
* Do not claim the comparator audits all free-text review explanations or rulings. Auditor review coverage and evidence checks are separate requirements, not presumed successful results.
* Sharon's business sign-off remains pending. Then actual results must match the approved key for statuses, source labels, review items, minutes and money to the sen.
* Evidence: `{approved_answer_key}`, `{actual_run_outputs}` and `{row_by_row_comparison}`. A mismatch is a bug to fix before demoing, not an acceptable result.
* Sources: PLAN section 10; DESIGN sections 4.2 and 5.5; draft answer key validation and handoff sections.

## What does a run cost, and how reliable is it?

* Some checks are recorded, not all: check 6 passed for a skill invoking a deterministic script; check 7 chose standard-library CSV because `openpyxl` was absent. This does not prove a full agent run.
* Check 11 records sample PDF export without installs using installed Chrome and managed Node. The last export took 0.562 seconds, not a full run duration. Damian approved the sample look at 17:23 on 10 October; repeatable Payroll conversion and populated real-output pagination remain unverified.
* Full-run runtime and credit use remain unknown; Law owns check 8 and visible team check 5, neither recorded. Sharon's results remain unrecorded for trigger 1, voice 2, scheduling 3, OCR 4, morning delivery 9 and photo intake 10.
* Use `{recorded_first_hour_check_results}`, `{measured_run_duration}` and `{measured_run_credit_usage}` with their actual owners and scope; do not invent missing results.
* If a fallback is used, disclose it. Do not present manual execution as scheduled overnight operation.
* Pricing, monetisation and security guarantees are not specified; ask the team rather than invent a business model or assurance.
* Sources: PLAN sections 0, 12 and 15; DESIGN section 0.

## What happens when a student outgrows Lembur?

* The intended growth path is portable books and continued time-and-decision support alongside accounting or order software.
* Helper capabilities and integrations are future only. Current growth-related build scope is the `person` field and fixed ledger columns, not a working multi-person or integration workflow.
* Do not claim a completed migration service or live connection to existing business software.
* Sources: PLAN sections 3, 4 and 16.

## What remains open before submission?

* The template format is settled and `submission/payslip_template.html` exists in dev PR 11. Remaining gates are Law's integration and acceptance, a repeatable Payroll PDF method and populated real-output pagination. Damian's sample visual approval is not approval of a real run's output.
* Law's recorded installation/visible-team check 5, full-run credit check 8 and measured full-run runtime; Sharon's platform checks 1, 2, 3, 4, 9 and 10.
* Sharon's story/key sign-off, stale workbook-reference updates and comparison of actual agent output with the independently verified key.
* Day Zero and price-only projections are agreed designs with build gates, not unresolved formulas or ownership. Sharon owns Day Zero; Law authorises it after the midnight checkpoint and projections after the first full run. No projected gains are currently allowed.
* Confirm the upheld-recommendation mapping where the Growth skill requires no draft but DESIGN section 7 expects a draft link; do not invent one.
* Damian's total video duration and final real-output look. The sample PDF look, WorkBuddy naming and exact judging criterion are approved; PLAN section 15's fallback and cut order remain fixed.
* Review items and unknown-expense caveats must stay visible even after the run passes its expected checks.
* Sources: PLAN sections 12, 13, 15 and 18; DESIGN sections 7 and 8; current draft answer key and skill instructions.
