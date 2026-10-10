# Project submission video script

## Draft status and production rules

- Text-only script and shot list for the hackathon submission, not a product advertisement or a generated video.
- Name WorkBuddy wherever the product uses it, following README and Damian's approved naming decision. Platform naming does not establish execution evidence.
- Proposed narration, scene order and capture instructions. Damian owns the final narration, visual look, recording and editing.
- Total length: `{submission_video_duration}`. Obtain the organisers' limit and Damian's approval before fixing scene timings.
- All scene durations below are placeholders. PLAN section 17 suggests about thirty seconds for Day Zero; this is guidance, not the confirmed submission time limit.
- Aisyah is the fictional student in the merged dataset, subject to Sharon's story sign-off. Use `{approved_persona_name}` in narration until then.
- Every business figure, recommendation, ruling and runtime claim stays a named placeholder until supported by verified outputs.
- Narration that describes successful execution is usable only after its scene's evidence gate passes. A scripted claim is not execution evidence.
- Demo data only. Keep the expected ledger and answer key out of the production agents' inputs.

## Scene 1 — Week zero: a starting plan

- Duration: `{day_zero_scene_duration}`.
- Purpose: introduce the idea and a plan that the later payslip can test.
- Shot: `{approved_persona_name}` enters `{business_idea_message}`; show costing, pricing assumptions, time assumptions and Auditor checks only if implemented and verified.
- Proposed narration: “Before starting, I want to know what this business could earn—and how much of my time it would take.”
- Output shot: `{verified_plan_summary_reference}` and `{verified_plan_file_reference}`.
- Predicted-rate slot: “RM {predicted_hourly_rate} per hour”, explicitly labelled as a prediction based on assumptions.
- Proposed narration: “This is my starting plan. The time estimates are assumptions; the weekly payslip will test them against reality.”
- Evidence gate: Day Zero formulas, expected-volume inputs and ownership remain unconfirmed in the source docs. Do not show generated predictions or a break-even result until agreed and tested.
- If generation is unavailable, ask Damian to approve an honestly labelled hand-prepared-plan treatment. The proposed cut order is not permission to silently substitute it.
- Sources: PLAN sections 3, 4, 15 and 17; DESIGN sections 1, 6.2 and 8.

## Scene 2 — The narrative time jump

- Duration: `{time_jump_duration}`.
- Title card: “Four weeks later…”
- Keep the same student character.
- This is the documented story framing, not a claim of weeks of real deployment. The fixture is one prepared Monday-to-Sunday week.
- Sources: PLAN sections 10 and 17; `data/demo/messages.md`.

## Scene 3 — Before bed: message and messy documents

- Duration: `{bedtime_scene_duration}`.
- Shot: `{verified_nightly_message}` and its dated demo inbox batch.
- Proposed narration: “The orders and receipts are scattered. Before bed, I send one message and leave the documents together.”
- Show actual synthetic receipts, order screenshots and the bank statement only on their documented intake dates.
- The bank statement arrives on Sunday; do not depict it arriving before its batch. Cash orders in the message are individual orders, not extra screenshots.
- Evidence gate: external text-trigger success must be confirmed by Law. If the run starts manually, obtain approval for that treatment and label it honestly.
- Sources: PLAN sections 12 and 17; DESIGN section 6.1; `data/demo/messages.md` replay instructions.

## Scene 4 — The Night Shift

- Duration: `{night_shift_scene_duration}`.
- Shot sequence from a continuous actual run:
  - Starting request and authorised inbox.
  - Bookkeeper intake and filed source links.
  - Reconciliation statuses and explanations for unclear matches.
  - Ledger rows with their evidence references.
  - Payroll hours and deterministic numbers outputs.
  - Payslip-day recommendations, Auditor report and ruling.
  - Generated payslip and unsent drafts.
- Proposed narration: “In WorkBuddy, the agents read and review. Deterministic tools do the matching and calculations. Uncertainty is flagged, not guessed.”
- Include actual evidence of the duplicate, missing receipt, mismatch and unreadable amount; do not prefill pass labels.
- Capture `{verified_correction_history}`: the correction is applied once, effective from its recorded date, with earlier sales retaining the earlier assumption.
- Evidence gates: Law's check results establish script/file-format support, extraction accuracy and visible agent execution. Verify saved correction history against the approved key, not only the final total.
- Label any edited acceleration “Time-lapse”. Do not claim a speed-up factor, runtime, parallel work or unattended scheduling without evidence.
- Sources: PLAN sections 10, 12 and 14; DESIGN sections 4 to 6; `data/demo/messages.md`.

## Scene 5 — Morning: the board meeting is ready

- Duration: `{morning_scene_duration}`.
- Story beat: the morning message, “Your board meeting is ready”, with the approval list.
- PLAN section 17 specifies 7am as the morning story cue; it is narrative timing, not proof of delivery at that time.
- Proposed narration, only when evidenced: “By morning, the result is ready to review.”
- Evidence gates: scheduled execution and return-message delivery require recorded successful checks. If unavailable, ask Damian to approve an honestly labelled result-view treatment.
- Do not portray a manually launched run as an unattended overnight task.
- Sources: PLAN sections 12, 15 and 17; DESIGN section 6.1.

## Scene 6 — The payslip reveal and the decision

- Duration: `{payslip_and_meeting_scene_duration}`.
- Shot: the verified payslip, preserving the top-to-bottom order in `submission/payslip_layout.md`.
- Headline: “RM {hourly_rate} per hour”. Supporting values: “RM {take_home}” and “{total_hours} hours”.
- Proposed narration: “This is what my business paid for my time—not just what came in.”
- Visible caveat: “Provisional earnings: an expense amount is unknown.”
- Proposed narration: “An unreadable expense is still missing, so these earnings may be lower when it is confirmed. The hours use assumptions, corrections and stated event time—not a complete timesheet.”
- Product shot: `{verified_product_results}` with a loss marker only where the tool establishes a loss.
- Explain through caption or narration: product profit uses plan costs and direct production/fulfilment time; take home uses ledger payments and the whole week's time. Product profits do not add up to take home.
- Plan-comparison shot: `{target_hourly_rate}` against `{hourly_rate}`, and `{planned_margin_percent}` against `{actual_margin_percent}`. Do not relabel the target as a generated prediction.
- Debate shot, following `submission/board_meeting_layout.md`:
  - Payroll: `{actual_payroll_recommendation}` with `{payroll_cited_evidence}`.
  - Growth coach: `{actual_growth_recommendation}` with `{growth_cited_evidence}`.
  - Auditor: `{actual_ruling}` and `{ruling_reason_with_citations}`.
- Leave agent dialogue unfilled until actual files exist. The answer key's expected ruling direction is not an actual ruling.
- Proposed narration: “One colleague argues for hourly earnings, another for revenue and sales. The Auditor checks the evidence and rules.”
- Raise-plan shot: `{upheld_recommendation}` linked to `{draft_reference}`, followed by the complete needs-review list.
- Evidence gate: actual ledger statuses, amounts, minutes, source labels, review items and product results must match Sharon's approved key. Ruling direction must be checked, not copied into the run.
- No precise raise promise or future-demand claim while projection rules remain unconfirmed.
- Sources: PLAN sections 3, 10 and 17; DESIGN sections 4.2, 4.3, 5, 7 and 8; draft answer key limitations.

## Scene 7 — Individual approval, then class

- Duration: `{approval_and_close_scene_duration}`.
- Shot: `{verified_individual_approval_evidence}` for each draft shown, followed by the student going to class.
- Proposed narration: “I review each draft and approve it individually. Nothing is sent or posted before my approval.”
- Do not use one blanket approval for all drafts. Do not add an interaction control that the confirmed implementation does not support.
- Show sending or posting only if the corresponding action is actually evidenced after its individual approval. Otherwise end at the verified review or approval state.
- Closing line: “Kau tidur, kami lembur. You sleep, we do the overtime.”
- Evidence gate: Law confirms the supported approval behaviour; Damian approves the final closing treatment.
- Sources: PLAN sections 2 and 17; DESIGN sections 5.1 and 6.1.

## Recording handoff

- Confirm organiser requirements, total duration and all scene timings with Damian.
- Obtain Sharon's persona and business sign-off, then Law/Sharon's real-run comparison with the key.
- Clear each scene's implementation gate before speaking its success narration.
- Retain original full-run recordings and backup copies; use recorded evidence rather than a live demo.
- Never invent an agent exchange, missing receipt, correction history or successful delivery for a shot.
- Keep limitations and review items readable in the edit, including the unknown-expense caveat.
- Label time-lapse edits and disclose any manual launch or fallback.
- Resolve Day Zero, cut-order and trigger decisions explicitly rather than treating proposals as approved.
- These notes provide a script and capture plan only; recording and editing remain with Damian.
