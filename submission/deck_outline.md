# Submission deck outline

## Draft status

- Content draft for the hackathon submission, not final slides or a product advertisement.
- Proposed slide sequence; slide count, speaking duration and final visual treatment await Damian's review.
- These notes supply the content for the final slides and documentation. If WorkBuddy is used to make them, capture the session for the evidence pack (PLAN section 11).
- The story: Lembur is a back office team in the student's chat app. She installs nothing. WorkBuddy is the platform we built it with, not part of the running product (PLAN section 11).
- Professional-colleague role titles and warm, student-first direction follow the confirmed design choices.
- Aisyah is the fictional persona in the merged demo dataset. Her story and the independently verified draft answer key still await Sharon's business sign-off.
- Built and merged into `dev`: the deterministic tools, the command line, the payslip command and template, the dataset, the answer key, the comparator, the tool layer, the model module, the runner, the prompts and the Telegram bot, each with its tests. Proofs 1, 2 and 4 passed on 11 October with the real models. Proof 3, the full round trip through the chat, is still open: show chat scenes only after it is recorded (PLAN section 12).
- Figures below are real outputs of the recorded run of 11 October 08:10 (PLAN section 12, proof 4), which the comparator passed with no difference. They are fictional demo data. Never invent a figure.
- Replace placeholders only with traceable, approved evidence. Do not call fixture checks a successful application run.

## Judging criteria: PLAN section 1

- Real problem and user value.
- Agentic workflow.
- Meaningful use of WorkBuddy: as written, WorkBuddy is the execution platform. Under the organisers' rule change we show it as our build platform (slide 9).
- End-to-end execution.
- Usable and verifiable results.
- Name WorkBuddy as the build platform and say only what it really did (PLAN section 11).

## Slide 1: What does your side business pay for your time?

- Criteria: real problem and user value.
- Main message: student founders can see orders coming in without knowing what the business earns per hour of their time.
- Supporting points: scattered documents, informal payments, late-night data entry and untracked working time.
- Proposed visual: student context beside a messy-input illustration; use demo material only.
- Evidence slot: `{approved_persona_context}`. Do not invent testimonials, demand validation or user adoption.
- Source: PLAN sections 2 and 3.

## Slide 2: A payslip and a practical next step

- Criteria: real problem and user value; usable and verifiable results.
- Main message: Lembur turns business records into a readable weekly payslip and drafts of changes the student can review, all in her chat app.
- Show the intended chain: what you took home → time used → earnings per hour → evidence-led decisions → approval-ready drafts.
- Night Shift is the build priority and can read a hand prepared baseline plan.
- Day Zero: the design is agreed (design section 8) but not built. The Night Shift reads a hand written plan file, shown as "the plan" (PLAN section 15, cut 1). Law decides when Day Zero is built.
- Evidence: `workspace/payslips/2026-W41.html` and `workspace/approvals/2026-W41/01_instagram_post.md`.
- Source: PLAN sections 2 and 4; DESIGN sections 1, 6 and 8.

## Slide 3: One message, a sequence of real work

- Criteria: agentic workflow; end-to-end execution.
- Map this slide to the six capabilities in PLAN section 1:
  - **Understanding the goal**: the bot and the Bookkeeper read the nightly message.
  - **Planning tasks**: the plan for the night, written before any agent runs (design section 6.1).
  - **Executing actions**: agents act through tools (design section 6.4).
  - **Collaborating and validating**: Payroll argues against the Growth coach, and the Auditor rules.
  - **Integrating results**: the payslip.
  - **Delivering the final outcome**: the morning message with the payslip file.
- Intended path, all in the student's chat app: message and files → plan for the night → intake → reconciliation → ledger → hours and earnings → recommendations → audit and ruling → drafts → payslip → morning message (design section 6.1). The drafts come before the payslip because the payslip points to them.
- Show a continuous recorded run. Starting request: the Sunday 2026-10-11 message in `data/demo/messages.md`, sent with `order_2026-10-11_zahra.png` and `bank_statement_2026-W41_SYNTHETIC.csv`. Run: the recorded run of 11 October 08:10 (PLAN section 12, proof 4), with the per night plans `workspace/audit/2026-W41/plan_<date>.md` and the tool call traces `workspace/audit/2026-W41/trace_<date>.jsonl`. Outputs: `workspace/payslips/2026-W41.html`, `workspace/boardroom/2026-W41/` (payroll, growth, ruling), `workspace/audit/2026-W41/audit_report.md` and `workspace/approvals/2026-W41/01_instagram_post.md`.
- Make the plan for the night, the tool calls, local file processing, calculation calls and generated outputs visible; conversation alone does not establish an agentic workflow.
- Evidence gates: file format is decided: CSV. The chat scenes need proof 3 (the bot). One real night needs proof 2 and the whole week needs proof 4 (PLAN section 12). Parallel recommendations are unproven until a recorded run shows them.
- Disclose any manual launch or guidance. If the bot is cut, a night started from the command line is shown as that (PLAN section 15). There is no scheduled run: a night starts when the student sends her message. Do not imply parallel recommendations or external message delivery from a manually launched sequential run.
- Sources: PLAN sections 1, 12 and 17; DESIGN sections 6.1 and 6.4.

## Slide 4: Three layers behind one chat

- Criteria: agentic workflow; usable and verifiable results.
- **Bot**: the front door in the chat app. It receives text and files and sends replies and files. It never calls a tool or a model itself (design sections 6.3 and 6.5).
- **Runner**: writes the plan for the night, then runs the four agents in order. Each agent works by asking for tools in a short loop (design sections 6.1 and 6.4).
- **Tools**: the deterministic commands of `tools/lembur.py`. They are the only thing that calculates or writes a figure (design section 4).
- **Agents act through tools**: an agent has no other way to act, so the rule against invented numbers is enforced by the code, not by trust. The Auditor gets no tool that changes the ledger or the plan (design sections 5.1 and 6.4).
- **A written plan each night**: `audit/<week>/plan_<date>.md` records each step, why tonight needs it and its outcome (design sections 6.1 and 7).
- **An Auditor that recomputes**: it reruns the numbers tool without writing and compares the result with the saved `numbers.json` (design section 5.5).
- **Two model roles**: `reason` drives the agents and `read` turns an image into text. Both come from the model gateway the organisers provided. No third party package and no agent framework (design section 6.3; PLAN section 18).
- **No install**: the product is a service and the student only needs a chat app (design section 1).
- **Not a general assistant**: a finished tool with numbers from tested tools, no set up and nothing sent without her approval (PLAN section 3).
- Status: the tool layer, the model module, the runner, the prompts and the Telegram bot are built and merged. The runner replayed the whole demo week with the real models (proof 4). The chat round trip is the one open proof (proof 3).
- Proposed visual: three layers, the chat app on top, the runner in the middle and the tools below, with the four agents inside the runner.
- Source: DESIGN sections 1, 4, 5.5 and 6; PLAN sections 3 and 13.

## Slide 5: Different objectives, independent verification

- Criteria: agentic workflow; usable and verifiable results.
- Bookkeeper: extracts and files evidence, prepares records and resolves unclear matches with reasons.
- Payroll: uses deterministic hours and numbers; prioritises the student's hourly earnings.
- Growth coach: prioritises revenue and sales; proposes changes and prepares drafts after the ruling.
- Auditor: reruns the numbers, checks sources and review coverage, and rules with cited reasons.
- Agents interpret and recommend; deterministic tools calculate. Reconciliation is a tool, not an extra agent.
- Each agent has its own prompt file in `prompts/` (design section 6.4).
- Proposed visual: four named roles with their responsibilities; show actual execution evidence only where available.
- Source: DESIGN sections 4, 5 and 6.4; `submission/identities.md`.

## Slide 6: The reveal: what your time earned

- Criteria: real problem and user value; usable and verifiable results.
- Primary value: “RM 2.53 per hour”.
- Supporting values: “RM 39.50” and “15.6 hours”. Plan target RM12.00 an hour; margin 36 percent against a planned 40.
- Show the payslip filled from `submission/payslip_template.html` (`payslips/<week>.html`); keep its fixed ten section order. It reaches the student as a file in her chat. A PDF is optional and not built (design section 7).
- Explain that hours use assumptions, dated corrections and stated event time, not continuous time tracking.
- Place the unknown-expense caveat next to the headline: earnings are provisional and may be lower when the unreadable expense is confirmed.
- Show Beaded keychain (11 sold, profit −RM10.50, −RM2.80 an hour, `loses_money`) and Beaded bracelet (3 sold, profit RM32.00, RM16.99 an hour) from `numbers.json`. Product direct-hour profit excludes shared time and is not the whole-business hourly rate.
- Take home uses ledger payments; product profit uses plan costs. Product profits do not sum to take home.
- Source: DESIGN sections 4.2, 4.3 and 7; draft answer key “Validation and limitations”.

## Slide 7: Reliability means keeping the uncertainty visible

- Criteria: agentic workflow; usable and verifiable results.
- Compare the recorded run's `workspace/` with `data/answer_key/` (the key is independently verified and awaits Sharon's business sign-off) for the planted problems. In the run: T0004 `duplicate`, T0012 `needs_review` (empty amount), T0019 `needs_review` (document RM5.00, bank RM4.50) and T0020 `unmatched` (bank line, RM9.00):
  - Duplicate receipt: excluded and listed for review.
  - Missing receipt: bank-derived unmatched row, counted when its amount is known, and listed for review.
  - Amount mismatch: bank amount used, both amounts preserved in notes, item reviewed.
  - Blurry receipt: amount stays unknown; document filed and item reviewed.
  - Loss-making bestseller: flagged only when verified product calculations establish the loss.
  - Event time: traces to the saved message.
  - Dated correction: earlier sales retain the earlier assumption; later sales use the corrected value.
- The merged reports validate the prepared fixture. Business sign-off and actual-run comparison are separate gates.
- The pass condition is `python -B data/test_harness/compare_outputs.py` printing PASS with no difference. A mismatch in statuses, minutes or money is a bug to fix before submission, not a presentation caveat to explain away.
- Figures that agents write are checked: every money and hours figure in the recommendations and the ruling must appear in `numbers.json`, or the text is sent back to the agent that wrote it (design section 6.4).
- Source: PLAN sections 10 and 12; DESIGN sections 4.1, 4.2 and 6.4; draft answer key validation and correction sections.

## Slide 8: From competing advice to an accountable decision

- Criteria: real problem and user value; agentic workflow; usable and verifiable results.
- Payroll (`boardroom/2026-W41/payroll.md`): adjust keychain pricing or materials to stop a −RM2.80 an hour loss; focus on the bracelet at RM16.99 an hour; move part of the 10.0 shared hours to productive work. Cited: profit_per_hour_rm, shared_hours, hourly_rate_rm.
- Growth coach (`boardroom/2026-W41/growth.md`): pull back from the keychain (profit −RM10.50); promote the bracelet (profit RM32.00); re-evaluate the RM32.00 Instagram channel cost. Cited: profit_rm, channel_costs_rm.
- Auditor (`boardroom/2026-W41/ruling.md`, `audit/2026-W41/audit_report.md`): all six recommendations upheld, no conflict between them, every cited figure present in `numbers.json`, numbers check passed. The week closes pending the receipt issues, and take home and hourly rate stay provisional because T0012 has no amount.
- Follow `submission/board_meeting_layout.md`; the expected ruling direction in the answer key is not an observed ruling.
- Show the upheld bracelet recommendation linked to its draft `workspace/approvals/2026-W41/01_instagram_post.md`, waiting for individual approval by reply in the chat.
- Do not claim any posting or sending. Lembur posts and sends nothing; the student sends an approved draft herself. Do not claim a projected hourly raise (the design is agreed, not built) or future demand.
- Source: DESIGN sections 5, 6.1, 7 and 8.

## Slide 9: How we used WorkBuddy to build it

- Criteria: meaningful use of WorkBuddy; end-to-end execution.
- Main message: WorkBuddy is our build platform. It is not part of the running product. The organisers relaxed the rule: we show proof that we used it while building, and explain how, where and in what scenarios (PLAN sections 1 and 11).
- **How**: each of us works with WorkBuddy as the builder in our own checkout. We give it the docs as the source of truth, it writes the code or the content, and the result is checked before it is merged.
- **Where and in what scenarios**
  - **Building the engine**: the reconciliation, hours and numbers tools, the command line and the payslip filler, with their tests.
  - **Building the runner and the bot**: the same way. Both are built; say only what the evidence pack shows.
  - **Building the dataset**: the synthetic receipts, orders, bank statement, nightly messages and the answer key, with a second independent calculation that had to agree with the first.
  - **Building the story**: agent identities, the payslip template, this deck outline, the video script and the question and answer sheet.
  - **Running our agents during development**: before the redesign, the four agents were instruction files that WorkBuddy ran as skills. A skill run of our own script passed on 10 October. That is where the agents' instructions were first shaped.
- **Evidence pack**: `submission/evidence/`, with screenshots of our WorkBuddy sessions, task lists and key exchanges, and one line each on what was being built. Items so far: `submission/evidence/workbuddy_session_payslip_template.png` and `submission/evidence/workbuddy_session_story_drafts.png`. Every claim on this slide needs a matching item in it.
- **What we say**: only what WorkBuddy really did. Work done or checked by other means is not presented as WorkBuddy's.
- Proposed visual: session screenshots from the evidence pack beside a short line for each scenario.
- Source: PLAN sections 1, 11 and 12.

## Slide 10: Future only. Stay useful as the business grows

- Criteria: real problem and user value; usable and verifiable results.
- Clearly label this slide “Future only”.
- Solo student: portable books, weekly payslips and decisions.
- First helper: future per-person time records and staffing decisions.
- Accounting or order software adoption: future transfer of books and reading those systems for continued time-and-decision support.
- More ways in: WhatsApp beside Telegram, voice notes and a hosted service. Each is a new channel or a deployment, not a new engine (PLAN section 16; design section 6.5).
- Posting approved drafts through a connector: roadmap only.
- Positioning: work alongside existing tools rather than become an all-in-one platform.
- No built integration, helper workflow, WhatsApp channel, voice notes, hosting or completed migration claim. Present scope permits the `person` field and fixed ledger columns, not these future capabilities.
- Source: PLAN sections 3, 4 and 16.

## Slide 11: Close with the result and its limits

- Criteria: real problem and user value; end-to-end execution; usable and verifiable results.
- Closing line: “Know what your business pays you. Review what to change next.”
- Recap. Input to output: seven nightly messages and their files became a ledger of 20 transactions, 14 bank lines and 20 hours lines, then a payslip of RM2.53 an hour. Validation: `python -B data/test_harness/compare_outputs.py` printed PASS with no difference. Deliverables: `workspace/payslips/2026-W41.html`, `workspace/boardroom/2026-W41/` and `workspace/approvals/2026-W41/01_instagram_post.md`.
- Retain the estimated-hours and unknown-expense limits. Do not imply accuracy beyond the available evidence.
- Practicality: about five minutes for the seven nights (Law, 07:45) and 5m13s in Damian's independent replay (08:10); one night, 2026-10-05, took about 20 seconds (proof 2). Models do not answer identically every time, so say each recorded run was compared again.
- Source: PLAN sections 1, 3, 10 and 12.

## Before final generation

- Damian approves the proposed sequence. The exact judging criterion, “Meaningful use of WorkBuddy”, is already approved.
- Sharon signs off the story and independently checked key.
- Law's recorded proof results (PLAN section 12) determine which intended workflow shots can be shown as implemented.
- Actual outputs match the approved key; review items and earnings caveats remain visible.
- The evidence pack in `submission/evidence/` covers every WorkBuddy claim on slide 9.
- Cuts follow the fixed order in PLAN section 15. Law decides.
- Keep demo inputs separate from the answer key during production runs. Do not give production agents the expected answers.
- Damian reviews the final slides for readability and evidence coverage.
