# Submission Q&A sheet

## Draft status

- Point-form rehearsal answers for the hackathon submission, not a claim that the project has passed an end-to-end run.
- Use source-based answers below; replace evidence placeholders only after the relevant approvals and actual-run checks.
- The merged answer key is independently verified but still awaits Sharon's business sign-off. Its calculations validate the fixture, not Law's extraction or workflow execution.
- The runner, the model module, the bot and the prompts are written as designs and are not built yet (PLAN section 13). Answers about them describe the design until their proofs in PLAN section 12 are recorded.
- Final wording and delivery belong to Damian. Do not invent user research, pricing, costs, guarantees or traction absent from the source docs.

## What problem are you solving?

- Student founders have scattered business records and rarely track their time. Sales alone do not tell them whether the work is worthwhile.
- Lembur's intended output is a weekly payslip showing take home, earnings per hour based on estimated/stated time, product economics and practical draft actions for review.
- It is a back office team in her chat app. She installs nothing; she needs only the chat app (design section 1).
- Evidence of actual user benefit: `{verified_user_value_evidence}`. Do not imply a real user study has happened.
- Sources: PLAN section 2; DESIGN sections 1 and 7.

## What is genuinely different?

- Receipt reading, reconciliation and chat input already exist elsewhere. They are necessary plumbing, not the innovation claim.
- Our intended distinction is correctable hours, a payslip anyone can understand, conflicting objectives debated openly, plan versus reality and action drafts awaiting approval.
- This is product positioning, not proof that no other product offers these features.
- Source: PLAN section 3.

## Could a larger platform copy this?

- Yes. A large platform could add an hourly-rate view.
- Our stated defence is the focused student audience, experience and working alongside their existing tools. We do not claim an established technical moat or validated market advantage.
- Source: PLAN section 3.

## Why not a general assistant such as OpenClaw, or WorkBuddy itself?

- **Numbers you can trust**: a general assistant does money arithmetic with the model. Ours never does: every figure comes from tested tools and is checked against an answer key.
- **No set up**: our user is a student at 2am. She will not install an assistant, obtain model keys and write instructions.
- **Narrow by design**: it cannot run commands on her machine or send anything. Nothing leaves without her approval.
- **It has an opinion**: hourly rate, profit per hour by product, plan against reality. A general assistant gives those only to someone who already knows to ask.
- **One line**: a general assistant is the workshop. Lembur is the finished tool, and we built it in such a workshop.
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
- `corrected` applies only from the correction date (design section 4.2). Earlier lines stay `estimate`.
- Source: DESIGN section 4.2; draft answer key “Correction and plan state”.

## Why trust Day Zero estimates?

- They are predictions based on assumptions, and the plan explicitly admits they tend to be optimistic. Weekly comparisons are intended to expose that optimism.
- The Day Zero design is agreed (design section 8) but not built. Sharon builds it only on Law's word. Do not claim generated Day Zero output is ready.
- Night Shift can read a hand prepared baseline plan. Law decides under the fixed cut order (PLAN section 15). The hand written plan file is shown as "the plan".
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
- Agents interpret evidence and write recommendations. Tools calculate matches, totals, minutes and rates. An agent acts only through the tools the runner gives it, and the Auditor gets no tool that changes the ledger or the plan.
- Source: DESIGN sections 1, 4, 5 and 6.4.

## Which models does it use?

- **Two roles**: `reason` drives the agents and needs no image input. `read` turns one image into text and is used only when a document is read.
- **Where they come from**: the model gateway the organisers provided. The tools we build with are not part of the product.
- **Which model fills which role**: still open. It waits on proofs 1 and 2 (PLAN section 12). Do not name a model before then. If a proof fails, a fallback model goes in the same role.
- **Configuration, not code**: the model for each role is set in environment variables. A key never appears in the repository, a prompt, a log or a reply.
- **No framework**: calls use plain HTTPS and the standard library. There is no third party package and no agent framework.
- **Tests**: a fake model with scripted answers replays the week in seconds without a key.
- Sources: DESIGN sections 6.3 and 8; PLAN sections 12 and 18.

## What if the model gets a number wrong?

- **It cannot write a figure of record**: every match, total, hours figure and rate comes from a deterministic tool. An agent has no other way to act than the tools the runner gives it, so this is enforced by the code, not by trust (design sections 1 and 5.1).
- **Copied, not calculated**: Payroll, the Growth coach and the Auditor copy figures only from `audit/<week>/numbers.json`.
- **A check on what agents write**: the runner checks that every money and hours figure in the recommendations and the ruling appears in `numbers.json`. A text with a figure that does not is sent back once to the agent that wrote it, and a second failure fails the step (design section 6.4).
- **A second look**: the Auditor reruns the numbers tool without writing and compares the result with the saved file (design section 5.5).
- **No model types into the payslip**: the payslip command fills the template from `numbers.json`, and the bot copies figures into its fixed sentences (design sections 6.5 and 7).
- **Where a model can still err**: reading a document or deciding an unclear case. Those are flagged for review, not guessed, and any mismatch with the answer key is a bug to fix (PLAN section 10).
- Sources: DESIGN sections 1, 5.1, 5.5, 6.4 and 7; PLAN section 10.

## What makes the debate more than theatre?

- Payroll prioritises hourly earnings; Growth coach prioritises revenue and sales. Their conflicting objectives must be visible through recommendations supported by current figures.
- The Auditor reruns numbers, checks review coverage and source traceability, rejects arguments without figures, and rules with reasons.
- Actual evidence: `{payroll_file}`, `{growth_file}`, `{audit_report}` and `{ruling_file}`. An expected ruling direction in the key is not a completed debate.
- This verification design does not guarantee perfect document reading or measured hours.
- Sources: DESIGN sections 5.3 to 5.5 and 7.

## Can you promise the raise plan will earn more?

- No guaranteed improvement. The design is agreed, price change only, and not built. It is built on Law's word after the first full run.
- Until approved, recommendations cite current tool outputs or plan values only. Do not invent future demand or a precise hourly raise.
- Source: DESIGN section 8.

## Does it send posts or supplier messages automatically?

- No. In the chat, the student replies "approve N" or "skip N". The bot moves an approved draft to `approvals/<week>/approved/` and she sends it herself. No agent and no model is involved in the move.
- Lembur posts and sends nothing in this version. Posting through a connector is roadmap only.
- Approval of one draft does not approve every draft.
- Evidence: `{verified_individual_approval_evidence}`.
- Sources: DESIGN sections 5.1 and 6.1.

## Does it run on a schedule?

- No. A night starts when the student sends her message to the bot. The morning message arrives when the night finishes (design section 6.1).
- Do not present a manually started run as scheduled or unattended overnight operation.
- Source: DESIGN section 6.1.

## How did you use WorkBuddy?

- Judging criterion: Meaningful use of WorkBuddy. WorkBuddy does not have to be in the final solution under the organisers' relaxed rule, but we must show proof that we used it while building, and explain how, where and in what scenarios. The organisers' exact wording is still to be added [confirm] (PLAN section 1).
- **Not part of the product**: Lembur is our own chat bot. WorkBuddy is the platform we built it with (PLAN section 11).
- **How**: each of us works with WorkBuddy as the builder in our own checkout. We give it the docs as the source of truth, it writes the code or the content, and the result is checked before it is merged.
- **Where and in what scenarios**: the engine and its tests, the runner and the bot (once built), the dataset and answer key, and the story (identities, payslip template, deck, video script, this sheet). Before the redesign the four agents also ran as WorkBuddy skills, and a skill run of our own script passed on 10 October.
- **Insurance**: one recorded run of our agents inside WorkBuddy (PLAN section 12, proof 5). Show `{workbuddy_recorded_run_reference}` only once it is recorded.
- **Evidence**: `{evidence_pack_references}` from `submission/evidence/`. Claim only what the evidence pack shows WorkBuddy really did. Work done or checked by other means is not presented as WorkBuddy's.
- Sources: PLAN sections 1, 11 and 12.

## Have you validated the project?

- The merged independent comparison and rule-check reports validate the prepared demo fixture. They do not validate extraction accuracy, the bot, approval by reply or an observed end-to-end run.
- Sharon's business sign-off remains pending. Then actual results must match the approved key for statuses, source labels, review items, minutes and money to the sen.
- Evidence: `{approved_answer_key}`, `{actual_run_outputs}` and `{row_by_row_comparison}`. A mismatch is a bug to fix before demoing, not an acceptable result.
- Sources: PLAN section 10; draft answer key validation and handoff sections.

## How long does a run take, and how reliable is it?

- Already known, from before the redesign (PLAN section 12): our scripts run from a WorkBuddy skill, the data files are CSV, the agents' instructions matched the answer key in one pass that was not run in WorkBuddy and used a different model, and the payslip template fills.
- Open: proofs 1 to 5 in PLAN section 12. Use `{recorded_proof_results}` from the owner of each proof, and `{measured_run_duration}` from Law; do not invent them.
- If a fallback is used, disclose it. Do not present manual execution as scheduled overnight operation.
- Cost per run, pricing, monetisation and security guarantees are not specified; ask the team rather than invent a business model or assurance.
- Sources: PLAN sections 10, 12 and 15; DESIGN sections 0 and 8.

## What happens when a student outgrows Lembur?

- The intended growth path is portable books and continued time-and-decision support alongside accounting or order software.
- Helper capabilities and integrations are future only. Current growth-related build scope is the `person` field and fixed ledger columns, not a working multi-person or integration workflow.
- More ways in are future work too: WhatsApp beside Telegram, voice notes and a hosted service. Each is a new channel or a deployment, not a new engine, and none is built.
- Do not claim a completed migration service or live connection to existing business software.
- Sources: PLAN sections 3, 4 and 16; DESIGN section 6.5.

## What remains open before submission?

- Open proofs: 1 to 5 (PLAN section 12).
- Which model fills each role (proofs 1 and 2), and who takes the agent orchestration and Telegram packages, which is marked [confirm] (PLAN sections 13 and 18).
- The organisers' exact wording of the rule change (PLAN section 1).
- Sharon's story and key sign-off and the actual run comparison.
- Day Zero and the raise projection: agreed designs, not built, on Law's word.
- Payslip PDF: optional and not built (design section 7). The HTML payslip is the payslip.
- Damian's total video duration and final look. WorkBuddy naming and the exact judging criterion are approved.
- Review items and unknown-expense caveats must stay visible even after the run passes its expected checks.
- Sources: PLAN sections 1, 12, 13, 15 and 18; DESIGN section 8; current draft answer key.
