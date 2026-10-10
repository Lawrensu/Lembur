# Role C task list (Damian)

Tasks for Law and Sharon are in docs/PLAN.md section 13.

- Source of truth: `README.md`, then `docs/PLAN.md`, then `docs/SYSTEM_DESIGN.md`.
- Keep the deliverable order below. Ask Law about anything absent, marked `[confirm]`, or dependent on an unresolved check.

## Already done

- [x] Read the three source documents in order.
- [x] Work on `dev-damian` and pull `origin/dev` before starting.
- [x] Confirm professional colleagues with role title names: Bookkeeper, Payroll, Growth coach and Auditor.
- [x] Confirm a warm, student first visual direction. Damian now follows the repository rule: name WorkBuddy wherever the product uses it.
- [x] Create and check `submission/identities.md` against design section 5.
- [x] Damian: write `submission/deck_outline.md`, `submission/video_script.md` and `submission/qa_sheet.md` as review ready content drafts. Final approval and evidence population remain pending.
- [x] Provisionally approve both format neutral wireframes: continuous payslip; equal Payroll and Growth coach arguments above the Auditor.
- [x] Write `submission/payslip_layout.md` and `submission/board_meeting_layout.md` as placeholder only notes, not final fillable templates.
- [x] Receive Sharon's merged demo persona, baseline plan, expected ledger and independently verified draft answer key. Business sign-off and real run verification remain pending.

## Do next: unblock the priority handoffs

- [ ] Damian: review `submission/identities.md` and pass it to Law for the agent instructions. File prepared; Law's receipt is not confirmed.
- [ ] Damian: build `submission/payslip_template.html` by 18:00 to design section 7. It is one self contained HTML file with `{{name}}` placeholders and `<!-- each NAME -->` blocks, no scripts, and nothing loaded from the internet. It replaces `payslip_layout.md` as the handoff to Law.
- [ ] Damian: run check 11 (WorkBuddy turns the HTML payslip into a PDF) as soon as a first version of the template exists. Steps and where to write the result: PLAN section 12.
- [ ] Check results for the other checks: PLAN section 12 says who runs each one and where the result is written. Read them before fixing the layouts and the story.
- [ ] Damian: confirm the total video duration. Leave scene timings as placeholders until agreed.
- [x] Damian: follow the WorkBuddy naming rule and retain the exact judging criterion, "Meaningful use of WorkBuddy".

## Produce the remaining content files, in this order

- [ ] **Hand off the payslip template before 18:00.** The layout note is written; the fillable template and delivery remain pending. Preserve the approved look, PLAN section 2 wording, and the static caveat about unreadable amounts (see `submission/payslip_layout.md`).
  - Preserve design section 7's top to bottom order:
    - Week and date range.
    - Hourly rate as the headline.
    - Take home with totals by category.
    - Hours by activity with the total.
    - Shared hours.
    - Profit per hour by product; mark products that lose money.
    - Plan versus reality.
    - Debate summary and Auditor's ruling.
    - Upheld raise recommendations, each linked to its draft.
    - Needs your review list.
- [ ] **Review `submission/board_meeting_layout.md` and confirm the final format adaptation.** Notes are written: equal Payroll and Growth coach arguments above an Auditor evidence, decision and reason block. Keep ruling text as placeholders until actual outputs exist. Approval is by reply ("approve N" or "skip N").
- [ ] **Review and approve `submission/deck_outline.md`.** The draft covers all five judging criteria and the future only growth path; confirm the proposed slide sequence before final generation. Retain "Meaningful use of WorkBuddy".
- [ ] **Review and approve `submission/video_script.md`.** The text draft follows PLAN section 17 and includes a shot list and implementation gates. Confirm the submission time limit, scene timings and any honestly labelled fallbacks before recording.
- [ ] **Review and rehearse `submission/qa_sheet.md`.** The draft covers PLAN section 3's honest admissions, fixture versus run validation, unknown expense limitations and future only outgrowth. Replace evidence placeholders only after the relevant approvals.
- [ ] **Trigger scenes stay loose.** The Telegram message, the overnight schedule and the morning message are unproven until checks 1, 3 and 9 are recorded in PLAN section 12.

## Validate before showing results

- [x] Damian: read all six content files against README, PLAN and SYSTEM_DESIGN. Draft content check passed; this is not run validation.
- [ ] Recheck the populated final files and generated outputs after verified runs: trace every actual figure, claim, ruling and approval state; retain review items and scope boundaries.
- [ ] Sharon's sign-off of the answer key and the comparison of the first real run with it: PLAN section 13 (Role A and Role B). Fixture checks passing is not approval of a release or proof of a real workflow run.
- [ ] Only then replace sample figures with figures from the first real run, keeping their source references.
- [ ] Generate final slides and documentation through the required workflow in PLAN section 1, using these content files and the verified outputs.
- [ ] Damian: review the visual result; keep agent style, final look, recording and editing decisions with Damian.

## Recording and submission checkpoints

- [ ] Midnight rough end to end run: if the checkpoint is missed, cuts follow the fixed order in PLAN section 15. The cut order belongs to Law; no one else changes it.
- [ ] Observe the 04:00 feature freeze: fixes only.
- [ ] After verified runs, record several complete runs, keep the best and retain backups. Do not rely on a live demo.
- [ ] Damian: edit the recording, clearly label time lapsed sections, and show only evidenced behaviour. Do not imply the narrative time jump proves weeks of real operation.
- [ ] Review the final package and submit by 08:00, ahead of the 09:00 deadline (PLAN sections 1 and 14).

## Rules for every handoff

- [ ] Use point form, no tables and no attribution lines. Name WorkBuddy wherever the product uses it, including slides, video and documentation.
- [ ] Use demo data only; no keys, tokens or real personal documents.
- [ ] Until a real run exists, use the figures in data/answer_key/answer_key.md and label each one as a sample. Never invent a figure.
- [ ] Label hours as estimates where applicable. Do not present product profits as summing to take home.
- [ ] Day Zero generation and raise projections are agreed designs, not built (design section 8). Do not claim either as built, and do not quote a predicted or projected figure.
- [ ] Keep integrations and helper capabilities future only; exclude other out of scope features from built feature claims.
- [ ] Make small, clear commits on `dev-damian` only. Pull `origin/dev` again before every PR; target `dev`, never `main`.
