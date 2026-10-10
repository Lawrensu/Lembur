# Lembur team checklist

* Sources of truth: `README.md`, then `docs/PLAN.md`, then `docs/SYSTEM_DESIGN.md`.
* Follow PLAN section 13 for task ownership and order of work. The remaining build is three packages: the backend (Sharon, first), agent orchestration (Law) and the Telegram connection (Damian). Ask Law about missing requirements or build authorisation; Damian owns the look, story, recording and editing.
* Use demo data only. No secrets, attribution lines, tables or dashes in prose. WorkBuddy is the build platform, not part of the running product: name it only for what it really did (PLAN section 11).
* The product is our own chat bot, redesigned on 10 October. Older tasks that depended on running inside WorkBuddy have been removed.

## Completed preparation

* [x] Damian: prepare the four professional colleague identities in `submission/identities.md`.
* [x] Damian: provisionally approve a continuous payslip with the hourly rate dominant, and equal Payroll and Growth coach arguments above a separate Auditor ruling.
* [x] Damian: prepare board meeting layout notes, deck outline, video script and Q&A drafts. They were written before the redesign and are now aligned to it. Final approval and real run evidence remain pending.
* [x] Damian: approve the exact judging criterion, “Meaningful use of WorkBuddy”.
* [x] Damian: build `submission/payslip_template.html` to SYSTEM_DESIGN section 7. Fixed section order, documented fields and blocks only, styles inside the file, no scripts or external assets.
* [x] Damian: keep shared hours labelled as already included, distinguish product profit from ledger based take home, and retain the unknown expense caveat in the template.
* [x] Damian: prepare labelled fixture HTML and export a four page A4 sample PDF without installing anything.
* [x] Damian: review the sample PDF look. Approved at 17:23 on 10 October with “the sample pdf looks good”. This is sample visual approval, not real run validation.
* [x] Law: the payslip command filled Damian's template from the rehearsed week with no placeholder left (PLAN section 12, what we already know).
* [x] Law: provide CSV plan and expected ledger fixtures and the deterministic command entry point.
* [x] Law: move the test harness to CSV with standard library dependencies only.
* [x] Law: a skill run of our own script passed in WorkBuddy on 10 October, and the data files are CSV (PLAN section 12, what we already know).
* [x] Team: agree the HTML placeholder template contract, reply based individual approval, no system posting, and the schedule and cut order.
* [x] Team: agree the redesign of 10 October. The product is our own chat bot, and WorkBuddy is the build platform (PLAN sections 11 and 18).

## Where things stand

* From PLAN section 13, 10 October 23:45.
* **Working, merged into `dev`**: the tools and the command line with their tests, the payslip command and Damian's template, the dataset, the answer key, the comparator and the redesigned docs.
* **Built and merged into `dev`**: the tool layer `app/tools.py` and the Telegram bot `app/bot.py`, each with its tests. **Not built**: the model module, the runner and `prompts/`. Do not present any unbuilt part as done until its proof in PLAN section 12 is recorded.
* **Order of work**: the backend first, merged into `dev`. Meanwhile the prompts are drafted and the bot is built against a stand in. Then the runner and the bot in parallel, then the join, then recording.
* **Seams**: design sections 6.3 and 6.4 fix what each package calls. Stay in your own files. If a seam does not fit, tell Law.
* **Result shape**: the owner of a proof writes the result under it in PLAN section 12 as `**Result, <date> <time>, <name>**: pass, fail or fallback taken. What was done. What happened.`

## Package 1, backend: Sharon, first

* [ ] Build `app/tools.py` first: the seven tools of design section 6.4, inside the workspace only, with the list of what each agent may use.
* [ ] Build `app/model.py` and `.env.example` (design section 6.3). Law gives you the gateway address, the example request and a key privately. The key goes only into your `.env`.
* [ ] Tests for both that run without a key and without a network.
* [ ] Proof 1, the reading model accepts an image through the gateway: send `data/demo/inbox/order_2026-10-11_zahra.png` and expect the four values listed under proof 1. Fallback: another model that accepts images, behind the same module.
* [ ] Open a pull request into `dev` and tell the other two. `app/tools.py` can go in ahead of `app/model.py`.

## Package 2, agent orchestration: Law

* [x] Write the four prompts in `prompts/` (design section 6.4).
* [ ] Build `app/runner.py`: the plan for the night, the agent loop and the order of steps (design sections 6.1, 6.3 and 6.4).
* [ ] Replay the demo week through the runner with a scripted model inside the tests.
* [ ] Proof 2, the reasoning model can run one night as an agent: the night of 2026-10-05 through the runner, with four rows, T0004 marked `duplicate` and a saved `numbers.json`, and no manual help.
* [ ] 03:00 decision point: one night runs through the runner with the real model, or the fallback is taken (PLAN section 15).
* [ ] Proof 4, the whole demo week passes the comparator: replay the seven nights with the real models, then `python -B data/test_harness/compare_outputs.py` must print PASS with no difference.
* [ ] Supply actual recommendation, ruling, audit and draft files for Damian's final content.
* [ ] Give Sharon the gateway address, the example request and a key privately.
* [ ] Add the organisers' exact message about the rule change to PLAN section 1 [confirm].
* [ ] Give explicit build authorisation before anyone implements price only projections or Day Zero. Both designs are agreed, not built.

## Package 3, Telegram connection: Damian

* [x] Create a bot with `@BotFather` and put its token in `.env`. Never put a bot token in the repository. Done: bot `lembur_damian_bot`, and the token was checked live against Telegram. `.env` is git ignored.
* [x] Build `app/bot.py` against a stand in `run_night` that returns the night summary of design section 6.3. It saves files into `inbox/`, answers `payslip`, `review`, `approve N` and `skip N`, and passes anything else to `run_night` (design section 6.5). Merged into `dev` as `4d13715`. 70 offline tests: 60 passed, 10 skipped for unavailable symlink support.
* [x] Write the fixed sentences the bot says and the morning message, “Your board meeting is ready”. Figures in them are copied from `numbers.json`, so only the wording is yours.
* [ ] Proof 3, the bot receives a message and a photo and replies with a file: send a text and a photo, then the word `payslip`. The photo must be in the inbox of that chat's workspace and the payslip file must arrive in the chat. Fallback: run the night from the command line and show the files. **Partial result recorded under the proof in PLAN section 12**: the photo half passed live; the payslip half waits on the runner.
* [ ] Join the bot to the real `run_night` once the runner is in `dev`. This is what unblocks the rest of proof 3.

## Sharon: data and checks

* [ ] Sign off the demo persona and the answer key. `answer_key.md` and `messages.md` were aligned for you on 10 October: CSV paths, Hana as T0006 and Nisa as T0007 on 6 October, and a generic university name. Read those changes first.
* [ ] Review the CSV test harness and report any problem to Law.
* [ ] Read the comparator's report for every full run: `python -B data/test_harness/compare_outputs.py`. A mismatch is a bug to fix, not something to explain away.
* [ ] Build Day Zero only after Law authorises it.

## Damian: story and final outputs

* [ ] Review the identity file against the agent prompts in `prompts/`.
* [ ] Refresh and approve `board_meeting_layout.md`, `deck_outline.md`, `video_script.md` and `qa_sheet.md` against the redesigned source docs.
* [ ] Make the deck with a slide on how WorkBuddy was used to build the product (PLAN section 11), and the video for the chat story (PLAN section 17).
* [ ] Confirm the organisers' video limit and the scene timings. Leave timing slots unfilled until confirmed.
* [ ] Keep the chat scenes conditional on proof 3. If the bot is cut, show a night started from the command line and its files, labelled honestly (PLAN section 15).
* [ ] Show approval by reply rather than a button or automatic posting. End at individual approval; the student sends approved drafts herself.
* [ ] For sample previews, use the answer key figures with a clear sample label. Actual dialogue and rulings come from actual output files, not expected answers.
* [ ] Populate final numerical claims only from verified run outputs. Payroll, Growth coach and Auditor copy figures from `audit/<week>/numbers.json`.
* [ ] Include every transaction with `unmatched`, `duplicate` or `needs_review` status and every line of `audit/<week>/review_items.md`.
* [ ] Keep WhatsApp, voice notes, hosting, posting through a connector, helper features and integrations future only. Do not imply agreed but unbuilt designs are implemented.

## Team: evidence, recording and submission

* [ ] Pull `dev` first. Work that started from an older `dev` rests on a design that has changed.
* [ ] Evidence pack, everyone: add screenshots of your WorkBuddy sessions, task lists and key exchanges to `submission/evidence/`, with one line each on what was being built (PLAN section 11). Session history is easy to lose, so capture it as you go. Say only what WorkBuddy really did.
* [ ] Reach the first full run through the chat by 04:30 (PLAN section 14). If it is missed, follow the fixed PLAN section 15 cut order: Day Zero generation, the bot, the plan written by the model, then open debate. Law decides.
* [ ] Optional, only after the first full run checkpoint and in this order: the payslip as a PDF, the price only raise projection. WhatsApp and a container file stay future work.
* [ ] Never cut the ledger, reconciliation flags, payslip with hourly rate, raise plan or the check against the answer key.
* [ ] Observe the 04:30 feature freeze: fixes only.
* [ ] From 04:30 to 07:00, record several complete verified runs and keep the best, with backup recordings. Never demo live: agent runs are long.
* [ ] Damian: edit the video with readable limitations and clearly labelled time lapse. The narrative time jump is not proof of weeks of real deployment.
* [ ] Nap in shifts: one person stays sharp for recording and submission.
* [ ] Review final claims, figures, review coverage and approval states. Submit by 08:00 ahead of the 09:00 deadline; do not aim for 08:59.
* [ ] Work on personal branches and pull `origin/dev` before each PR. Target `dev`, never `main`; keep commits small and clear.
