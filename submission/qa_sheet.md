# Submission Q&A sheet

## Draft status

- Point-form rehearsal answers for the hackathon submission, not a claim that the project has passed an end-to-end run.
- Use source-based answers below; replace evidence placeholders only after the relevant approvals and actual-run checks.
- The merged answer key is independently verified but still awaits Sharon's business sign-off. Its calculations validate the fixture, not Law's extraction or workflow execution.
- Final wording and delivery belong to Damian. Do not invent user research, pricing, costs, guarantees or traction absent from the source docs.

## What problem are you solving?

- Student founders have scattered business records and rarely track their time. Sales alone do not tell them whether the work is worthwhile.
- Lembur's intended output is a weekly payslip showing take home, earnings per hour based on estimated/stated time, product economics and practical draft actions for review.
- Evidence of actual user benefit: `{verified_user_value_evidence}`. Do not imply a real user study has happened.
- Sources: PLAN section 2; DESIGN section 7.

## What is genuinely different?

- Receipt reading, reconciliation and chat input already exist elsewhere. They are necessary plumbing, not the innovation claim.
- Our intended distinction is correctable hours, a payslip anyone can understand, conflicting objectives debated openly, plan versus reality and action drafts awaiting approval.
- This is product positioning, not proof that no other product offers these features.
- Source: PLAN section 3.

## Could a larger platform copy this?

- Yes. A large platform could add an hourly-rate view.
- Our stated defence is the focused student audience, experience and working alongside their existing tools. We do not claim an established technical moat or validated market advantage.
- Source: PLAN section 3.

## Are the hours measured?

- No. Production uses units sold and the time assumption in force on each date. Fulfilment uses order counts and channel time assumptions. Admin uses a weekly assumption; events use clear stated durations.
- Calculating those inputs deterministically does not make them measured working time.
- Accuracy depends on the student's assumptions. The correction loop makes them adjustable, not perfect.
- Sources: PLAN section 3; DESIGN section 4.2.

## What time do you miss?

- Unplanned work such as failed batches and supply runs can be missed.
- Production is attached to units sold, not units made; this is not a complete timesheet of when labour happened.
- Stated non-event hours are not applied automatically; they go to review. Unclear event durations also go to review without a guessed hours line.
- Sources: PLAN section 3; DESIGN section 4.2.

## What can the student correct?

- Only `minutes_per_unit`, `fulfilment_minutes_per_order` and `admin_hours_per_week` are permitted time corrections.
- Each correction updates the plan and appends a dated change-log row. It applies from the correction date onward; earlier lines retain their earlier assumption.
- This does not support arbitrary retrospective time entries or automatically recover failed-batch hours.
- The draft key records a source-label clarification not yet incorporated into the source docs. Confirm its treatment with the team before treating it as a new specification.
- Source: DESIGN section 4.2; draft answer key “Correction and plan state”.

## Why trust Day Zero estimates?

- They are predictions based on assumptions, and the plan explicitly admits they tend to be optimistic. Weekly comparisons are intended to expose that optimism.
- Expected-volume inputs and prediction/break-even formulas are unconfirmed. Do not claim generated Day Zero output is ready until those rules and the workflow are agreed and tested.
- Night Shift can read a hand-prepared baseline plan. Showing that fallback in the submission requires Damian's confirmed presentation decision.
- Sources: PLAN sections 3, 4 and 15; DESIGN sections 1 and 8.

## How do you handle missing or conflicting evidence?

- A duplicate is excluded from totals and reviewed. A referenced bank/receipt mismatch uses the bank amount, keeps both amounts in notes and is reviewed.
- An unreadable amount remains empty, not zero. The document is retained and the item is reviewed.
- On payslip day, an unused bank line becomes an unmatched transaction and is counted when its amount is known; it remains on the review list.
- These are specified behaviours. Actual-run evidence: `{verified_reconciliation_output}`.
- Sources: PLAN section 10; DESIGN sections 4 and 4.1.

## Why are the displayed earnings provisional?

- The blurry expense has an unknown amount. The known-amount take home and hourly rate exclude it, so true earnings may be lower once it is readable.
- Keep that caveat beside the headline and take-home amount; request a clearer receipt rather than estimate the expense.
- Fixture values are expected results, not proof of true measured earnings or an observed run.
- Sources: DESIGN sections 2 and 4; draft answer key “Validation and limitations”.

## What evidence supports cash sales?

- Cash rows are `cash_declared`; no bank evidence is expected. They may come from documents or the student's saved message, but are not bank-verified.
- Cash classification precedes duplicate matching in the specified rules. The planted duplicate uses a non-cash receipt, so that test does not establish cash-duplicate detection.
- Sources: DESIGN sections 4.1 and 5.2; PLAN section 10.

## What happens if a receipt arrives late?

- There is a known limit: after a leftover bank line has become a transaction on payslip day, a later document is not paired automatically. It appears unmatched for the student to resolve.
- Do not promise seamless late-document reconciliation or silently hide unresolved evidence.
- Source: DESIGN section 4.1.

## Why do product profits not add up to take home?

- Take home uses counted ledger income and paid expenses. Product profit uses plan-based unit costs and channel costs, because bulk purchases cannot be reliably assigned by product.
- Product hourly profit uses direct production and fulfilment time. Whole-business hourly earnings include event and admin time as well.
- Those intentionally different money and time bases mean product profits do not sum to take home. Shared time is not arbitrarily allocated to products.
- Source: DESIGN section 4.3.

## Why four agents?

- Each agent has different tools, context or objectives. Bookkeeper handles raw inputs; Payroll owns time and earnings; Growth coach owns revenue/sales recommendations and drafts; Auditor independently verifies and rules.
- Timekeeping is part of Payroll. Reconciliation is a deterministic tool, not a fifth agent.
- Agents interpret evidence and write recommendations. Tools calculate matches, totals, minutes and rates.
- Source: DESIGN sections 1, 4 and 5.

## What makes the debate more than theatre?

- Payroll prioritises hourly earnings; Growth coach prioritises revenue and sales. Their conflicting objectives must be visible through recommendations supported by current figures.
- The Auditor reruns numbers, checks review coverage and source traceability, rejects arguments without figures, and rules with reasons.
- Actual evidence: `{payroll_file}`, `{growth_file}`, `{audit_report}` and `{ruling_file}`. An expected ruling direction in the key is not a completed debate.
- This verification design does not guarantee perfect document reading or measured hours.
- Sources: DESIGN sections 5.3 to 5.5 and 7.

## Can you promise the raise plan will earn more?

- No guaranteed improvement. Quantified projections require an agreed deterministic calculation, and that rule remains unconfirmed.
- Until approved, recommendations cite current tool outputs or plan values only. Do not invent future demand or a precise hourly raise.
- Source: DESIGN section 8.

## Does it send posts or supplier messages automatically?

- Drafts wait for the student's individual approval. Approval of one draft does not approve every draft.
- Nothing is posted or sent before that draft is approved. Whether final delivery is implemented must be established by Law's actual execution evidence.
- Evidence: `{verified_individual_approval_and_delivery}`. Do not infer approval controls or completed sending from draft files alone.
- Sources: DESIGN sections 5.1 and 6.1.

## How is WorkBuddy doing meaningful work?

- Judging criterion: Meaningful use of WorkBuddy, following PLAN section 1 and Damian's approved naming decision.
- The source plan requires WorkBuddy to perform real task execution: authorised file processing, agent tasks, deterministic calculation, verification and generated deliverables, not merely chat.
- Show `{verified_execution_evidence}` and `{generated_output_references}`. Claim only the features confirmed by the recorded check results and actual run.
- Automated scheduling, parallel tasks or external messaging need their own evidence; a manually started sequential run proves none of them.
- Sources: PLAN sections 1, 11 and 12; DESIGN section 6.1.

## Have you validated the project?

- The merged independent comparison and rule-check reports validate the prepared demo fixture. They do not validate extraction accuracy, triggers, approval actions or an observed end-to-end run.
- Sharon's business sign-off remains pending. Then actual results must match the approved key for statuses, source labels, review items, minutes and money to the sen.
- Evidence: `{approved_answer_key}`, `{actual_run_outputs}` and `{row_by_row_comparison}`. A mismatch is a bug to fix before demoing, not an acceptable result.
- Sources: PLAN section 10; draft answer key validation and handoff sections.

## What does a run cost, and how reliable is it?

- The source docs do not record results for first-hour runtime, scheduling, extraction, file-format, trigger or credit-use checks.
- Use `{recorded_first_hour_check_results}`, `{measured_run_duration}` and `{measured_run_credit_usage}` from Law; do not invent them.
- If a fallback is used, disclose it. Do not present manual execution as scheduled overnight operation.
- Pricing, monetisation and security guarantees are not specified; ask the team rather than invent a business model or assurance.
- Sources: PLAN sections 0, 12 and 15; DESIGN section 0.

## What happens when a student outgrows Lembur?

- The intended growth path is portable books and continued time-and-decision support alongside accounting or order software.
- Helper capabilities and integrations are future only. Current growth-related build scope is the `person` field and fixed ledger columns, not a working multi-person or integration workflow.
- Do not claim a completed migration service or live connection to existing business software.
- Sources: PLAN sections 3, 4 and 16.

## What remains open before submission?

- Law's fillable template format and recorded first-hour results.
- Sharon's story/key sign-off and actual-run comparison.
- Day Zero formulas, owner and any approved presentation fallback.
- Raise projections, which remain excluded.
- Damian's total video duration and final look. WorkBuddy naming and the exact judging criterion are approved.
- Review items and unknown-expense caveats must stay visible even after the run passes its expected checks.
- Sources: PLAN sections 12, 13, 15 and 18; DESIGN section 8; current draft answer key.
