# Board meeting layout notes

## Status

* Format-neutral presentation notes based on the provisionally approved wireframe, not a final presentation template or evidence of a completed debate.
* Warm, student-first presentation with professional-colleague role titles.
* All recommendations, figures, source references and ruling text remain named placeholders.
* Exact board styling and page or slide breaks still await Damian's review. The payslip template format is settled in SYSTEM_DESIGN section 7; its sample PDF look was approved at 17:23 on 10 October. This is not approval of a final board presentation or proof of a real run.
* The four role instruction files exist in `skills/`; their installation, visible collaboration and actual execution still require check 5 and a verified run. PLAN section 13's 16:30 “not built yet” snapshot predates those files.
* Individual approval by reply and no system posting are settled design rules. Actual file move and confirmation evidence remain pending.
* Intended recommendations are prepared independently from the same saved numbers file. Do not claim they ran simultaneously until Law's check 5 and the run recording prove it.

## Approved structure

* Introduce the reporting week and the disagreement topic.
* Give Payroll and Growth coach equal space above the Auditor, with matching internal structure.
* Identify each speaker by name and objective; never rely on colour alone.
* Place the Auditor in a separate full-width section beneath the arguments. It is independent authority, not a third contestant or a vote.
* Show the upheld action and its draft reference after the ruling.
* Repeat this structure for each actual disagreement. Allow long evidence or reasons to continue without truncating them.
* If the confirmed output format cannot support paired arguments, preserve the reading order and equal emphasis in a stacked layout; confirm the adaptation with Damian before treating it as final.

## Week and disagreement

* Context: `{week}` · `{date_range}`.
* Topic: `{disagreement_topic}`.
* Present one actual disagreement at a time; do not manufacture conflict for the story.

## Payroll: hourly earnings

* Role heading: “Payroll”.
* Objective label: “What pays you better per hour?”
* Proposed change: `{payroll_recommendation}`.
* Current evidence: `{payroll_cited_figures}`.
* Sources: `{payroll_source_references}`.
* Use the actual `boardroom/{week}/payroll.md` recommendation. Every proposed change must cite the figures it rests on.
* Keep the student's hourly earnings as the objective; do not promise an improvement that has not been calculated under approved rules.

## Growth coach: revenue and sales

* Role heading: “Growth coach”.
* Objective label: “What grows revenue and sales?”
* Proposed change: `{growth_recommendation}`.
* Current evidence: `{growth_cited_figures}`.
* Sources: `{growth_source_references}`.
* Use the actual `boardroom/{week}/growth.md` recommendation. Its structure and visual weight match Payroll's.
* The objective differs from Payroll's; popularity alone is not evidence that expanding a product is worthwhile.
* Do not invent forecasts, demand claims or projected gains.

## Auditor: evidence, decision and reason

* Role heading: “Auditor”.
* Evidence checked: `{verified_figures_and_sources}`.
* Decision: `{upheld_side_and_change}`.
* Reason: `{ruling_reason_with_citations}`.
* Unsupported arguments or outstanding evidence: `{rejected_argument_or_review_item}` where present in actual outputs.
* Populate the ruling from `boardroom/{week}/ruling.md`, with checks from `audit/{week}/audit_report.md`.
* Show actual pass or fail findings and relevant references; do not prefill a success label.
* The Auditor reruns the numbers, checks review coverage and traces hours to their sources. Do not imply it independently measured the student's time or guaranteed that every document was read correctly.
* Preserve the distinction between ledger-based take home and plan-cost product profit; product direct hourly rates exclude shared event and admin time.
* Where an expense amount is unknown, state: “Known-amount earnings are provisional; an expense still needs confirmation.”
* An expected Auditor direction from the answer key is a test expectation, not an actual ruling. Keep decision and reason placeholders until the ruling exists.

## Upheld actions and draft review

* After the actual ruling, repeat one group per upheld recommendation:
  * Upheld action: `{upheld_recommendation}`, referencing the actual speaker and recommendation number.
  * Draft: `{draft_reference}` in `workspace/approvals/{week}/`, only where a real numbered draft exists.
  * State before a reply: “Waiting for individual approval”. Do not fabricate a draft or a completed approval.
* Growth coach instructions specify that some upheld changes need no customer or supplier message, while SYSTEM_DESIGN section 7 expects draft references for raise recommendations. Ask Law to confirm the mapping before populating that case; do not add a schema field or invent a message.
* The student replies “approve N” or “skip N” for one numbered draft. Approval moves it into `workspace/approvals/{week}/approved/` and the agent confirms. Skipping leaves it pending in its original folder, not rejected or deleted.
* The system never posts or sends drafts, even after approval. The student sends an approved draft herself. Do not depict a system send, approval button or blanket approval.
* Show `{verified_approval_reply}`, `{approved_draft_path}` and `{agent_confirmation}` only after the actual interaction. These are presentation slots, not extra renderer fields.
* The price only projection design is agreed in SYSTEM_DESIGN section 8, with the same units sold and week minutes. Implementation requires Law's authorisation after the first full run. Current skills accept no projections; cite current `numbers.json` figures only.

## Relationship to the payslip

* The expanded meeting provides the evidence behind the short debate-and-ruling summary in payslip section 8.
* Upheld actions must match payslip section 9 and point to the same drafts.
* Review items must remain consistent with payslip section 10: all transactions with `unmatched`, `duplicate` or `needs_review` status and every line of `workspace/audit/{week}/review_items.md`, including hours and numbers warnings. Do not hide uncertainty in a separate presentation.
* Source notes are for traceability, not authoring attribution.

## Handoff checks

* Both actual recommendation files exist. Every numerical argument copies `workspace/audit/{week}/numbers.json` display values, naming their keys; ledger rows and plan references supply context, not alternative numerical dialogue.
* The actual Auditor report and ruling exist; failures, unknown amounts and rejected arguments are not omitted.
* Run outputs match Sharon's approved, independently checked answer key before any claim of validated execution.
* Placeholder names are display slots, not new data-model fields or a new workflow.
* No invented dialogue, financial figures, forecasts, built-feature claims or private data.
* Final board format and visual adaptation are confirmed separately. The HTML payslip contract is already settled; Law's production renderer integration, repeatable PDF conversion and actual output validation remain pending.

## Sources

* Positioning and honest limits: `docs/PLAN.md`, sections 2 and 3.
* Validation: `docs/PLAN.md`, section 10.
* Financial bases and time sources: `docs/SYSTEM_DESIGN.md`, sections 4.2 and 4.3.
* Conflicting objectives and Auditor duties: `docs/SYSTEM_DESIGN.md`, sections 5.3 to 5.5.
* Recommendations, ruling, drafts and individual approval: `docs/SYSTEM_DESIGN.md`, sections 6.1 and 7.
* Agreed but build gated projection design: `docs/SYSTEM_DESIGN.md`, section 8. Current skill instructions still prohibit projected claims.
* Unknown expense and fixture-only validation: `data/answer_key/answer_key.md`, “Validation and limitations”. The draft key does not supply an observed ruling.
* Visual structure: Damian's provisional approval of equal arguments above a separate Auditor ruling.
