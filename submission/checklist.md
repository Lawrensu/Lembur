# Lembur team checklist

* Sources of truth: `README.md`, then `docs/PLAN.md`, then `docs/SYSTEM_DESIGN.md`.
* Follow PLAN section 13 for task ownership and dependencies. Ask Law about missing requirements or build authorisation; Damian owns the look, story, recording and editing.
* Use demo data only. No secrets, attribution lines, tables or dashes in prose. Name WorkBuddy wherever the product uses it.

## Completed preparation

* [x] Damian: prepare the four professional colleague identities in `submission/identities.md`.
* [x] Damian: provisionally approve a continuous payslip with the hourly rate dominant, and equal Payroll and Growth coach arguments above a separate Auditor ruling.
* [x] Damian: prepare payslip and board meeting layout notes, deck outline, video script and Q&A drafts. Final approval and real run evidence remain pending.
* [x] Damian: approve the exact judging criterion, “Meaningful use of WorkBuddy”.
* [x] Law: provide CSV plan and expected ledger fixtures, the deterministic command entry point, and recorded results for checks 6 and 7.
* [x] Law: move the test harness to CSV with standard library dependencies only.
* [x] Team: agree the HTML placeholder template contract, reply based individual approval, no system posting, and the schedule and cut order.

## Damian: priority handoff before 18:00

* [x] Move this checklist to `submission/checklist.md` and update it for the three teammates.
* [x] Build `submission/payslip_template.html` to SYSTEM_DESIGN section 7. The file is ready for review; Law's renderer integration and acceptance remain pending.
* [x] Preserve the fixed order: week and dates, hourly rate, take home and categories, hours and total, shared hours, product economics, plan comparison, debate and ruling, raise drafts, review list.
* [x] Use only the documented scalar fields and repeating blocks. Keep styles inside the HTML, without scripts or external assets.
* [x] Keep shared hours labelled as already included. Distinguish product profit from ledger based take home, and retain the unknown expense caveat.
* [x] Prepare labelled fixture HTML and export a four page A4 sample PDF without installing anything. Record the export method and timing in PLAN section 12; this is not a completed check 11 pass.
* [x] Damian: review the sample PDF look. Approved at 17:23 on 10 October with “the sample pdf looks good”. This is sample visual approval, not real run validation.
* [ ] Law: confirm the repeatable PDF conversion method for Payroll and verify populated real output pagination. HTML remains available as the fallback.
* [ ] Law or the builder agent: read `submission/payslip_handoff.md` and confirm receipt and acceptance of `submission/payslip_template.html`. The written handoff is ready; acceptance and production integration are not assumed.
* [ ] Review the identity file with Law for the skill instructions.

## Law: build and evidence

* [x] Merge the Windows output encoding and plan correction guards into the entry point. PLAN section 13's older task snapshot predates these changes; runtime acceptance remains separate from merged code.
* [ ] Fill Damian's template from `audit/<week>/numbers.json` through the payslip command, after the ruling.
* [x] Write the Bookkeeper, Payroll, Auditor and Growth coach skill instruction files and run order in the repository. Written files do not establish installation or execution.
* [x] Specify individual approval by reply in the Growth coach instructions: “approve N” moves that draft into `approvals/<week>/approved/`; “skip N” leaves it pending. The system never posts or sends drafts.
* [ ] Verify installation, role handoff and approval file moves in an actual recorded run. Resolve intended parallel recommendations versus common sequential handoff wording through check 5.
* [ ] Clarify the raise plan mapping where an upheld recommendation needs no draft. Growth coach instructions allow this case; SYSTEM_DESIGN section 7 expects a draft reference. Do not fabricate a draft or add a field.
* [ ] Run checks 5 and 8. Record visible team execution and the credit balance change of a complete run.
* [ ] Supply actual recommendation, ruling, audit and draft files for Damian's final content.
* [ ] Give explicit build authorisation before implementing price only projections after the first full run, or Day Zero after the midnight checkpoint. Both designs are agreed, not built.

## Sharon: data and checks

* [ ] Sign off the demo persona and independently checked draft answer key.
* [ ] Update old workbook references to CSV, retire superseded workbook copies and update or retire their helper scripts.
* [ ] Align answer key transaction references with file name intake order: Hana is T0006 and Nisa is T0007 on 6 October.
* [ ] Replace the real university name in the persona with a generic one.
* [ ] Review the CSV test harness and report any problem to Law.
* [ ] Run checks 1, 2, 3, 4, 9 and 10, starting with check 1. Record each result in PLAN section 12; do not put bot tokens in the repository.
* [ ] From 18:00, compare Law's real run with the answer key using the harness. Fix differences in status, minutes, sources, review items and money to the sen before recording.
* [ ] Build Day Zero only after Law authorises it following the midnight checkpoint.

## Damian: story and final outputs

* [x] Refresh `board_meeting_layout.md`, `deck_outline.md`, `video_script.md` and `qa_sheet.md` against the merged rules. Preserve the board structure, proposed nine slides, seven scenes and evidence placeholders; this is a content refresh, not final approval or run validation.
* [ ] Damian: approve the refreshed board presentation, proposed deck sequence, narration and Q&A wording.
* [ ] Confirm the organisers' video limit and the scene timings. Leave timing slots unfilled until confirmed.
* [ ] Keep trigger, scheduling and morning message scenes conditional until checks 1, 3 and 9 establish them.
* [ ] Show approval by reply rather than a button or automatic posting. End at individual approval; the student sends approved drafts herself.
* [ ] For sample previews, use the answer key figures with a clear sample label. Actual dialogue and rulings come from actual output files, not expected answers.
* [ ] Populate final numerical claims only from verified run outputs. Payroll, Growth coach and Auditor copy figures from `audit/<week>/numbers.json`.
* [ ] Include every transaction with `unmatched`, `duplicate` or `needs_review` status and every line of `audit/<week>/review_items.md`.
* [ ] Generate final slides and documentation using WorkBuddy as required by PLAN section 1. The Markdown drafts provide content and layout.
* [ ] Keep helper features, external posting and integrations future only. Do not imply agreed but unbuilt designs are implemented.

## Team: recording and submission

* [ ] Reach the midnight rough end to end checkpoint. If it is missed, follow the fixed PLAN section 15 cut order: Day Zero generation, Telegram trigger, scheduling, then open debate.
* [ ] Never cut the ledger, reconciliation flags, hourly rate payslip, raise plan or Auditor comparison with the key.
* [ ] Observe the 04:00 feature freeze: fixes only.
* [ ] Record several complete verified runs and keep backup recordings. Do not rely on a live demo.
* [ ] Damian: edit the video with readable limitations and clearly labelled time lapse. The narrative time jump is not proof of weeks of real deployment.
* [ ] Review final claims, figures, review coverage and approval states. Submit by 08:00 ahead of the 09:00 deadline.
* [ ] Work on personal branches and pull `origin/dev` before each PR. Target `dev`, never `main`; keep commits small and clear.
