# Submission deck outline

## Draft status

- Content draft for the hackathon submission, not final slides or a product advertisement.
- Proposed slide sequence; slide count, speaking duration and final visual treatment await Damian's review.
- These notes supply the content for the final slides and documentation. If WorkBuddy is used to make them, capture the session for the evidence pack (PLAN section 11).
- The story: Lembur is a back office team in the student's chat app. She installs nothing. WorkBuddy is the platform we built it with, not part of the running product (PLAN section 11).
- Professional-colleague role titles and warm, student-first direction follow the confirmed design choices.
- Aisyah is the fictional persona in the merged demo dataset. Her story and the independently verified draft answer key still await Sharon's business sign-off.
- Built and merged into `dev`: the deterministic tools, the command line, the payslip command and template, the dataset, the answer key, the comparator, the tool layer (`app/tools.py`) and the Telegram bot (`app/bot.py`), each with its tests. Not built yet: the model module (`app/model.py`), the runner (`app/runner.py`) and the prompts (`prompts/`). Show nothing as running until its proof in PLAN section 12 is recorded.
- Until a real run exists, use the figures in data/answer_key/answer_key.md and label each one as a sample. Never invent a figure. Measured runtime and actual recommendation and ruling text remain placeholders.
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
- Evidence slots: `{verified_payslip_reference}` and `{verified_draft_references}`.
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
- Show a continuous recorded run with `{starting_request}`, `{run_reference}` and `{output_references}`.
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
- Status: the tool layer and the Telegram bot are built and merged; the model module, the runner and the prompts are designs, not built yet (PLAN section 13). Draw the unbuilt parts as the plan until their proofs are recorded.
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
- Primary value: “RM {hourly_rate} per hour”.
- Supporting values: “RM {take_home}” and “{total_hours} hours”.
- Show the payslip filled from `submission/payslip_template.html` (`payslips/<week>.html`); keep its fixed ten section order. It reaches the student as a file in her chat. A PDF is optional and not built (design section 7).
- Explain that hours use assumptions, dated corrections and stated event time, not continuous time tracking.
- Place the unknown-expense caveat next to the headline: earnings are provisional and may be lower when the unreadable expense is confirmed.
- Show `{product_name}` and `{product_profit_per_hour}` only from verified outputs. Product direct-hour profit excludes shared time and is not the whole-business hourly rate.
- Take home uses ledger payments; product profit uses plan costs. Product profits do not sum to take home.
- Source: DESIGN sections 4.2, 4.3 and 7; draft answer key “Validation and limitations”.

## Slide 7: Reliability means keeping the uncertainty visible

- Criteria: agentic workflow; usable and verifiable results.
- Compare `{actual_run_output}` with `{approved_answer_key_reference}` for the planted problems:
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
- Show `{payroll_recommendation}` versus `{growth_recommendation}`, with current cited figures and source references.
- Show `{actual_auditor_ruling}` and `{ruling_reason_with_citations}` beneath the arguments.
- Follow `submission/board_meeting_layout.md`; the expected ruling direction in the answer key is not an observed ruling.
- Show the upheld action linked to `{draft_reference}`, waiting for individual approval by reply in the chat.
- Do not claim any posting or sending. Lembur posts and sends nothing; the student sends an approved draft herself. Do not claim a projected hourly raise (the design is agreed, not built) or future demand.
- Source: DESIGN sections 5, 6.1, 7 and 8.

## Slide 9: How we used WorkBuddy to build it

- Criteria: meaningful use of WorkBuddy; end-to-end execution.
- Main message: WorkBuddy is our build platform. It is not part of the running product. The organisers relaxed the rule: we show proof that we used it while building, and explain how, where and in what scenarios (PLAN sections 1 and 11).
- **How**: each of us works with WorkBuddy as the builder in our own checkout. We give it the docs as the source of truth, it writes the code or the content, and the result is checked before it is merged.
- **Where and in what scenarios**
  - **Building the engine**: the reconciliation, hours and numbers tools, the command line and the payslip filler, with their tests.
  - **Building the runner and the bot**: the same way. Say so only once they are built.
  - **Building the dataset**: the synthetic receipts, orders, bank statement, nightly messages and the answer key, with a second independent calculation that had to agree with the first.
  - **Building the story**: agent identities, the payslip template, this deck outline, the video script and the question and answer sheet.
  - **Running our agents during development**: before the redesign, the four agents were instruction files that WorkBuddy ran as skills. A skill run of our own script passed on 10 October. That is where the agents' instructions were first shaped.
- **Evidence pack**: `submission/evidence/`, with screenshots of our WorkBuddy sessions, task lists and key exchanges, and one line each on what was being built. Slot: `{evidence_pack_references}`. Every claim on this slide needs a matching item in it.
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
- Recap `{verified_input_to_output_result}`, `{verified_validation_result}` and `{usable_deliverable_references}`.
- Retain the estimated-hours and unknown-expense limits. Do not imply accuracy beyond the available evidence.
- Practicality slot: `{measured_run_duration}`; populate only from Law's actual runs.
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
