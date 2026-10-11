# Project submission video script

## Draft status and production rules

- Text-only script and shot list for the hackathon submission, not a product advertisement or a generated video.
- The story happens in the student's chat app (PLAN section 17). WorkBuddy is the platform we built the product with, not part of the running product. Name it only in the build segment (scene 8) and only for what it really did (PLAN section 11). Naming WorkBuddy does not establish execution evidence.
- Proposed narration, scene order and capture instructions. Damian owns the final narration, visual look, recording and editing.
- Total length: `{submission_video_duration}`. Obtain the organisers' limit and Damian's approval before fixing scene timings.
- All scene durations below are placeholders. PLAN section 17 suggests about thirty seconds for Week 0; this is guidance, not the confirmed submission time limit.
- Aisyah is the fictional student in the merged dataset, subject to Sharon's story sign-off. Use `{approved_persona_name}` in narration until then.
- There is no scheduled run. A night starts when the student sends her message, and the morning message arrives when the night finishes.
- The tool layer, the Telegram bot, the model module, the runner and the prompts are built and merged (PLAN section 13). The demo week replays through the runner with the real models and the comparator prints PASS (PLAN section 12, proof 4), so the figures below are real run outputs. Proof 3's live chat half is not yet recorded: the payslip file has not yet arrived in the chat, only in `workspace/payslips/2026-W41.html`.
- Every business figure below is copied from the recorded run of 11 October 08:10, which passed the comparator. `{approved_persona_name}` stays a placeholder until Sharon signs the persona off.
- Narration that describes successful execution is usable only after its scene's evidence gate passes. A scripted claim is not execution evidence. The one scene that still needs a live recording is scene 3 and scene 5's chat delivery (proof 3).
- Demo data only. Keep the expected ledger and answer key out of the production agents' inputs.

## Scene 1: Week zero, a starting plan

- Duration: `{day_zero_scene_duration}`.
- Purpose: introduce the idea and a plan that the later payslip can test.
- Shot: `{approved_persona_name}` sends `{business_idea_message}` to the bot in her chat app; show costing, pricing assumptions, time assumptions and Auditor checks only if implemented and verified.
- Proposed narration: “Before starting, I want to know what this business could earn, and how much of my time it would take.”
- Output shot: `{verified_plan_summary_reference}` and `{verified_plan_file_reference}`.
- Plan target: “RM {target_hourly_rate} per hour”, from the hand written plan file.
- Proposed narration: “This is my starting plan. The time estimates are assumptions; the weekly payslip will test them against reality.”
- Evidence gate: Day Zero is an agreed design, not built (design section 8). Law says when. Do not show generated predictions or a break even result.
- If Day Zero generation is not built, show the hand written plan file as "the plan" (PLAN section 15, cut 1). Law decides. Label it honestly.
- Sources: PLAN sections 3, 4, 15 and 17; DESIGN sections 1, 6.2 and 8.

## Scene 2: The narrative time jump

- Duration: `{time_jump_duration}`.
- Title card: “Four weeks later…”
- Keep the same student character.
- This is the documented story framing, not a claim of weeks of real deployment. The fixture is one prepared Monday-to-Sunday week.
- Sources: PLAN sections 10 and 17; `data/demo/messages.md`.

## Scene 3: Before bed, message and messy documents

- Duration: `{bedtime_scene_duration}`.
- Shot: `{verified_nightly_message}` and its dated demo inbox batch, sent in the chat. The real messages and their dated files are in `data/demo/messages.md`; for example Monday 2026-10-05 is four files (two order screenshots, a bead receipt and its duplicate) with the message “Two Instagram keychain orders today, Dana and Mira…”.
- Proposed narration: “The orders and receipts are scattered. Before bed, I send one message to my bot and leave the documents with it.”
- Show actual synthetic receipts, order screenshots and the bank statement only on their documented intake dates.
- The bank statement arrives on Sunday; do not depict it arriving before its batch. Cash orders in the message are individual orders, not extra screenshots.
- Evidence gate: the bot receiving a message and a photo is proof 3 (PLAN section 12). If the bot is cut, start a night from the command line and show the files (PLAN section 15, cut 2). Label it honestly.
- Sources: PLAN sections 12, 15 and 17; DESIGN sections 6.1 and 6.5; `data/demo/messages.md` replay instructions.

## Scene 4: The Night Shift

- Duration: `{night_shift_scene_duration}`.
- This is the agents-at-work scene. Show it as the plan for the night and the tool calls.
- Shot sequence from a continuous actual run:
  - The message and files arriving in the inbox.
  - The plan for the night, `audit/<week>/plan_<date>.md`: each step, why tonight needs it, and its outcome.
  - Bookkeeper intake and filed source links.
  - Tool calls: an agent asks for a tool, the runner runs it and returns the result.
  - Reconciliation statuses and explanations for unclear matches.
  - Ledger rows with their evidence references.
  - Payroll hours and deterministic numbers outputs.
  - Payslip-day recommendations, Auditor report and ruling, then the unsent drafts, then the generated payslip. The drafts come before the payslip (design section 6.1).
- Proposed narration: “First the plan for tonight is written. Then the agents read and review, and ask the tools to do the matching and the calculations. Uncertainty is flagged, not guessed.”
- Include actual evidence of the duplicate, missing receipt, mismatch and unreadable amount; do not prefill pass labels. The recorded run shows: the duplicate filed as T0004, the blurred thread receipt T0012 with an empty amount on 2026-10-08, a keychain sale amount mismatch T0019, and the missing bead top-up T0020 on 2026-10-11.
- Capture the correction history: keychains P01 `minutes_per_unit` 20 to 15, effective 2026-10-07, source `message.2026-10-07`, applied once with earlier sales keeping the 20-minute assumption (`workspace/plan/plan_change_log.csv`).
- Capture the night plan from `workspace/audit/2026-W41/plan_2026-10-11.md`: each step with its “why tonight needs it” and its outcome, including the two steps the rules added back (growth recommendation, drafts).
- Evidence gates: receipt reading is proof 1, one real night is proof 2 and the whole week is proof 4 (PLAN section 12). The files are CSV. Verify saved correction history against the approved key, not only the final total.
- Label any edited acceleration “Time-lapse”. Do not claim a speed-up factor, runtime or parallel work without evidence. Nothing here is scheduled.
- Sources: PLAN sections 10, 12 and 17; DESIGN sections 4 to 6.

## Scene 5: Morning, the board meeting is ready

- Duration: `{morning_scene_duration}`.
- Story beat: the morning message in the chat, “Your board meeting is ready”, with the payslip file and the drafts waiting for a reply.
- The morning message arrives when the night finishes (design section 6.1, step 11). There is no scheduled 7am run; any morning time on screen is narrative framing, not proof of delivery at that time.
- Proposed narration, only when evidenced: “By morning, the result is ready to review.”
- Evidence gate: the full run through the chat (the first full run checkpoint, PLAN section 14). Fallback if the bot is cut: the payslip file and the files of the night from the command line, labelled honestly.
- Do not portray a run as scheduled or unattended. A night starts when the student sends her message.
- Sources: PLAN sections 14, 15 and 17; DESIGN sections 6.1 and 6.5.

## Scene 6: The payslip reveal and the decision

- Duration: `{payslip_and_meeting_scene_duration}`.
- Shot: the verified payslip, which arrives as an HTML file in the chat (a PDF is optional and not built), preserving the fixed ten section order of design section 7. The file is `workspace/payslips/2026-W41.html`.
- Headline: “RM 2.53 per hour”. Supporting values: “RM 39.50” and “15.6 hours”.
- Proposed narration: “This is what my business paid for my time, not just what came in.”
- Visible caveat: “Provisional earnings: an expense amount is unknown.” (run detail: transaction T0012, the blurred thread receipt, has an empty amount; the Auditor's ruling notes take-home and hourly are provisional because of it.)
- Proposed narration: “An unreadable expense is still missing, so these earnings may be lower when it is confirmed. The hours use assumptions, corrections and stated event time, not a complete timesheet.”
- Product shot: Beaded keychain (P01) 11 units sold, revenue RM54.50, profit −RM10.50, −RM2.80 per hour, `loses_money: true`; Beaded bracelet (P02) 3 units sold, revenue RM54.00, profit RM32.00, RM16.99 per hour. Show the loss marker on the keychain only, where the tool establishes it.
- Explain through caption or narration: product profit uses plan costs and direct production/fulfilment time; take home uses ledger payments and the whole week's time. Product profits do not add up to take home.
- Plan-comparison shot: RM12.00 target against RM2.53 actual, and 40 percent planned margin against 36 percent actual. Do not relabel the target as a generated prediction.
- Debate shot, following `submission/board_meeting_layout.md`:
  - Payroll: adjust keychain pricing or materials to stop a −RM2.80 per hour loss; focus production on the bracelet at RM16.99 per hour; reallocate part of the 10.0 shared hours toward productive tasks (cited: profit_per_hour_rm −2.80 and 16.99, shared_hours 10.0, hourly_rate_rm 2.53, from numbers.json).
  - Growth coach: pull back from the loss-making keychain (−RM10.50); promote the profitable bracelet (RM32.00); re-evaluate the Instagram channel cost (channel_costs_rm RM32.00) (cited: profit_rm −10.50 and 32.00, channel_costs_rm 32.00, from numbers.json).
  - Auditor: all six recommendations upheld, no conflicts between them (cited: profit_per_hour_rm −2.80 and 16.99, profit_rm −10.50 and 32.00, shared_hours 10.0, hourly_rate_rm 2.53, channel_costs_rm 32.00). The week closes pending the two receipt issues.
- Agent dialogue above is the actual recorded run output, not the answer key's expected direction.
- Proposed narration: “One colleague argues for hourly earnings, another for revenue and sales. The Auditor checks the evidence and rules.”
- Raise-plan shot: the upheld recommendation links to its draft `approvals/2026-W41/01_instagram_post.md` (“Serves Recommendation 2. Hey friends! Our Beaded bracelet is a hit…”), followed by the complete needs-review list: the 15-minute keychain correction (2026-10-07), the blurred thread receipt with a missing amount (2026-10-08), and the missing bead top-up receipt (2026-10-11).
- Evidence gate: actual ledger statuses, amounts, minutes, source labels, review items and product results must match Sharon's approved key. Ruling direction must be checked, not copied into the run.
- No precise raise promise or future demand claim: the raise projection is an agreed design, not built.
- Sources: PLAN sections 3, 10 and 17; DESIGN sections 4.2, 4.3, 5, 7 and 8; draft answer key limitations.

## Scene 7: Approval by reply, then class

- Duration: `{approval_and_close_scene_duration}`.
- Shot: `{verified_individual_approval_evidence}` for each draft shown, followed by the student going to class. Only one draft exists in the recorded run: `approvals/2026-W41/01_instagram_post.md`, serving Recommendation 2 (the bracelet).
- Proposed narration: “I approve each draft with a reply. Lembur posts nothing, I send it myself.”
- Do not use one blanket approval for all drafts. Do not add an interaction control that the confirmed implementation does not support.
- Show no posting or sending by Lembur. End at the reply "approve 1" in the chat, the bot's confirmation, and the draft moved to `approvals/2026-W41/approved/`. (The run left the draft pending; the move to `approved/` needs the recorded approval reply.)
- Closing line: “Kau tidur, kami lembur. You sleep, we do the overtime.”
- Approval is by reply (design section 6.1). Damian approves the final closing treatment, and decides whether scene 8 sits before this closing line or after the story.
- Sources: PLAN sections 2 and 17; DESIGN sections 5.1 and 6.1.

## Scene 8: How we built it, with WorkBuddy

- Duration: `{workbuddy_build_scene_duration}`.
- Purpose: show proof that WorkBuddy was used during the build, and explain how, where and in what scenarios (PLAN sections 1 and 11). It is a short segment outside the chat story.
- Shot: `{evidence_pack_screenshots}` from `submission/evidence/`: WorkBuddy sessions, task lists and key exchanges, each with a caption of what was being built.
- Proposed narration: “We built Lembur with WorkBuddy. Each of us gave it the docs as the source of truth, it wrote the code or the content, and we checked the result before merging.”
- Scenarios to name, only those the evidence pack supports: the engine and its tests, the dataset and answer key, the story, and the early run of the agents as instruction files.
- Do not say or imply that the running product lives in WorkBuddy. Do not present work done or checked by other means as WorkBuddy's.
- Evidence gate: every claim in this scene needs a matching item in the evidence pack.
- Sources: PLAN sections 1, 11 and 12.

## Recording handoff

- Confirm organiser requirements, total duration and all scene timings with Damian.
- Obtain Sharon's persona and business sign-off, then Law/Sharon's real-run comparison with the key.
- Clear each scene's implementation gate before speaking its success narration.
- Retain original full-run recordings and backup copies; use recorded evidence rather than a live demo.
- Never invent an agent exchange, missing receipt, correction history or successful delivery for a shot.
- Keep limitations and review items readable in the edit, including the unknown-expense caveat.
- Label time-lapse edits and disclose any manual launch or fallback.
- The cut order is fixed (PLAN section 15) and belongs to Law.
- These notes provide a script and capture plan only; recording and editing remain with Damian.
