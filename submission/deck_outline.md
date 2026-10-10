# Submission deck outline

## Draft status

* Content draft for the hackathon submission, not final slides or a product advertisement.
* This draft retains the proposed nine slide sequence. Damian's approval of that sequence, speaking duration and final visual treatment remain pending.
* Source authority: README first, then `docs/PLAN.md`, then `docs/SYSTEM_DESIGN.md`; PLAN governs scope and schedule, SYSTEM_DESIGN governs behaviour and data. Report source conflicts rather than silently resolve them.
* Use the required WorkBuddy generation workflow in PLAN section 1 for the final slides and documentation; these notes supply the content.
* Professional-colleague role titles and warm, student-first direction follow the confirmed design choices.
* Aisyah is the fictional persona in the merged demo dataset. Her story and the independently verified draft answer key still await Sharon's business sign-off.
* Business figures, measured runtime, credit use and actual recommendation/ruling text remain placeholders.
* Replace placeholders only with traceable, approved evidence. Do not call fixture checks a successful application run.
* Source status mismatch: PLAN section 13's 10 October 16:30 list saying the four skills are not built is stale. Four instruction files exist at `skills/*/SKILL.md` in commit `541ef89`; installation and product-agent execution are not proven, and check 5 remains pending.
* The console-encoding and numeric plan-correction fixes in `tools/` are merged. No full agent-run outputs were present in this local `workspace/` during the refresh; this does not establish another teammate's run status. Merged tools and written skills are not end-to-end evidence.
* `submission/payslip_template.html` exists in `dev` through PR 11. Damian approved the sample PDF appearance at 17:23 on 10 October. That is sample appearance/export evidence, not real-run validation; Law's production payslip command and a repeatable Payroll PDF method remain pending.

## Judging criteria: PLAN section 1

* Real problem and user value.
* Agentic workflow.
* Meaningful use of WorkBuddy: WorkBuddy does real execution, not just conversation.
* End-to-end execution.
* Usable and verifiable results.
* Name WorkBuddy wherever the product uses it, following README and PLAN section 1. This wording is approved by Damian.

## Slide 1: What does your side business pay for your time?

* Criteria: real problem and user value.
* Main message: student founders can see orders coming in without knowing what the business earns per hour of their time.
* Supporting points: scattered documents, informal payments, late-night data entry and untracked working time.
* Proposed visual: student context beside a messy-input illustration; use demo material only.
* Evidence slot: `{approved_persona_context}`. Do not invent testimonials, demand validation or user adoption.
* Source: PLAN sections 2 and 3.

## Slide 2: A payslip and a practical next step

* Criteria: real problem and user value; usable and verifiable results.
* Main message: Lembur on WorkBuddy turns business records into a readable weekly payslip and drafts of changes the student can review.
* Show the intended chain: what you took home → time used → earnings per hour → evidence-led decisions → approval-ready drafts.
* Night Shift is the build priority and can read a hand-prepared baseline plan.
* Day Zero is an agreed design in SYSTEM_DESIGN section 8, not a verified capability. The planned `planned_sales` sheet holds `product_id`, `channel` and `units_per_week`; deterministic tools use that planned week for predicted figures.
* Sharon owns Day Zero. Build only when Law authorises it after the midnight checkpoint; until then show the hand-prepared plan, not generated predictions.
* Evidence slots: `{verified_payslip_reference}` and `{verified_draft_references}`.
* Source: PLAN sections 2, 4, 13, 14 and 15; SYSTEM_DESIGN sections 1, 6 and 8.

## Slide 3: One request, a sequence of real work

* Criteria: agentic workflow; end-to-end execution; Meaningful use of WorkBuddy.
* Intended WorkBuddy path: message and authorised inbox → intake → reconciliation → ledger → hours and earnings → recommendations → audit → payslip and drafts.
* Show a continuous recorded run with `{starting_request}`, `{run_reference}` and `{output_references}`.
* Make WorkBuddy task execution, local file processing, calculation calls and generated outputs visible; conversation alone does not establish this criterion.
* Recorded check status: check 6 passed for a temporary diagnostic skill running a deterministic script, not the four product agents; check 7 chose CSV. Sharon owns checks 1, 2, 3, 4, 9 and 10, whose results remain unrecorded; Law owns pending checks 5 and 8; Damian owns check 11, with sample appearance approved but production repeatability and real-output validation pending.
* Show Payroll and Growth coach recommendations as intended at the same time, each independently reading `workspace/audit/<week>/numbers.json` without reading the other's recommendation. Current skill handoff instructions describe sequential roles; actual parallel execution may be claimed only with Law's check 5 evidence.
* Disclose any manual launch or guidance. Do not imply overnight scheduling or external return-message delivery from a manually launched sequential run; Sharon's recorded checks establish those behaviours.
* Sources: PLAN sections 1, 11 and 12; SYSTEM_DESIGN sections 4.3 and 6.1; Payroll and Growth coach skill instructions.

## Slide 4: Different objectives, independent verification

* Criteria: agentic workflow; Meaningful use of WorkBuddy; usable and verifiable results.
* Bookkeeper: extracts and files evidence, prepares records and resolves unclear matches with reasons.
* Payroll: uses deterministic hours and numbers; prioritises the student's hourly earnings.
* Growth coach: prioritises revenue and sales; proposes changes and prepares relevant drafts after the ruling.
* Auditor: reruns the numbers without writing, compares with the saved file, checks sources and review coverage, and rules with cited reasons.
* Agents interpret and recommend; deterministic tools calculate. Reconciliation is a tool, not an extra agent.
* Every numerical recommendation and ruling copies figures only from `workspace/audit/<week>/numbers.json`; agents do not recalculate or invent them.
* Proposed visual: four named WorkBuddy roles with their responsibilities; show actual execution evidence only where available. Written `SKILL.md` files do not prove installation or a team run.
* Source: SYSTEM_DESIGN sections 4 and 5; `submission/identities.md`.

## Slide 5: The reveal: what your time earned

* Criteria: real problem and user value; usable and verifiable results.
* Primary value: “RM {hourly_rate} per hour”.
* Supporting values: “RM {take_home}” and “{total_hours} hours”.
* Show a verified real payslip only after the production renderer fills `submission/payslip_template.html`, not `submission/payslip_layout.md`. Keep the fixed ten-section order; build once after the ruling from the saved numbers, with the Auditor checking final review coverage.
* Until then the approved sample demonstrates appearance only. WorkBuddy PDF conversion must be repeatable by Payroll and verified with populated real output; HTML remains the documented fallback.
* Explain that hours use assumptions, dated corrections and stated event time; not continuous time tracking.
* Place the unknown-expense caveat next to the headline: earnings are provisional and may be lower when the unreadable expense is confirmed.
* Show `{product_name}` and `{product_profit_per_hour}` only from verified outputs. Product direct-hour profit excludes shared time and is not the whole-business hourly rate.
* Take home uses ledger payments; product profit uses plan costs. Product profits do not sum to take home.
* Source: SYSTEM_DESIGN sections 4.2, 4.3 and 7; PLAN check 11; draft answer key “Validation and limitations”.

## Slide 6: Reliability means keeping the uncertainty visible

* Criteria: agentic workflow; usable and verifiable results.
* Compare `{actual_run_output}` with `{approved_answer_key_reference}` for the planted problems:
  * Duplicate receipt: excluded and listed for review.
  * Missing receipt: bank-derived unmatched row, counted when its amount is known, and listed for review.
  * Amount mismatch: bank amount used, both amounts preserved in notes, item reviewed.
  * Blurry receipt: amount stays unknown; document filed and item reviewed.
  * Loss-making bestseller: flagged only when verified product calculations establish the loss.
  * Event time: traces to the saved message.
  * Dated correction: earlier sales retain the earlier assumption; later sales use the corrected value.
* Final review includes every transaction row with status `unmatched`, `duplicate` or `needs_review`, plus every line of `workspace/audit/<week>/review_items.md`. The Auditor verifies both sources reach the rendered payslip.
* The merged reports validate the prepared fixture. Business sign-off and actual-run comparison are separate gates.
* A mismatch in statuses, minutes or money is a bug to fix before submission, not a presentation caveat to explain away.
* Source: PLAN section 10; SYSTEM_DESIGN sections 4.1, 4.2, 5.5 and 7; draft answer key validation and correction sections.

## Slide 7: From competing advice to an accountable decision

* Criteria: real problem and user value; agentic workflow; usable and verifiable results.
* Show `{payroll_recommendation}` versus `{growth_recommendation}`, with current figures copied only from `workspace/audit/<week>/numbers.json` and cited source references.
* Show `{actual_auditor_ruling}` and `{ruling_reason_with_citations}` beneath the arguments.
* Follow `submission/board_meeting_layout.md`; the expected ruling direction in the answer key is not an observed ruling.
* Keep `{draft_reference}` for a verified upheld action that requires a post or supplier message, waiting for individual approval. Do not invent a draft for an action that needs none.
* Mapping gate for Law: the Growth coach skill allows upheld actions needing no draft, while SYSTEM_DESIGN section 7 says each upheld recommendation points to a draft and defines `raise_plan` with `draft_file`. Clarify this source mismatch before populating the raise plan or its draft links.
* “approve N” moves only numbered draft N from `workspace/approvals/<week>/` to `workspace/approvals/<week>/approved/`. “skip N” leaves it pending, not rejected. The system never posts or sends drafts, even after approval; the student sends an approved draft herself.
* Price-only projection design is agreed in SYSTEM_DESIGN section 8: replay one product's new price with the same units sold and the same week minutes. Build only on Law's word after the first full run. Existing skills prohibit projections until updated and tested; until then cite current figures only, with no projected raise or future-demand claim.
* Source: SYSTEM_DESIGN sections 5, 6.1, 7 and 8; PLAN sections 4 and 18; `skills/growth_coach/SKILL.md`.

## Slide 8: Future only: stay useful as the business grows

* Criteria: real problem and user value; usable and verifiable results.
* Clearly label this slide “Future only”.
* Solo student: portable books, weekly payslips and decisions.
* First helper: future per-person time records and staffing decisions.
* Accounting or order software adoption: future transfer of books and reading those systems for continued time-and-decision support.
* Positioning: work alongside existing tools rather than become an all-in-one platform.
* No built integration, helper workflow or completed migration claim. Present scope permits the `person` field and fixed ledger columns, not these future capabilities.
* Source: PLAN sections 3, 4 and 16.

## Slide 9: Close with the result and its limits

* Criteria: real problem and user value; end-to-end execution; usable and verifiable results.
* Closing line: “Know what your business pays you. Review what to change next.”
* Recap `{verified_input_to_output_result}`, `{verified_validation_result}` and `{usable_deliverable_references}`.
* Retain the estimated-hours and unknown-expense limits. Do not imply accuracy beyond the available evidence.
* Practicality slots: `{measured_run_duration}` and `{measured_run_credit_usage}`; both remain unknown and may be populated only from Law's actual runs, including check 8 credit evidence. Sample PDF export timing is not full-run timing.
* Source: PLAN sections 1, 3, 10 and 12.

## Before final generation

* Damian approves the proposed sequence. The exact judging criterion, “Meaningful use of WorkBuddy”, is already approved.
* Sharon signs off the story and independently checked key.
* Recorded evidence controls workflow shots: check 6 skill-script execution passed and check 7 selected CSV; Sharon records checks 1, 2, 3, 4, 9 and 10; Law records checks 5 and 8; Damian's check 11 sample appearance is approved, while Law's production renderer, repeatable Payroll PDF conversion and populated-output validation remain pending.
* Actual outputs match the approved key; review includes all three transaction statuses and every `review_items.md` line, with earnings caveats visible. Keep actual dialogue, recommendations, rulings and business figures as placeholders until verified.
* PLAN section 15's cut order is approved and fixed, not an open decision: Day Zero generation → Telegram trigger → scheduled overnight run → open debate. If the midnight checkpoint is missed, apply that order with the documented hand-prepared plan, in-WorkBuddy launch, manual run and single-ruling fallbacks; disclose what was cut.
* Never cut the ledger, reconciliation flags, payslip with hourly rate, raise plan or Auditor check against the answer key. Law's authorisation to build Day Zero after midnight and the price-only projection after the first full run is separate from the approved cut order.
* Law clarifies the upheld-action-to-draft mapping before populating the raise plan. No invented drafts, projections or installation/execution claims.
* Keep demo inputs separate from the answer key during production runs. Do not give production agents the expected answers.
* Final slides use the required WorkBuddy generation workflow, then Damian reviews readability and evidence coverage. This refresh is content only; final generation and measured speaking duration remain pending.
