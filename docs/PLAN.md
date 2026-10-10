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
  * **Duplicate receipt**: not cash, and identical to the original on date, amount, counterparty and reference.
  * **Mismatched amount**: the receipt and its bank line share the same reference.
  * **Missing receipt**: an expense whose bank description names the supplier, so the category is clear.
  * **Bank transfer sales**: two with the same amount within a day of each other will come out ambiguous unless each carries a reference found on the statement. The answer key states which bank line each belongs to.
  * **Materials purchases**: restock size, so one receipt does not swamp the week's take home.
  * **Stated hours**: for events only.
* **The answer key must state**
  * Expected ledger totals by category.
  * The expected status and review list entry for each planted problem.
  * Expected minutes for each hours line, and the total.
  * Expected take home and hourly rate.
  * Expected profit and profit per hour for each product.
  * The expected direction of the Auditor's ruling.
* **Expected ledger file**: Role B also provides the expected ledger with the same sheets and columns as `ledger.xlsx`. Payroll can then be built and checked before the Bookkeeper is finished.
* **Where the files live**: demo inputs stay outside `workspace/`, so the workspace can be wiped and refilled before each recorded run.
  * `data/demo/plan.xlsx`: the hand written plan file, copied to `workspace/plan/` before a run.
  * `data/demo/inbox/`: the documents the student drops, copied to `workspace/inbox/` before a run.
  * `data/demo/messages.md`: each nightly message and the correction reply, with its date.
  * `data/answer_key/expected_ledger.xlsx`: the expected ledger.
  * `data/answer_key/answer_key.md`: every other expected figure and flag.
* **Checking the key itself**: the hand calculation is confirmed by a second, independent calculation before anyone builds against it.
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

Run before building. Role A writes each result under its check as soon as it is known.

1. **Telegram text message starts a task**
   * **Why**: the trigger in the demo.
   * **Fallback**: start the task inside WorkBuddy and show the message separately.
2. **Telegram voice note works**
   * **Why**: stretch goal only.
   * **Fallback**: typed message.
3. **Scheduled tasks run reliably** (the computer must stay on)
   * **Why**: the overnight story.
   * **Fallback**: run manually and present honestly what the schedule does.
4. **Receipt reading accuracy on 3 samples**
   * **Why**: Bookkeeper reliability.
   * **Fallback**: clean demo images plus one deliberately blurry receipt.
5. **A custom skill per agent, and the team run is visible**
   * **Why**: agent collaboration on camera.
   * **Fallback**: run agents in sequence and show the `boardroom` folder as evidence.
6. **A skill can run a deterministic script**
   * **Why**: arithmetic and matching. Also check which runtime and libraries are available.
   * **Fallback**: spreadsheet formulas inside the ledger.
7. **`.xlsx` reads and writes reliably**
   * **Why**: the data model.
   * **Fallback**: CSV.
8. **Credits used by one full run**
   * **Why**: practicality question from judges, and our own budget.
   * **Fallback**: smaller dataset.
9. **Morning message goes back to Telegram**
   * **Why**: the "board meeting is ready" moment.
   * **Fallback**: screenshot of the WorkBuddy result.

---

## 13. Team split

* **A. Builder (Law)**: WorkBuddy workflow, agent skills and instructions, receipt extraction, reconciliation, trigger, payslip and deck output.
* **B. Data and business (Sharon)**: persona, demo dataset with planted problems, answer key, expected ledger, hand written plan file. Then Day Zero [confirm owner]. Then documentation.
* **C. Design and story (Damian)**: agent identities, payslip and board meeting look, pitch slides, video script, recording and editing.
* **Why Role B builds Day Zero** [confirm]: Day Zero's output is the plan file Role B writes by hand first, so Role B knows its exact shape. Day Zero is mostly skills and instructions, so it can be built without touching the Night Shift.
* **Order of work**: each step is verified before the next one builds on it.
  1. **Role A, first hour checks 6, 7, 5 and 4**: they decide script or formulas, and `.xlsx` or CSV. Verified when the results are written in section 12.
  2. **Everyone, data and rules freeze**: design sections 2 to 4. Verified when all three teammates have read and agreed them.
  3. **Role B, plan file, dataset, answer key and expected ledger**: verified when a second calculation agrees with the hand calculation.
  4. **Role A, Bookkeeper and reconciliation**: verified when the ledger matches the expected ledger.
  5. **Role A, Payroll**: verified when hours, take home and rates match the answer key. It can start as soon as step 3 is done, working from the expected ledger.
  6. **Role A, Auditor and debate**: verified when the ruling points the expected way.
  7. **Role C, recording**: needs real run outputs from steps 4 to 6.
* **What Role C does meanwhile**: look, identities, deck skeleton and script run in parallel from the start. The payslip order in design section 7 is fixed, so Role C and Payroll work to the same list.

---

## 14. Timeline (to 9:00am)

Checkpoints in bold are fixed. Time blocks marked [confirm] are proposals.

* **12:00 to 13:00**
  * **A**: first hour checks (section 12).
  * **B**: persona, start the hand written plan file.
  * **C**: payslip look, agent identities.
* **13:00 to 18:00** [confirm]
  * **A**: Bookkeeper intake, reconciliation, ledger.
  * **B**: demo dataset with planted problems, answer key, expected ledger.
  * **C**: payslip template, deck skeleton.
* **18:00 to 24:00** [confirm]
  * **A**: Payroll, hours, payslip.
  * **B**: check run output against the answer key.
  * **C**: story and video script.
  * **Midnight: first rough end to end run.**
* **00:00 to 04:00**
  * **A**: Auditor, boardroom debate, plan versus reality, polish.
  * **B**: Day Zero [confirm].
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

## 15. Cut order if behind schedule [confirm]

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
* **Still open**
  * **Agent style**: professional colleagues or distinct personalities. Role C's call. It does not affect the build.
  * **Every [confirm] in this file**: Day Zero owner (13), time blocks (14), cut order (15).
  * **Open items in the design file**: design section 8.
