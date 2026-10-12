# Submission Q&A sheet

## Draft status

- Point-form rehearsal answers for the hackathon submission, not a claim that the project has passed an end-to-end run.
- Use source-based answers below; replace evidence placeholders only after the relevant approvals and actual-run checks.
- The merged answer key is independently verified but still awaits Sharon's business sign-off. Its calculations validate the fixture, not Law's extraction or workflow execution.
- Built and merged into `dev`: the deterministic tools, the command line, the payslip command and template, the dataset, the answer key, the comparator, the tool layer, the model module, the runner, the prompts and the Telegram bot. Proofs 1, 2 and 4 passed with the real models on 11 October. Proof 3, the full chat round trip, passed before submission (system design, Proofs).
- Final wording and delivery belong to Damian. Do not invent user research, pricing, costs, guarantees or traction absent from the source docs.

## What problem are you solving?

- Student founders have scattered business records and rarely track their time. Sales alone do not tell them whether the work is worthwhile.
- Lembur's intended output is a weekly payslip showing take home, earnings per hour based on estimated/stated time, product economics and practical draft actions for review.
- It is a back office team in her chat app. She installs nothing; she needs only the chat app (system design, Application Layers).
- Evidence of actual user benefit: none from real users. The evidence is one fictional demo week turned into a payslip of RM2.53 an hour that flags a RM2.80 an hour loss on the bestselling keychain. No user study has happened.
- Sources: system design (Problem, Application Layers, Outputs).

## What is genuinely different?

- Receipt reading, reconciliation and chat input already exist elsewhere. They are necessary plumbing, not the innovation claim.
- Our intended distinction is correctable hours, a payslip anyone can understand, conflicting objectives debated openly, plan versus reality and action drafts awaiting approval.
- This is product positioning, not proof that no other product offers these features.
- Source: system design (Positioning).

## Could a larger platform copy this?

- Yes. A large platform could add an hourly-rate view.
- Our stated defence is the focused student audience, experience and working alongside their existing tools. We do not claim an established technical moat or validated market advantage.
- Source: system design (Positioning).

## Why not a general assistant such as OpenClaw, or WorkBuddy itself?

- **Numbers you can trust**: a general assistant does money arithmetic with the model. Ours never does: every figure comes from tested tools and is checked against an answer key.
- **No set up**: our user is a student at 2am. She will not install an assistant, obtain model keys and write instructions.
- **Narrow by design**: it cannot run commands on her machine or send anything. Nothing leaves without her approval.
- **It has an opinion**: hourly rate, profit per hour by product, plan against reality. A general assistant gives those only to someone who already knows to ask.
- **One line**: a general assistant is the workshop. Lembur is the finished tool, and we built it in such a workshop.
- Source: system design (Positioning).

## Are the hours measured?

- No. Production uses units sold and the time assumption in force on each date. Fulfilment uses order counts and channel time assumptions. Admin uses a weekly assumption; events use clear stated durations.
- Calculating those inputs deterministically does not make them measured working time.
- Accuracy depends on the student's assumptions. The correction loop makes them adjustable, not perfect.
- Sources: system design (Positioning, Hours).

## What time do you miss?

- Unplanned work such as failed batches and supply runs can be missed.
- Production is attached to units sold, not units made; this is not a complete timesheet of when labour happened.
- Stated non-event hours are not applied automatically; they go to review. Unclear event durations also go to review without a guessed hours line.
- Sources: system design (Positioning, Hours).

## What can the student correct?

- Only `minutes_per_unit`, `fulfilment_minutes_per_order` and `admin_hours_per_week` are permitted time corrections.
- Each correction updates the plan and appends a dated change-log row. It applies from the correction date onward; earlier lines retain their earlier assumption.
- This does not support arbitrary retrospective time entries or automatically recover failed-batch hours.
- `corrected` applies only from the correction date (system design, Hours). Earlier lines stay `estimate`.
- Source: system design (Hours); draft answer key “Correction and plan state”.

## Why trust Day Zero estimates?

- They are predictions based on assumptions, and the plan explicitly admits they tend to be optimistic. Weekly comparisons are intended to expose that optimism.
- The Day Zero design is agreed (system design, TODO (future)) but not built. Sharon builds it only on Law's word. Do not claim generated Day Zero output is ready.
- Night Shift reads a hand prepared baseline plan. The hand written plan file is shown as "the plan".
- Sources: system design (Positioning, System Functionality, Application Layers, TODO (future)).

## How do you handle missing or conflicting evidence?

- A duplicate is excluded from totals and reviewed. A referenced bank/receipt mismatch uses the bank amount, keeps both amounts in notes and is reviewed.
- An unreadable amount remains empty, not zero. The document is retained and the item is reviewed.
- On payslip day, an unused bank line becomes an unmatched transaction and is counted when its amount is known; it remains on the review list.
- These are specified behaviours. Actual-run evidence, `workspace/ledger_transactions.csv`: T0004 `duplicate`, T0012 `needs_review` with an empty amount, T0019 `needs_review` (document RM5.00, bank RM4.50, bank amount used) and T0020 `unmatched` (RM9.00 bank line counted).
- Sources: system design (Validation, Deterministic Tools, Reconciliation).

## Why are the displayed earnings provisional?

- The blurry expense has an unknown amount. The known-amount take home and hourly rate exclude it, so true earnings may be lower once it is readable.
- Keep that caveat beside the headline and take-home amount; request a clearer receipt rather than estimate the expense.
- Fixture values are expected results, not proof of true measured earnings or an observed run.
- Sources: system design (Conventions, Deterministic Tools); draft answer key “Validation and limitations”.

## What evidence supports cash sales?

- Cash rows are `cash_declared`; no bank evidence is expected. They may come from documents or the student's saved message, but are not bank-verified.
- Cash classification precedes duplicate matching in the specified rules. The planted duplicate uses a non-cash receipt, so that test does not establish cash-duplicate detection.
- Sources: system design (Reconciliation, Bookkeeper, Validation).

## What happens if a receipt arrives late?

- There is a known limit: after a leftover bank line has become a transaction on payslip day, a later document is not paired automatically. It appears unmatched for the student to resolve.
- Do not promise seamless late-document reconciliation or silently hide unresolved evidence.
- Source: system design (Reconciliation).

## Why do product profits not add up to take home?

- Take home uses counted ledger income and paid expenses. Product profit uses plan-based unit costs and channel costs, because bulk purchases cannot be reliably assigned by product.
- Product hourly profit uses direct production and fulfilment time. Whole-business hourly earnings include event and admin time as well.
- Those intentionally different money and time bases mean product profits do not sum to take home. Shared time is not arbitrarily allocated to products.
- Source: system design (Numbers).

## Why four agents?

- Each agent has different tools, context or objectives. Bookkeeper handles raw inputs; Payroll owns time and earnings; Growth coach owns revenue/sales recommendations and drafts; Auditor independently verifies and rules.
- Timekeeping is part of Payroll. Reconciliation is a deterministic tool, not a fifth agent.
- Agents interpret evidence and write recommendations. Tools calculate matches, totals, minutes and rates. An agent acts only through the tools the runner gives it, and the Auditor gets no tool that changes the ledger or the plan.
- Source: system design (Application Layers, Deterministic Tools, Agents, How an agent acts).

## Which models does it use?

- **Two roles**: `reason` drives the agents and needs no image input. `read` turns one image into text and is used only when a document is read.
- **Where they come from**: the model gateway the organisers provided. The tools we build with are not part of the product.
- **Which model fills which role**: proofs 1 and 2 passed with the models set in `.env`. The model names are not in the repository, so ask Law before naming one. If a proof fails, a fallback model goes in the same role.
- **Configuration, not code**: the model for each role is set in environment variables. A key never appears in the repository, a prompt, a log or a reply.
- **No framework**: calls use plain HTTPS and the standard library. There is no third party package and no agent framework.
- **Tests**: a fake model with scripted answers replays the week in seconds without a key.
- Sources: system design (Runtime, TODO (future), Proofs, Key Decisions).

## What if the model gets a number wrong?

- **It cannot write a figure of record**: every match, total, hours figure and rate comes from a deterministic tool. An agent has no other way to act than the tools the runner gives it, so this is enforced by the code, not by trust (system design, Application Layers and Rules for every agent).
- **Copied, not calculated**: Payroll, the Growth coach and the Auditor copy figures only from `audit/<week>/numbers.json`.
- **A check on what agents write**: the runner checks that every money and hours figure in the recommendations and the ruling appears in `numbers.json`. A text with a figure that does not is sent back once to the agent that wrote it, and a second failure fails the step (system design, How an agent acts).
- **A second look**: the Auditor reruns the numbers tool without writing and compares the result with the saved file (system design, Auditor).
- **No model types into the payslip**: the payslip command fills the template from `numbers.json`, and the bot copies figures into its fixed sentences (system design, Chat and Outputs).
- **Where a model can still err**: reading a document or deciding an unclear case. Those are flagged for review, not guessed, and any mismatch with the answer key is a bug to fix (system design, Validation).
- Sources: system design (Application Layers, Rules for every agent, Auditor, How an agent acts, Outputs, Validation).

## What makes the debate more than theatre?

- Payroll prioritises hourly earnings; Growth coach prioritises revenue and sales. Their conflicting objectives must be visible through recommendations supported by current figures.
- The Auditor reruns numbers, checks review coverage and source traceability, rejects arguments without figures, and rules with reasons.
- Actual evidence: `workspace/boardroom/2026-W41/payroll.md`, `workspace/boardroom/2026-W41/growth.md`, `workspace/audit/2026-W41/audit_report.md` and `workspace/boardroom/2026-W41/ruling.md`. In the run the Auditor upheld all six recommendations, each with a cited figure from `numbers.json`. An expected ruling direction in the key is not a completed debate.
- This verification design does not guarantee perfect document reading or measured hours.
- Sources: system design (Payroll, Growth coach, Auditor, Outputs).

## Can you promise the raise plan will earn more?

- No guaranteed improvement. The design is agreed, price change only, and not built. It is built on Law's word after the first full run.
- Until approved, recommendations cite current tool outputs or plan values only. Do not invent future demand or a precise hourly raise.
- Source: system design (TODO (future)).

## Does it send posts or supplier messages automatically?

- No. In the chat, the student replies "approve N" or "skip N". The bot moves an approved draft to `approvals/<week>/approved/` and she sends it herself. No agent and no model is involved in the move.
- Lembur posts and sends nothing in this version. Posting through a connector is roadmap only.
- Approval of one draft does not approve every draft.
- Evidence: not yet recorded. It needs the reply `approve 1` in a live chat and the draft appearing in `approvals/2026-W41/approved/` (proof 3).
- Sources: system design (Rules for every agent, Flow).

## Does it run on a schedule?

- No. A night starts when the student sends her message to the bot. The morning message arrives when the night finishes (system design, Flow).
- Do not present a manually started run as scheduled or unattended overnight operation.
- Source: system design (Flow).

## How did you use WorkBuddy?

- Judging criterion: Meaningful use of WorkBuddy. WorkBuddy does not have to be in the final solution under the organisers' relaxed rule, but we must show proof that we used it while building, and explain how, where and in what scenarios. The organisers' exact wording is still to be added [confirm] (system design, How WorkBuddy Was Used).
- **Not part of the product**: Lembur is our own chat bot. WorkBuddy is the platform we built it with (system design, How WorkBuddy Was Used).
- **How**: each of us works with WorkBuddy as the builder in our own checkout. We give it the docs as the source of truth, it writes the code or the content, and the result is checked before it is merged.
- **Where and in what scenarios**: the engine and its tests, the runner and the bot (once built), the dataset and answer key, and the story (identities, payslip template, deck, video script, this sheet). Before the redesign the four agents also ran as WorkBuddy skills, and a skill run of our own script passed on 10 October.
- **Evidence**: `submission/evidence/workbuddy_session_payslip_template.png` and `submission/evidence/workbuddy_session_story_drafts.png`. Claim only what the evidence pack shows WorkBuddy really did. Work done or checked by other means is not presented as WorkBuddy's.
- Sources: system design (Problem, How WorkBuddy Was Used, Proofs).

## Have you validated the project?

- The merged independent comparison and rule-check reports validate the prepared demo fixture. They do not validate extraction accuracy, the bot, approval by reply or an observed end-to-end run.
- Sharon's business sign-off remains pending. Then actual results must match the approved key for statuses, source labels, review items, minutes and money to the sen.
- Evidence: the key in `data/answer_key/`, the run outputs in `workspace/` and the row by row comparison from `python -B data/test_harness/compare_outputs.py`, which printed PASS with no difference on 11 October 08:10 (20 transactions, 14 bank lines, 20 hours lines, take home RM39.50, 15.6 hours, RM2.53 an hour). A mismatch is a bug to fix before demoing, not an acceptable result.
- Sources: system design (Validation); draft answer key validation and handoff sections.

## How long does a run take, and how reliable is it?

- Already known, from before the redesign: our scripts run from a WorkBuddy skill, the data files are CSV, the agents' instructions matched the answer key in one pass that was not run in WorkBuddy and used a different model, and the payslip template fills.
- Proofs 1, 2 and 4 passed on 11 October with the real models; proof 3, the chat round trip, passed before submission. Recorded results are under each proof in system design, Proofs. Measured duration: about five minutes for the seven nights (Law, 07:45) and 5m13s in Damian's independent replay (08:10); one night, 2026-10-05, took about 20 seconds (proof 2). One passing run is not a guarantee for every run, so each recorded run is compared again.
- If a fallback is used, disclose it. Do not present manual execution as scheduled overnight operation.
- Cost per run, pricing, monetisation and security guarantees are not specified; ask the team rather than invent a business model or assurance.
- Sources: system design (Validation, Proofs, TODO (future)).

## What happens when a student outgrows Lembur?

- The intended growth path is portable books and continued time-and-decision support alongside accounting or order software.
- Helper capabilities and integrations are future only. Current growth-related build scope is the `person` field and fixed ledger columns, not a working multi-person or integration workflow.
- More ways in are future work too: WhatsApp beside Telegram, voice notes and a hosted service. Each is a new channel or a deployment, not a new engine, and none is built.
- Do not claim a completed migration service or live connection to existing business software.
- Sources: system design (Positioning, System Functionality, TODO (future), Chat).

## What remains open before submission?

- Proof 3, the full round trip through the chat, passed before submission (system design, Proofs).
- Which model fills each role is configuration. The demo used the two named in system design, Tool Stack.
- The organisers' exact wording of the rule change (system design, How WorkBuddy Was Used).
- Sharon's story and key sign-off and the actual run comparison.
- Day Zero and the raise projection: agreed designs, not built, on Law's word.
- Payslip PDF: optional and not built (system design, Outputs). The HTML payslip is the payslip.
- Damian's total video duration and final look. WorkBuddy naming and the exact judging criterion are approved.
- Review items and unknown-expense caveats must stay visible even after the run passes its expected checks.
- Sources: system design (Problem, Proofs, Key Decisions, TODO (future)); current draft answer key.
