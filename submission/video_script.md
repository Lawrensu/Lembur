# Project submission video script

## Draft status and production rules

* Text only script and shot list for the hackathon submission, not a product advertisement or a generated video.
* Authorities: `README.md`, `docs/PLAN.md` and `docs/SYSTEM_DESIGN.md`. SYSTEM_DESIGN wins on behaviour and data; PLAN wins on scope and schedule. Layout notes and written skills do not override them.
* Name WorkBuddy wherever the product uses it, following README and Damian's approved naming decision. Platform naming does not establish execution evidence.
* Proposed narration and capture instructions in the preserved seven scene order. Damian owns the final narration, scene treatment, visual look, recording and editing.
* Total length: `{submission_video_duration}`. Obtain the organisers' limit and Damian's approval before fixing scene timings.
* All scene durations below are placeholders. PLAN section 17 suggests about thirty seconds for Day Zero; this is guidance, not the confirmed submission time limit.
* Aisyah is the fictional student in the merged dataset, subject to Sharon's story sign-off. Use `{approved_persona_name}` in narration until then.
* Every business figure, recommendation, ruling and runtime claim stays a named placeholder until supported by verified outputs. Source references and output paths must resolve to the recorded run, not sample content.
* Narration that describes successful execution is usable only after its scene's evidence gate passes. A scripted claim is not execution evidence or a guarantee.
* `skills/README.md` and the Bookkeeper, Payroll, Growth coach and Auditor instruction files exist in the repository. No recorded installation or product agent run evidence is established here; Law's check 5 remains pending.
* PLAN section 13's 10 October 16:30 snapshot still says the four skills are not built. Distinguish later written files from installed skills and verified execution; leave PLAN unchanged.
* `submission/payslip_template.html` is in `dev` through PR 11. Damian approved the sample PDF look at 17:23 on 10 October. The production renderer, repeatable Payroll PDF method and populated real output pagination and review coverage remain pending.
* Demo data only. Keep the expected ledger and answer key out of the production agents' inputs.

## Scene 1: Week zero, a starting plan

* Duration: `{day_zero_scene_duration}`.
* Purpose: introduce the idea and a plan that the later payslip can test.
* Shot: `{approved_persona_name}` enters `{business_idea_message}`; show costing, pricing assumptions, time assumptions and Auditor checks only if implemented and verified.
* Proposed narration: “Before starting, I want to know what this business could earn and how much of my time it would take.”
* Output shot: `{verified_plan_summary_reference}` and `{verified_plan_file_reference}`.
* Predicted-rate slot, only for verified Day Zero generation: “RM {predicted_hourly_rate} per hour”, explicitly labelled as a prediction based on assumptions.
* Proposed narration: “This is my starting plan. The time estimates are assumptions; the weekly payslip will test them against reality.”
* Evidence gate: Day Zero's design is agreed, including `planned_sales` expected volumes (`product_id`, `channel`, `units_per_week`) and deterministic planned-week calculations. Sharon owns Day Zero; it is not built until Law authorises it after the midnight checkpoint. Show generated predictions only after implementation and verification. Break even is optional, not a mandatory output or recording gate.
* If generation is unavailable, use the approved hand prepared baseline as “the plan”, following PLAN section 15's fixed cut order. This is an approved fallback, not a proposed cut or generated prediction. Damian owns its final scene treatment.
* Sources: PLAN sections 3, 4, 13, 15 and 17; SYSTEM_DESIGN sections 1, 6.2 and 8.

## Scene 2: The narrative time jump

* Duration: `{time_jump_duration}`.
* Title card: “Four weeks later…”
* Keep the same student character.
* This is the documented story framing, not a claim of weeks of real deployment. The fixture is one prepared Monday to Sunday week.
* Sources: PLAN sections 10 and 17; `data/demo/messages.md`.

## Scene 3: Before bed, message and messy documents

* Duration: `{bedtime_scene_duration}`.
* Shot: `{verified_nightly_message}` and its dated demo inbox batch.
* Proposed narration: “The orders and receipts are scattered. Before bed, I send one message and leave the documents together.”
* Show actual synthetic receipts, order screenshots and the bank statement only on their documented intake dates.
* The bank statement arrives on Sunday; do not depict it arriving before its batch. Cash orders in the message are individual orders, not extra screenshots.
* Evidence gates: Sharon owns check 1 for a Telegram text trigger, check 2 for the wanted voice note, and check 10 for attachments reaching `workspace/inbox/`. These remain pending until their results are recorded; Law does not own all platform checks.
* Do not portray voice input or Telegram attachment intake as working without its own evidence. The voice fallback is typed text or documented keyboard dictation; the attachment fallback is files dropped into the folder.
* If the trigger is unavailable, follow PLAN section 15's fixed fallback: start inside WorkBuddy and show the message separately. Label the manual launch honestly; Damian owns the final treatment.
* Sources: PLAN sections 4, 12, 15 and 17; SYSTEM_DESIGN section 6.1; `data/demo/messages.md` replay instructions.

## Scene 4: The Night Shift

* Duration: `{night_shift_scene_duration}`.
* Shot sequence, only from a continuous actual run whose evidence gates pass:
  * Starting request and authorised inbox.
  * Bookkeeper intake and filed source links.
  * Reconciliation statuses and explanations for unclear matches.
  * Ledger rows with their evidence references.
  * Payroll hours and deterministic numbers saved to `workspace/audit/<week>/numbers.json`.
  * Payroll and Growth coach recommendations in `workspace/boardroom/<week>/payroll.md` and `workspace/boardroom/<week>/growth.md`, with cited figures copied only from that same saved numbers file.
  * Auditor's read only numbers comparison and checks in `workspace/audit/<week>/audit_report.md`, then its actual ruling in `workspace/boardroom/<week>/ruling.md`.
  * Payslip generated once after the ruling, the Auditor's final review coverage confirmation, then numbered unsent drafts in `workspace/approvals/<week>/`.
* Proposed narration: “In WorkBuddy, the agents read and review. Deterministic tools do the matching and calculations. Uncertainty is flagged, not guessed.”
* Include actual evidence of the duplicate, missing receipt, mismatch and unreadable amount; do not prefill pass labels.
* Review shot: show every transaction row with status `unmatched`, `duplicate` or `needs_review`, plus EVERY line of `workspace/audit/<week>/review_items.md` when present. Keep row IDs, reasons, known or unknown amounts and actual source references readable; never invent a receipt link for a bank-only row.
* Capture `{verified_correction_history}`: the correction is applied once, effective from its recorded date, with earlier sales retaining the earlier assumption.
* Evidence gates: check 6 established that a diagnostic skill can run deterministic scripts; check 7 decided CSV. Neither establishes a product agent run. Sharon's check 4 for receipt OCR accuracy and Law's check 5 for installed custom skills and a visible team run remain pending.
* Recommendations are intended to run in parallel, independently reading the same `numbers.json` without reading each other's recommendation. Written skill handoff wording also describes sequential roles. Law must resolve the runtime treatment through check 5; do not claim simultaneous execution without a recording. Sequential execution is the documented fallback.
* Verify saved correction history, ledger statuses, hours sources and copied numbers against Sharon's approved key, not only the final total. Recorded tool checks are not proof of the complete agent workflow.
* Label any edited acceleration “Time-lapse”. Do not claim a speed-up factor, runtime, parallel execution or unattended scheduling without evidence.
* Sources: PLAN sections 10, 12, 13 and 14; SYSTEM_DESIGN sections 4 to 6; `skills/README.md`; `skills/payroll/SKILL.md`; `skills/growth_coach/SKILL.md`; `skills/auditor/SKILL.md`; `data/demo/messages.md`.

## Scene 5: Morning, the board meeting is ready

* Duration: `{morning_scene_duration}`.
* Story beat: the last reply of the run is the morning message, “Your board meeting is ready”. It includes “RM {hourly_rate} per hour”, copied from `workspace/audit/<week>/numbers.json`, the named verified payslip path `workspace/payslips/<week>.html` or an evidenced `workspace/payslips/<week>.pdf`, and each numbered draft's actual file and description awaiting “approve N”.
* Show only drafts and paths that the run produced. Preserve any actual upheld action requiring no draft; do not invent one to fill the list.
* PLAN section 17 specifies 7am as the morning story cue; it is narrative timing, not proof of delivery at that time.
* Proposed narration, only when evidenced: “By morning, the result is ready to review.”
* Evidence gates: a last-run reply returned inside WorkBuddy does not establish scheduled execution or Telegram delivery. Sharon's check 3 for unattended scheduling and check 9 for Telegram morning-message delivery are separate pending gates. File delivery needs its own check 9 evidence as well.
* Recorded check 6 proves script invocation, not unattended scheduling. Do not portray a manually launched run as an unattended overnight task.
* If unavailable, use the fixed manual-run fallback and the documented WorkBuddy result-view fallback, with honest labels and Damian's final treatment. Never turn an in-app result into a fictional Telegram arrival.
* Sources: PLAN sections 12, 15 and 17; SYSTEM_DESIGN section 6.1; `skills/README.md`.

## Scene 6: The payslip reveal and the decision

* Duration: `{payslip_and_meeting_scene_duration}`.
* Shot: the verified payslip generated from `submission/payslip_template.html`, using SYSTEM_DESIGN section 7's fixed top to bottom order. `submission/payslip_layout.md` is a hierarchy reference, not the production handoff.
* Sample boundary: the template exists in `dev` through PR 11 and its sample PDF look was approved at 17:23. A sample is not a populated actual payslip or proof that Payroll can repeat its PDF export.
* Headline: “RM {hourly_rate} per hour”. Supporting values: “RM {take_home}” and “{total_hours} hours”. Copy calculated display values only from `workspace/audit/<week>/numbers.json`.
* Proposed narration: “This is what my business paid for my time, not just what came in.”
* Visible caveat when the actual review list contains an unknown expense: “Provisional earnings: an expense amount is unknown.” Never substitute zero for that amount.
* Proposed narration, only with that evidence: “An unreadable expense is still missing, so these earnings may be lower when it is confirmed. The hours use assumptions, corrections and stated event time, not a complete timesheet.”
* Product shot: `{verified_product_results}` with a loss marker only where the tool establishes a loss.
* Explain through caption or narration: product profit uses plan costs and direct production/fulfilment time; take home uses ledger payments and the whole week's time. Product profits do not add up to take home.
* Plan-comparison shot: `{target_hourly_rate}` against `{hourly_rate}`, and `{planned_margin_percent}` against `{actual_margin_percent}`. Do not relabel the target as a generated prediction; omit an actual margin unsupported by the run.
* Debate shot, using `submission/board_meeting_layout.md` as a visual reference and actual run files as evidence:
  * Payroll: `{actual_payroll_recommendation}` with `{payroll_cited_evidence}`, from `workspace/boardroom/<week>/payroll.md`.
  * Growth coach: `{actual_growth_recommendation}` with `{growth_cited_evidence}`, from `workspace/boardroom/<week>/growth.md`.
  * Auditor: `{actual_ruling}` and `{ruling_reason_with_citations}`, from `workspace/boardroom/<week>/ruling.md`, with checks from `workspace/audit/<week>/audit_report.md`.
* Leave agent dialogue and ruling unfilled until verified actual output files exist. Written skill instructions and the answer key's expected ruling direction are not an actual exchange or ruling.
* Proposed narration: “One colleague argues for hourly earnings, another for revenue and sales. The Auditor checks the evidence and rules.”
* Raise-plan shot: `{upheld_recommendation}` linked to `{draft_reference}`, followed by every `unmatched`, `duplicate` and `needs_review` transaction row and EVERY line of `workspace/audit/<week>/review_items.md`. Draft only where the actual upheld action needs communication.
* Evidence gate: actual ledger statuses, amounts, minutes, source labels, review items and product results must match Sharon's approved key. Ruling direction must be checked, not copied into the run. Law must confirm production renderer integration and a repeatable Payroll PDF method; verify populated ruling, drafts, full review coverage and pagination on the recorded output. HTML remains the fallback.
* The projection design is agreed, not unconfirmed: a price-only replay uses the same units sold and the same week minutes. Law authorises building it only after the first full run; then deterministic outputs, assumption labels and Auditor verification are required. Current written skills prohibit projected claims and cite current figures only. Do not promise a precise raise or future demand.
* Sources: PLAN sections 3, 4, 10, 12, 13 and 17; SYSTEM_DESIGN sections 4.2, 4.3, 5, 7 and 8; `submission/payslip_layout.md`; `skills/payroll/SKILL.md`; `skills/growth_coach/SKILL.md`; `skills/auditor/SKILL.md`; draft answer key limitations.

## Scene 7: Individual approval, then class

* Duration: `{approval_and_close_scene_duration}`.
* Shot: `{verified_individual_approval_evidence}` for each draft shown. Show the student's “approve N” reply, the actual move of that numbered file from `workspace/approvals/<week>/` to `workspace/approvals/<week>/approved/`, and the agent's confirmation that it is ready for her to send. End at verified approval, then show the student going to class.
* Proposed narration: “I reply approve N for each draft. The approved draft is ready for me to send; WorkBuddy does not post or send it.”
* Do not use one blanket approval for all drafts. The agreed interaction is a reply typed inside WorkBuddy or via evidenced Telegram, not an approval command, button or tap. Do not add an unsupported control.
* If “skip N” is shown, that draft stays pending in `workspace/approvals/<week>/` and the agent confirms it was left there. It is not rejected or moved.
* NEVER show the system posting or sending a draft in this version, even after approval. Do not show a sending sequence; this story ends at approval and class.
* Closing line: “Kau tidur, kami lembur. You sleep, we do the overtime.”
* Evidence gate: Law confirms the supported reply and file-move behaviour with actual evidence; written instructions alone do not prove it worked. Damian owns and approves the final closing scene treatment.
* Sources: PLAN sections 2, 4, 11, 17 and 18; SYSTEM_DESIGN sections 5.1 and 6.1; `skills/growth_coach/SKILL.md`.

## Recording handoff

* Confirm organiser requirements, total duration and all scene timings with Damian; leave the placeholders unchanged until approved.
* Obtain Sharon's persona and business sign-off, then Law/Sharon's real-run comparison with the key.
* Clear each scene's implementation gate before speaking its success narration. Agreed designs, written files, approved sample appearance and verified runtime behaviour are distinct states.
* Retain original full-run recordings and backup copies; use recorded evidence rather than a live demo.
* Never invent an agent exchange, missing receipt, correction history, successful delivery, simultaneous execution or approval file move for a shot.
* Keep limitations and the complete review list readable in the edit, including every review-status transaction, every `review_items.md` line and any unknown-expense caveat.
* Label time-lapse edits and disclose any manual launch or fallback. Checks 1, 3 and 9 remain independent of local script execution and an in-app reply.
* PLAN section 15's cut order is fixed, not a proposal: Day Zero generation → Telegram trigger → scheduled overnight run → open debate. Use the hand prepared baseline, an in-app launch, a manual run and a single Auditor ruling as the respective approved fallbacks. Never cut the ledger, reconciliation flags, hourly-rate payslip, raise plan or Auditor check against the key.
* Law must settle sequential handoff versus intended parallel recommendations and confirm production renderer integration, repeatable Payroll PDF conversion and real-run populated pagination. Do not change PLAN's historical snapshot or infer that pending work has passed.
* Clarify with Law how to represent an upheld recommendation needing no customer or supplier draft: Growth coach instructions allow no draft, but SYSTEM_DESIGN section 7 expects a draft reference. Do not fabricate a draft or a new field to fill that gap.
* These notes provide a written script and capture plan only. No video generation, system sending or extra interaction is part of this version; final scene treatment, recording and editing remain with Damian.
