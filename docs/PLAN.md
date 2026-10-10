# Lembur: Master Plan

> **Kau tidur, kami lembur.** (You sleep, we do the overtime.)
>
> Accounting apps tell you what you earned. We tell you what you earned per hour of your life, and then help you give yourself a raise.

---

## 0. How to use this file

* **Two sources of truth**
  * This file: the product, scope, validation, roles and schedule.
  * `docs/SYSTEM_DESIGN.md`: how the system works (data, tools, agents, workflows, outputs).
* **Not written in either file**: ask the team, do not assume.
* **Section numbers are stable**: sections 5 to 9 moved to the design file and keep a pointer here, so older references still resolve.
* **Demo dataset and answer key**: separate files owned by Role B. Section 10 says what they must contain.

---

## 1. Context

* **Hackathon**: Hackerdorm × BuilderX, Track 2 (Agentic Solutions, Tencent WorkBuddy).
* **Theme**: how can AI help students and small businesses solve real business problems and operate more effectively?
* **Rule**: implementation, slides and documentation are all delivered using WorkBuddy.
* **Deadline**: 9:00am. We submit by 8:00am.
* **What judges look for (Track 2 brief)**
  * **Real problem and user value**: a clear user and measurable value.
  * **Agentic workflow**: task breakdown, multistep execution, tool use, agent collaboration, parallel work, validation, adapting to outcomes.
  * **Meaningful use of WorkBuddy**: WorkBuddy does the real work, not just chat.
  * **End to end execution**: one prompt, one goal, no manual guiding of each step.
  * **Usable and verifiable results**: reliable, complete, practical output.

---

## 2. Product summary

* **Name**: Lembur, Malay for working overtime. The agents do the overtime while the student sleeps.
* **Modes**: Day Zero (planning) and Night Shift (running).
* **One line**: an AI back office team on WorkBuddy that tells student founders what they really earn per hour of their time, before they start and every week after, and drafts the changes that would earn them more.
* **User**: a student running, or about to start, a side business while studying. Sells through Instagram, Telegram and campus bazaars. Gets paid in cash and bank transfers, with screenshots as proof.
* **Core pain**: not knowing whether the business actually makes money, least of all per hour of their time.
* **Why it happens**: the data is scattered and informal, nobody does data entry at 2am, and nobody tracks their own hours.
* **Core reveal**: a weekly payslip showing the real hourly rate, always paired with a raise plan.
* **Design principle**: turn business numbers into human truths. Write "RM3.10 an hour", not "18% margin".

---

## 3. Positioning

* **Alongside, not against**: we run with the tools small businesses already use or will adopt (order tools like Take App, accounting tools like Bukku, payment tools like HitPay). Books can live anywhere. We own time and decisions.
* **Plumbing, not pitch**: receipt reading, reconciliation and chat input are commodity features. We build them because the product needs them, not as our innovation.
* **What is ours**
  * Hours inferred from orders and messages, roughly right and correctable.
  * A payslip anyone understands.
  * Agents with conflicting objectives debating in the open.
  * Plan versus reality, from Day Zero onwards.
  * Actions drafted and waiting for approval, not just advice.
* **Honest admissions for Q&A**
  * Receipt reading, reconciliation and chat input exist everywhere.
  * Hours are estimates: only as good as the minutes per unit, and correctable with one reply.
  * Unplanned time such as failed batches or supply runs is missed.
  * Day Zero estimates tend to be optimistic, which the plan versus reality loop exposes.
  * A big platform could add an hourly rate view. Our defence is the audience, the experience and working alongside their tools.

---

## 4. Scope

* **In scope**
  1. **Night Shift**: the nightly workflow for a running business. Build first.
  2. **Day Zero**: the planning workflow for a new business. Build second. It writes the plan file the Night Shift reads.
* **Out of scope**
  * **All in one platform**: pulls build time into dashboards and logins, and weakens WorkBuddy's role.
  * **Late and due payment tracking**: does not fit prepaid chat sellers.
  * **Dress rehearsal simulation**: parked. It would be a third workflow.
  * **Exam mode**: parked.
  * **Voice note trigger**: stretch goal, depends on the first hour checks.
  * **Multi person or helper features**: the `person` data field only, no features.
  * **Integrations with accounting or order tools**: roadmap slide only (section 16).

---

## 5 to 9. System design

Moved to `docs/SYSTEM_DESIGN.md`. Old section numbers map as follows.

* **5. Two modes, one engine**: design section 1.
* **6. Time model**: design section 4.2.
* **7. Agents**: design section 5. The deterministic tools are design section 4.
* **8. Workflows**: design section 6.
* **9. Data model**: design section 3. Conventions for dates, weeks, money and rounding are design section 2.

---

## 10. Validation

* **Planted problems and the expected result of each** (statuses are defined in design section 4.1)
  * **Duplicate receipt**: the second copy is `duplicate`, left out of totals, and on the review list.
  * **Missing receipt**: a bank line with no document becomes a row with status `unmatched`, counted in totals, and on the review list.
  * **Amount that does not match the bank statement**: `needs_review`, the bank amount is used, and both amounts are in `notes`.
  * **Blurry receipt**: `needs_review`, amount empty, left out of totals, document still filed.
  * **Bestseller that loses money**: the product with the most units sold has a profit below zero after fees and shipping (design section 4.3).
  * **Event hours**: one nightly message states an event with its duration.
  * **Correction**: one reply corrects a `minutes_per_unit` value mid week, with sales of that product both before and after it.
* **Rules the demo dataset must follow**
  * **One week**: Monday to Sunday.
  * **One product per order**: so per order fees, shipping and packing time belong to one product.
  * **Payment methods**: `cash` and `bank_transfer` only.
  * **Bank statement**: CSV or a text PDF, never a photo. Every line has a unique reference.
  * **Duplicate receipt**: not cash, and identical to the original on date, type, amount, counterparty and reference. The planted duplicate must not copy the mismatched receipt: a later copy of that receipt is a known reconciliation limit.
  * **Mismatched amount**: the receipt and its bank line share the same reference.
  * **Missing receipt**: an expense whose bank description names the supplier, so the category is clear.
  * **Bank transfer sales**: every sale needs a distinct counterparty or a reference. Two sales with the same date and amount and empty counterparty and reference make the second row `duplicate`, not ambiguous. When the duplicate keys differ, equal amounts within one day may still be ambiguous without bank references. The answer key states which bank line each belongs to.
  * **Materials purchases**: restock size, so one receipt does not swamp the week's take home.
  * **Stated hours**: for events only, written as clock times or plain numeric hours. Unsupported duration wording goes to review.
* **The answer key must state**
  * Expected ledger totals by category.
  * The expected status and review list entry for each planted problem.
  * Expected minutes for each hours line, and the total. Match hours lines by date, activity, product and assumption reference, never by `entry_id`: only open week IDs may be renumbered.
  * Expected take home and hourly rate.
  * Expected profit and profit per hour for each product.
  * The expected direction of the Auditor's ruling.
* **Expected ledger files**: Role B provides `ledger_transactions.csv`, `ledger_bank_lines.csv` and `ledger_hours.csv` with the same columns as the workspace ledger CSV files. Payroll can then be built and checked before the Bookkeeper is finished.
* **Where the files live**: demo inputs stay outside `workspace/`, so the workspace can be wiped and refilled before each recorded run.
  * `data/demo/plan_products.csv`, `data/demo/plan_channels.csv`, `data/demo/plan_assumptions.csv`, `data/demo/plan_change_log.csv`: the hand written plan, copied to `workspace/plan/` before a run.
  * `data/demo/inbox/`: the documents the student drops, copied to `workspace/inbox/` before a run.
  * `data/demo/messages.md`: each nightly message and the correction reply, with its date.
  * `data/answer_key/ledger_transactions.csv`, `data/answer_key/ledger_bank_lines.csv`, `data/answer_key/ledger_hours.csv`: the expected ledger.
  * `data/answer_key/answer_key.md`: every other expected figure and flag.
* **Checking the key itself**: the hand calculation is confirmed by a second, independent calculation before anyone builds against it.
* **Intake order**: the Bookkeeper reads inbox files in file name order, then adds rows that come only from the message. Transaction IDs follow that order.
* **Pass condition**: the run's outputs match the answer key exactly (statuses, minutes, and money to the sen). A mismatch is a bug to fix, not something to explain away in the demo.

---

## 11. How WorkBuddy is used

* **One message before bed**: remote tasks through messaging apps (Telegram).
* **The messy inbox folder**: reading authorised local folders, batch file processing.
* **The agent team**: expert team and parallel tasks, each agent packaged as a skill.
* **The Auditor**: task breakdown with verification, shown as its own agent.
* **Payslip, books, board meeting deck**: native document, spreadsheet and presentation generation.
* **Every night, automatically**: automation (scheduled tasks).
* **Approval, then action**: human approval before anything is sent, connectors where needed.
* **Slides and documentation**: generated in WorkBuddy from the real demo run's outputs.

---

## 12. First hour checks

* **Run before building**: the owner of a check writes its result under the check as soon as it is known. Checks 6 and 7 are done.
* **Owners, decided 10 October**: Sharon runs checks 1, 2, 3, 4, 9 and 10. Damian runs check 11. Law runs 5 and 8. Reason: these checks test the platform, not our code, and every teammate has WorkBuddy installed.
* **A person runs these checks, not an agent**: they need a phone, a Telegram chat and a look at the screen. An agent may prepare the test files and write up the result it is given.
* **How to write a result**: one bullet under the check, in this shape: `**Result, <date> <time>, <name>**: pass, fail or fallback taken. What was done. What happened.` Add one more bullet for anything the build must know, such as a prompt that needed a click.
* **Time box**: checks 6 and 7 shared 30 minutes. Every other check has 15 minutes. At the limit, write what was seen, take the fallback and move on.
* **Keep the repository clean**: use a throwaway Telegram bot or chat. A bot token is a secret and never goes into a file here. Delete every test file from `workspace/` afterwards. Commit only the results written in this section.
* **Dependencies**: do not install any dependency without Law's approval. If WorkBuddy asks to install something to finish a check, stop and write that down.
* **Check 6 evidence**: record the direct shell run and the temporary diagnostic skill invocation separately. Remove the diagnostic skill afterwards; it is not one of the four product agents.
* **Check boundaries**: check 6 is a runtime smoke test, including workspace write access and a failing exit code when any probe fails. Schema and empty cell conventions belong to check 7 through the sheet adapter and its tests.

* **Menu names below**: taken from the WorkBuddy guides at `workbuddy.ai/docs`. They may differ slightly in the app. If a menu is missing, write that down as the result.
* **`<clone>` below**: the full path of your copy of this repository.

1. **Telegram text message starts a task**
   * **Why**: the trigger in the demo.
   * **Fallback**: start the task inside WorkBuddy and show the message separately.
   * **Owner**: Sharon.
   * **Set up once, for checks 1, 2, 9 and 10**
     1. In Telegram, open `@BotFather` and send `/newbot`. Give a name and a username ending in `bot`. Copy the token it returns.
     2. In WorkBuddy, open the Assistant icon in the sidebar, then Assistant Settings, then Channels. Choose Telegram, paste the token and save.
     3. In Telegram, open the new bot, press Start and send "hello". If the bot shows as unavailable, send `/start`.
     4. Keep the computer on with WorkBuddy running. In System Settings, turn on Prevent Sleep.
   * **Steps**: from the phone, send "Create a file named check1.txt containing the word ok in the folder `<clone>/workspace`". Do not touch the computer.
   * **Pass when**: the file appears in `workspace/` with no click on the computer.
   * **Also write down**: whether the computer asked for a confirmation, and which folder the task used. The guides suggest a remote task may be tied to its own Assistant folder. The build must know whether a Telegram task can reach `workspace/` at all.
2. **Telegram voice note works**
   * **Why**: stretch goal only.
   * **Fallback**: typed message, or the phone keyboard's dictation.
   * **Owner**: Sharon. Five minutes at most: the guides do not mention voice notes for Telegram.
   * **Steps**: send a voice note saying "Create a file named check2.txt containing the word ok in the same folder".
   * **Pass when**: the file appears.
3. **Scheduled tasks run reliably** (the computer must stay on)
   * **Why**: the overnight story.
   * **Fallback**: run manually and present honestly what the schedule does.
   * **Owner**: Sharon.
   * **Steps**
     1. Open Automation in the sidebar and choose New Automation.
     2. Task: "Append one line with the current date and time to the file `<clone>/workspace/check3.txt`".
     3. Schedule: One time, a few minutes ahead. If One time has no clock time, use Daily at a time a few minutes ahead. Choose `<clone>` as the workspace directory. Save and activate.
     4. Run A: leave WorkBuddy open and wait.
     5. Run B: repeat with the screen locked and Prevent Sleep on.
   * **Pass when**: the line appears at the set time in both runs with no click.
   * **Also write down**: the smallest repeat interval offered, whether a permission prompt appeared, and whether a skill can be chosen for the run.
4. **Receipt reading accuracy on 3 samples**
   * **Why**: Bookkeeper reliability.
   * **Fallback**: clean demo images plus one deliberately blurry receipt.
   * **Owner**: Sharon.
   * **Steps**
     1. Copy `order_2026-10-11_zahra.png`, `receipt_pouches.png` and `receipt_thread_blurred.png` from `data/demo/inbox/` into an empty folder outside the repository, so the answer key is out of reach.
     2. Start a new task with that folder selected, on a model that accepts images.
     3. Ask: "Read the three images in this folder. For each one give the date, whether it is money in or money out, the amount, the other party, the payment method and the payment reference. If a value cannot be read, say unreadable. Do not guess."
     4. Compare with rows T0019, T0009 and T0012 of `data/answer_key/ledger_transactions.csv`. For T0019 the document amount is RM5.00; the ledger shows the bank amount.
   * **Pass when**: every readable value matches, and the blurred amount comes back as unreadable rather than a number.
   * **Also write down**: the model used.
5. **A custom skill per agent, and the team run is visible**
   * **Why**: agent collaboration on camera.
   * **Fallback**: run agents in sequence and show the `boardroom` folder as evidence.
   * **Owner**: Law.
   * **Find out**: whether four skills can work inside one task, whether two of them can run in parallel, and what the screen shows while they do. The guides describe an expert team under Experts in the sidebar and say a team run costs several times a single run.
6. **A skill can run a deterministic script**
   * **Why**: arithmetic and matching. Also check which runtime and libraries are available.
   * **Fallback**: spreadsheet formulas inside the ledger.
   * **Direct shell result, 2026-10-10**: the first run at 13:17 Malaysia time failed before the checks. `tools/numbers.py` shadows the standard library `numbers` module, causing a circular import through `decimal`.
   * **Direct shell retry**: `C:/Users/User/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -P D:/Projects/Lembur/tools/check_runtime.py`. The executable reports Python 3.13.14 despite its directory name. Seven of nine checks passed; exit code 1. Decimal rounding, ISO week, CSV, temporary write access and workspace write access passed. `openpyxl` is absent, so its import and the `.xlsx` probe failed. Reported script format: CSV. No dependencies installed.
   * **Workspace cleanup**: the probe wrote and read its own temporary file inside `workspace/`, then removed it. A regression test confirms the directory contents are unchanged.
   * **Rename, decided and done**: `tools/numbers.py` is now `tools/business_numbers.py`; the remaining test loader and probe instructions are updated. Direct probe execution no longer needs `-P`.
   * **Skill invocation result, 2026-10-10**: passed. Law ran a temporary diagnostic skill inside WorkBuddy that called `python -B tools/check_runtime.py` from the repository root. It used the managed Python 3.13.14 and gave the same seven of nine checks and CSV mode as the direct run; the two failures are the absent `openpyxl`. Check 6 is conclusive: a skill can run a deterministic script. The diagnostic skill is not one of the four product agents and is removed afterwards.
   * **Time box**: checks 6 and 7 started at 13:17 Malaysia time; their shared limit is 13:47. If still inconclusive at that point, use the documented fallback.
7. **`.xlsx` reads and writes reliably**
   * **Why**: the data model.
   * **Fallback**: CSV.
   * **Result, decided by Law at 13:42 on 2026-10-10**: CSV chosen. `openpyxl` is not installed; the eight `.xlsx` tests remain skipped. CSV adapter tests cover file names, headers, string rows and empty cells. The adapter retains `.xlsx` support for later.
   * **Entry point rule**: pass `fmt="csv"` to every `sheets.load_book` and `sheets.save_book` call, never `auto`: an installed library must not silently switch the data source.
   * **Files**: `<book>_<sheet>.csv`, as listed in design section 3.1 and validation section 10.
   * **Full suite result, 2026-10-10**: both managed Python with `-B -m unittest discover -s tools/tests -p "test_*.py" -v` and Law's exact `py -B -m unittest discover -s tools/tests -p "test_*.py"` command passed: 63 tests discovered, 55 passed, 8 skipped, no failures or errors, exit code 0. All skipped tests require `openpyxl`. The independent `test_design_rules.py` was not edited.
8. **Credits used by one full run**
   * **Why**: practicality question from judges, and our own budget.
   * **Fallback**: smaller dataset.
   * **Owner**: Law.
   * **Steps**: note the credit balance before and after one full run. The balance is under Usage in the profile at `workbuddy.ai`, or under plan and usage in the app settings.
9. **Morning message goes back to Telegram**
   * **Why**: the "board meeting is ready" moment.
   * **Fallback**: screenshot of the WorkBuddy result.
   * **Owner**: Sharon. Needs the set up from check 1.
   * **Steps**
     1. After check 1, look at the Telegram chat: did the result of that task arrive there?
     2. Create an automation as in check 3 with the task "Reply with exactly: Your board meeting is ready." Turn on the switch that sends the result to the Assistant or the messaging app. Schedule it a few minutes ahead.
     3. In the Telegram chat, ask "Send me the file `<clone>/workspace/check1.txt`".
   * **Pass when**: the scheduled message arrives on the phone with no click on the computer.
   * **Also write down**: whether step 3 delivered a file. The payslip would be sent the same way.
10. **Telegram photo reaches `workspace/inbox`**
    * **Why**: receipts are on the student's phone.
    * **Fallback**: show files dropped into the folder.
    * **Owner**: Sharon. Needs the set up from check 1.
    * **Steps**: from the phone, send `receipt_pouches.png` to the bot twice, once as a photo and once as a file. Each time add the text "Save this attachment into `<clone>/workspace/inbox` and tell me the saved file name".
    * **Pass when**: the file is in `workspace/inbox` and opens.
    * **Also write down**: the saved file names, whether the photo was renamed or compressed, and where the attachment went if it did not reach `inbox`. File names matter: the Bookkeeper reads the inbox in file name order.
11. **WorkBuddy turns the HTML payslip into a PDF**
    * **Why**: the payslip is an HTML template filled by a script (design section 7). The student should receive a PDF.
    * **Fallback**: the HTML file is the payslip.
    * **Owner**: Damian.
    * **Steps**
      1. Put one self contained HTML file in an empty folder: the payslip template with sample values, or any styled page if the template is not ready.
      2. Start a new task with that folder selected.
      3. Ask: "Convert the HTML file in this folder to a PDF with the same name, in the same folder. Keep the layout exactly. Do not install anything. If you would need to install something, stop and tell me what."
    * **Pass when**: the PDF opens and looks like the page does in a browser, and nothing was installed.
    * **Also write down**: exactly how WorkBuddy did it, tool or command, and how long it took. The Payroll skill has to repeat it.

---

## 13. Team split

* **A. Builder (Law)**: WorkBuddy workflow, agent skills and instructions, receipt extraction, reconciliation, trigger, payslip and deck output.
* **B. Data and business (Sharon)**: persona, demo dataset with planted problems, answer key, expected ledger, hand written plan file. Then Day Zero, confirmed owner. Then documentation.
* **C. Design and story (Damian)**: agent identities, payslip and board meeting look, pitch slides, video script, recording and editing.
* **Why Role B builds Day Zero**: Day Zero's output is the plan file Role B writes by hand first, so Role B knows its exact shape. Day Zero is mostly skills and instructions, so it can be built without touching the Night Shift.
* **Order of work**: each step is verified before the next one builds on it.
  1. **Role A, first hour checks 6, 7, 5 and 4**: they decide script or formulas, and `.xlsx` or CSV. Verified when the results are written in section 12.
  2. **Everyone, data and rules freeze**: design sections 2 to 4. Verified when all three teammates have read and agreed them.
  3. **Role B, plan file, dataset, answer key and expected ledger**: verified when a second calculation agrees with the hand calculation.
  4. **Role A, Bookkeeper and reconciliation**: verified when the ledger matches the expected ledger.
  5. **Role A, Payroll**: verified when hours, take home and rates match the answer key. It can start as soon as step 3 is done, working from the expected ledger.
  6. **Role A, Auditor and debate**: verified when the ruling points the expected way.
  7. **Role C, recording**: needs real run outputs from steps 4 to 6.
* **What Role C does meanwhile**: look, identities, deck skeleton and script run in parallel from the start. The payslip order in design section 7 is fixed, so Role C and Payroll work to the same list.
* **Current tasks, as of 10 October 15:30**: do them in the order listed. Anything unclear or not written here: ask Law before acting.
* **Where things stand**
  * **Working**: the reconciliation, hours and numbers tools and the command entry point `tools/lembur.py`, checked by 82 tests. Replayed night by night through the commands, they rebuild Sharon's expected ledger and answer key exactly: every status, every hours line, take home RM39.50, 938 minutes, RM2.53 an hour.
  * **Decided today**: CSV files (check 7), scripts run from a skill (check 6), intake order, the payslip format (design section 7), and who runs each remaining check (section 12).
  * **Not built yet**: the four skills and the payslip command. No run by the agents exists, so no real output exists yet.
* **Role B, Sharon**
  1. **Sign off the answer key**: `data/answer_key/answer_key.md` is still marked draft. The tools reproduce every figure in it.
  2. **Make the CSV files the only copy**: `data/demo/plan_*.csv` and `data/answer_key/ledger_*.csv` are the source of truth. Update the paths in `data/demo/messages.md` and `answer_key.md`. Remove the `.xlsx` workbooks from `data/demo/` and `data/answer_key/`, and either update the helper scripts to read the CSV files or remove them.
  3. **Apply the intake order**: file name order, so on 6 October Hana is T0006 and Nisa is T0007. The CSV ledger already says so; `answer_key.md` does not yet.
  4. **Persona**: replace the real university name with a generic one.
  5. **Platform checks 1, 2, 3, 4, 9 and 10**: section 12 gives the steps. Write each result under its check.
  6. **From 18:00**: compare the first real run with the answer key. Waits on Role A.
  7. **Day Zero**: waits on Law's decision about the two parked proposals in design section 8. Do not start it before then.
* **Role C, Damian**
  1. **`checklist.md`**: move it under `submission/`. Reword it as a task list for the three of us, with no "drafter" or "checker" roles. Keep the judging criterion as "Meaningful use of WorkBuddy". Remove the line about confirming cuts: section 15 is fixed. No dashes in prose.
  2. **`submission/payslip_template.html`, due 18:00**: built to the format and field names in design section 7. This replaces the layout note as the handoff to Role A.
  3. **Check 11**: section 12.
  4. **`board_meeting_layout.md`, `deck_outline.md`, `video_script.md`, `qa_sheet.md`**: all four can start now.
  5. **Sample figures**: until a real run exists, use the answer key figures and label them as samples. Never invent a figure.
  6. **Trigger scenes**: the Telegram trigger, the overnight schedule and the morning message are unproven until checks 1, 3 and 9 are recorded. Keep those scenes loose until then.
* **Role A, Law**
  1. **Entry point**: `tools/lembur.py`, the commands the skills call. Done; its commands are listed in design section 4.
  2. **The four skills**: Bookkeeper first, then Payroll, then the Auditor and the Growth coach.
  3. **Payslip command**: fills Damian's template from `numbers.json`.
  4. **Checks 5 and 8**: section 12.

---

## 14. Timeline (to 9:00am)

* **Confirmed schedule**: checkpoints in bold are fixed; the time blocks below are confirmed as written.

* **12:00 to 13:00**
  * **A**: first hour checks (section 12).
  * **B**: persona, start the hand written plan file.
  * **C**: payslip look, agent identities.
* **13:00 to 18:00**
  * **A**: Bookkeeper intake, reconciliation, ledger.
  * **B**: demo dataset with planted problems, answer key, expected ledger.
  * **C**: payslip template, deck skeleton.
* **18:00 to 24:00**
  * **A**: Payroll, hours, payslip.
  * **B**: check run output against the answer key.
  * **C**: story and video script.
  * **Midnight: first rough end to end run.**
* **00:00 to 04:00**
  * **A**: Auditor, boardroom debate, plan versus reality, polish.
  * **B**: Day Zero, subject to Law's decision on the parked formulas after the midnight checkpoint.
  * **C**: slides drafted in WorkBuddy.
* **04:00: feature freeze. Fixes only.**
* **04:00 to 07:00**
  * **A**: record several full runs, keep the best.
  * **B**: documentation in WorkBuddy from real run outputs.
  * **C**: edit video, time lapse the slow parts.
* **08:00: submit.** Do not aim for 8:59.
* **Never demo live**: agent runs are long. Keep backup recordings.
* **Nap in shifts**: one person stays sharp for recording and submission.

---

## 15. Cut order if behind schedule

* **If the midnight checkpoint is missed, cut in this order**
  1. **Day Zero generation**: show the hand written plan file as "the plan".
  2. **Telegram trigger**: start the task inside WorkBuddy.
  3. **Scheduled overnight run**: run manually.
  4. **Open debate**: reduce to a single Auditor ruling.
* **Never cut**: ledger, reconciliation flags, payslip with hourly rate, raise plan, Auditor check against the answer key.
* **Why this order**: the payslip and validation carry the differentiator and the "usable and verifiable results" criterion. Everything above them can be faked honestly or shown as a static file.

---

## 16. Growth path (one slide, zero build time)

* **Path**: run alongside existing tools as the business grows.
  1. **Solo student**: our agents keep the books in a portable ledger and produce the payslip.
  2. **First helper**: hours logged per person. The payslip answers "is paying a helper worth it?"
  3. **Using accounting or order software**: the ledger moves across once. Our agents then read from those tools and keep producing payslips and decisions.
* **Answer to have ready**: "What happens when they outgrow you?" They move their books to accounting software and keep using us for time and decisions.
* **Only build work allowed for growth**: the `person` field and the fixed ledger columns (design section 3).

---

## 17. Demo storyline

One character, told across time.

1. **Week 0, Day Zero** (about 30 seconds): idea in, plan and predicted hourly rate out.
2. **Title card**: "Four weeks later…"
3. **The Night Shift**: message before bed, messy folder, agents at work (time lapse), 7am "Your board meeting is ready."
4. **Climax**: the payslip reveals the hourly rate, the agent debate, plan versus reality, and the raise plan with drafts.
5. **Close**: one tap to approve. The student goes to class.

---

## 18. Open decisions

* **Decided**
  * **Product name**: Lembur.
  * **Payslip day**: Sunday night.
  * **Data model and calculation rules**: as written in the design file.
  * **Branches**: README is the authority. `main`, `dev`, `dev-law`, `dev-sharon`, `dev-damian`; Role A works on `dev-law`.
  * **Day Zero owner**: Sharon.
  * **Schedule and cut order**: sections 14 and 15 confirmed as written.
  * **Shared figures and audit**: Payroll saves `audit/<week>/numbers.json`; the Auditor compares a read only rerun with that file. The payslip is built once after the ruling.
  * **Nontransaction review**: `audit/<week>/review_items.md`, combined with transaction review rows on the payslip. No new sheet.
  * **Agent style, decided by Damian**: professional colleagues, using role titles.
  * **Demo data**: the CSV files in `data/demo/` and `data/answer_key/` are the source of truth. The `.xlsx` workbooks are superseded.
  * **Payslip format**: an HTML template with named placeholders, filled by a script, then turned into a PDF by WorkBuddy. Details in design section 7; the PDF step is check 11.
  * **Check owners**: Sharon runs the platform checks 1, 2, 3, 4, 9 and 10. Damian runs check 11. Law keeps 5 and 8. Reason: these checks test the platform rather than our code, and every teammate has it installed.
* **Still open**
  * **Open items in the design file**: design section 8. Both calculation proposals stay parked until Law decides after the midnight checkpoint.
