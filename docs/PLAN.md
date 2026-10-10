# Lembur: Master Plan

> **Kau tidur, kami lembur.** (You sleep, we do the overtime.)
>
> Accounting apps tell you what you earned. We tell you what you earned per hour of your life, and then help you give yourself a raise.

---

## 0. How to use this file

* **Two sources of truth**
  * This file: the product, scope, validation, roles and schedule.
  * `docs/SYSTEM_DESIGN.md`: how the system works (data, tools, agents, workflows, outputs).
* **Not written in either file**: ask Law, do not assume.
* **Section numbers are stable**: sections 5 to 9 are a pointer block, and the other numbers keep their topics, so older references still resolve.
* **Redesigned on 10 October, 18:00**: the product is now a chat bot of our own. It no longer runs inside WorkBuddy. Sections 1, 4, 11 to 15, 17 and 18 were rewritten. Sections 2, 3, 10 and 16 changed little.
* **Keep it simple**: Law's rule for the rest of the build. Add no feature, file, field or proof that is not written in these docs. If something looks missing, ask before building it.

---

## 1. Context

* **Hackathon**: Hackerdorm × BuilderX, Track 2 (Agentic Solutions).
* **Problem statement**: how can AI agents autonomously solve real world problems by understanding goals, planning workflows, using tools and delivering complete end to end outcomes for users?
* **Deadline**: 9:00am Sunday. We submit by 8:00am.
* **Rule change, reported by the organisers on 10 October**: WorkBuddy does not have to be part of the final solution. We must show proof that we used it while building, and explain in the presentation how, where and in what scenarios. [confirm] Law adds the organisers' exact message here.
* **What the agent should be capable of**, from the track brief, and where we show each
  * **Understanding the goal**: the Bookkeeper and Payroll read the nightly message.
  * **Planning tasks**: the plan for the night (design section 6.1).
  * **Executing actions**: agents act through tools (design section 6.4).
  * **Collaborating and validating**: Payroll argues against the Growth coach, and the Auditor rules.
  * **Integrating results**: the payslip.
  * **Delivering the final outcome**: the morning message with the payslip file.
* **What makes a strong solution**, from the track brief
  1. **Real problem and user value**: a clear user and measurable value.
  2. **Agentic workflow**: task decomposition, multistep execution, tool calling, agent collaboration, parallel workflows, validation, adapting to outcomes.
  3. **Meaningful use of WorkBuddy**: as written, WorkBuddy is the execution platform. Under the rule change we show it as our build platform (section 11), and we keep one recorded run of our agents inside WorkBuddy as insurance (section 12, proof 5).
  4. **End to end execution**: one prompt, one goal, no manual guiding of each step.
  5. **Usable and verifiable results**: reliable, complete, practical output.

---

## 2. Product summary

* **Name**: Lembur, Malay for working overtime. The agents do the overtime while the student sleeps.
* **Modes**: Day Zero (planning) and Night Shift (running).
* **One line**: an AI back office team in the student's chat app that tells student founders what they really earn per hour of their time, before they start and every week after, and drafts the changes that would earn them more.
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
* **Why not a general assistant**, such as OpenClaw, or WorkBuddy itself
  * **Numbers you can trust**: a general assistant does money arithmetic with the model. Ours never does: every figure comes from tested tools and is checked against an answer key.
  * **No set up**: our user is a student at 2am. She will not install an assistant, obtain model keys and write instructions.
  * **Narrow by design**: it cannot run commands on her machine or send anything. Nothing leaves without her approval.
  * **It has an opinion**: hourly rate, profit per hour by product, plan against reality. A general assistant gives those only to someone who already knows to ask.
  * **One line for Q&A**: a general assistant is the workshop. Lembur is the finished tool, and we built it in such a workshop.

---

## 4. Scope

* **In scope**
  1. **Night Shift**: the nightly workflow for a running business, through the chat bot. Build first.
  2. **Day Zero**: the planning workflow for a new business. Design agreed, built only on Law's word (section 15).
* **Out of scope**
  * **A web app or dashboard**: the chat is the whole interface. A web app pulls build time into screens and logins.
  * **WhatsApp**: future work. It needs a business account and a public address. Telegram is the channel we build.
  * **Automatic posting of approved drafts**: the system never posts or sends a draft. The student sends an approved draft herself.
  * **Voice notes**: future work. They need a speech to text service.
  * **Hosting and a container file**: future work. The demo runs on the team's machine.
  * **Late and due payment tracking**: does not fit prepaid chat sellers.
  * **Multi person or helper features**: the `person` data field only, no features.
  * **Integrations with accounting or order tools**: roadmap slide only (section 16).
  * **Dress rehearsal simulation, exam mode**: parked.

---

## 5 to 9. System design

Moved to `docs/SYSTEM_DESIGN.md`. Old section numbers map as follows.

* **5. Two modes, one engine**: design section 1.
* **6. Time model**: design section 4.2.
* **7. Agents**: design section 5. How they act is design section 6.4. The deterministic tools are design section 4.
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
* **Checking the key itself**: the hand calculation is confirmed by a second, independent calculation before anyone builds against it. The scripts of both calculations are kept as a record in the `.ref` folders beside the data. They read the removed workbooks and no longer run. The comparator still reads `data/answer_key/.expected_ledger.ref/calculation.json`, so that folder must stay.
* **Intake order**: the Bookkeeper reads inbox files in file name order, then adds rows that come only from the message. Transaction IDs follow that order.
* **Two kinds of run are checked**: a replay with the fake model, inside the tests, and a run with the real models (section 12, proof 4). Both use `workspace/` and the same comparator.
* **Pass condition**: the run's outputs match the answer key exactly (statuses, minutes, and money to the sen). A mismatch is a bug to fix, not something to explain away in the demo.
* **How to check it**: the test harness in `data/test_harness/`, written by Sharon. Run each script from the repository root.
  * `python -B data/test_harness/compare_outputs.py`: compares `workspace/` with the answer key and prints PASS or FAIL. It checks every ledger row, recalculates the figures on its own, and checks that the plan correction was applied.
  * `python -B data/test_harness/reset_workspace.py --clean-only`: empties `workspace/` before a run. `--full` also copies the plan and every inbox file. `--day <date>` copies one day's files, but it empties the workspace first, so it cannot be used between the nights of one run.
  * `python -B data/test_harness/mutation_test.py`: proves the comparator catches eleven kinds of error. It works in a temporary folder and never touches `workspace/`.
  * **Not compared**: the `notes` and `description` columns of transactions, because an agent words them itself. Hours lines are matched by date, activity, product and assumption reference.

---

## 11. How WorkBuddy is used

WorkBuddy is our build platform. It is not part of the running product.

* **How**: each of us works with WorkBuddy as the builder in our own checkout. We give it the docs as the source of truth, it writes the code or the content, and the result is checked before it is merged.
* **Where and in what scenarios**
  * **Building the engine**: the reconciliation, hours and numbers tools, the command line and the payslip filler were written in WorkBuddy sessions, with their tests.
  * **Building the runner and the bot**: the same way.
  * **Building the dataset**: the synthetic receipts, orders, bank statement, nightly messages and the answer key, with a second independent calculation that had to agree with the first.
  * **Building the story**: agent identities, the payslip template, the deck outline, the video script and the question and answer sheet.
  * **Running our agents during development**: before the redesign, the four agents were instruction files that WorkBuddy ran as skills. A skill run of our own script passed on 10 October. That is where the agents' instructions were first shaped.
* **Evidence pack**: `submission/evidence/`. Each of us adds screenshots of our WorkBuddy sessions, task lists and key exchanges, with one line each on what was being built. Session history is easy to lose, so capture it as you go.
* **What we say**: only what WorkBuddy really did. Work done or checked by other means is not presented as WorkBuddy's.

---

## 12. Proofs

Each proof answers one question before we build on the answer. The owner writes the result under the proof in this shape: `**Result, <date> <time>, <name>**: pass, fail or fallback taken. What was done. What happened.`

1. **The reading model accepts an image through the gateway**
   * **Why**: receipts arrive as photos. Nothing else matters if this fails.
   * **Steps**: deploy the model in the gateway dashboard. Send one request with `data/demo/inbox/order_2026-10-11_zahra.png` and ask for the date, the amount, the customer and the payment reference.
   * **Pass when**: it returns 2026-10-11, RM5.00, Zahra and DEMO-IN-010.
   * **Fallback**: another model that accepts images, behind the same module.
   * **Owner**: Law.
2. **The reasoning model can run one night as an agent**
   * **Why**: agents act by asking for tools in a fixed reply format (design section 6.4). A model that drifts from the format cannot run a night.
   * **Steps**: run the night of 2026-10-05 through the runner with the real model.
   * **Pass when**: four rows, T0004 marked `duplicate`, and a saved `numbers.json`, with no manual help.
   * **Fallback**: a stronger model in the same role.
   * **Owner**: Law.
3. **The bot receives a message and a photo and replies with a file**
   * **Why**: the chat is the whole interface.
   * **Steps**: create a bot with `@BotFather`. Put its token in `.env`. Send the bot a text and a photo, then the word `payslip`.
   * **Pass when**: the photo is in the inbox of that chat's workspace, and the payslip file arrives in the chat.
   * **Fallback**: run the night from the command line and show the files.
   * **Owner**: [confirm]
4. **The whole demo week passes the comparator**
   * **Why**: this is the pass condition of section 10.
   * **Steps**: replay the seven nights of `data/demo/messages.md` through the runner with the real models, then run `python -B data/test_harness/compare_outputs.py`.
   * **Pass when**: it prints PASS with no difference.
   * **Fallback**: fix the prompt or the runner. A mismatch is a bug, not something to explain away.
   * **Owner**: Law, checked by Sharon.
5. **One recorded run of our agents inside WorkBuddy**
   * **Why**: insurance. The judging slide still names WorkBuddy as the execution platform (section 1).
   * **Steps**: install the four instruction files from `skills/` as WorkBuddy skills. Run the night of 2026-10-05 with the Bookkeeper skill, then the Payroll skill. Record the screen.
   * **Pass when**: the same four rows and a saved `numbers.json`.
   * **Fallback**: none needed. The evidence pack of section 11 stands by itself.
   * **Owner**: Law.

* **What we already know**, from before the redesign
  * **Our scripts run from a WorkBuddy skill**: passed on 10 October with its managed Python 3.13.
  * **The data files are CSV**: decided on 10 October. The `.xlsx` workbooks and the code that read them are removed.
  * **The agents' instructions work**: one full pass of the demo week that followed only the files in `skills/`, the inbox images and the nightly messages matched the answer key with no difference. That pass was not run in WorkBuddy and used a different model from the one we will run on.
  * **The payslip can become a PDF**: Damian printed the sample payslip to PDF with an installed browser and no install, and approved the look.
  * **The payslip template fills**: the payslip command filled Damian's template from the rehearsed week with no placeholder left.

---

## 13. Team split

* **A. Builder (Law)**: the runner, the model module, the agent prompts, integration.
* **B. Data and business (Sharon)**: the demo dataset, the answer key, the comparator, checking every run against the key. Then Day Zero, on Law's word.
* **C. Design and story (Damian)**: agent identities, the payslip template, the wording of the bot's replies, the deck, the video.
* **Three way split of the remaining build** [confirm]: Law decides. This proposal follows the seams of design section 6.3, so that three people can build at once.
  * **Law**: `app/runner.py`, `app/model.py`, `prompts/`. Proofs 1, 2, 4 and 5.
  * **Sharon**: `app/bot.py` and proof 3. The evidence pack. The comparison of each full run.
  * **Damian**: the fixed sentences the bot says, the morning message, the deck with a slide on how WorkBuddy was used, the video script for the chat story.
* **Where things stand, 10 October 18:00**
  * **Working**: the tools and the command line, with their tests. The payslip command and Damian's template. The dataset, the answer key and the comparator.
  * **Written, not yet built**: the runner, the model module, the bot, the prompts.
  * **Removed**: the WorkBuddy platform checks, the `.xlsx` support, the runtime probe.
* **Everyone**
  1. **Pull `dev` first.** Work that started from an older `dev` rests on a design that has changed.
  2. **Pull requests go into `dev`**, never into `main`.
  3. **Capture evidence as you go** (section 11).
* **Order of work**: each step is verified before the next one builds on it.
  1. **Proof 1**: the reading model.
  2. **Runner with a fake model**: the week replays in tests.
  3. **Proof 2, then proof 4**: the real model, one night, then the week.
  4. **Bot and proof 3**: in parallel with step 2, against the seam of design section 6.3.
  5. **First full run through the chat**: the midnight checkpoint.
  6. **Recording**: from real run outputs.

---

## 14. Timeline (to 9:00am)

* **18:00 to 21:00**
  * **A**: proof 1, the runner with a fake model, the prompts.
  * **B**: the bot against the seam, proof 3. Start the evidence pack.
  * **C**: the bot's sentences, the deck for the chat story.
  * **21:00: the runner passes the comparator with the real model, or the fallback is taken (section 15).**
* **21:00 to 24:00**
  * **A**: the runner and the bot joined. Proof 5 recorded.
  * **B**: every full run compared with the key.
  * **C**: the video script from real outputs.
  * **Midnight: first full run through the chat.**
* **00:00 to 04:00**
  * **A**: fixes, then the optional items in the order of section 15.
  * **B**: Day Zero, only on Law's word.
  * **C**: slides.
* **04:00: feature freeze. Fixes only.**
* **04:00 to 07:00**: record several full runs and keep the best. Edit the video. Finish the documentation.
* **08:00: submit.** Do not aim for 8:59.
* **Never demo live**: agent runs are long. Keep backup recordings.
* **Nap in shifts**: one person stays sharp for recording and submission.

---

## 15. Cut order if behind schedule

* **If the runner does not pass the comparator by 21:00**: the fallback is the run inside WorkBuddy with the instruction files in `skills/`. The demo shows that run, and the bot becomes the roadmap.
* **If the midnight checkpoint is missed, cut in this order**
  1. **Day Zero generation**: show the hand written plan as "the plan".
  2. **The bot**: start a night from the command line and show the files.
  3. **The plan written by the model**: use the fixed list of steps.
  4. **Open debate**: reduce to a single Auditor ruling.
* **Optional, only after the midnight checkpoint, in this order**: the payslip as a PDF, the price only raise projection. WhatsApp and a container file stay future work (section 4).
* **Never cut**: ledger, reconciliation flags, payslip with hourly rate, raise plan, the check against the answer key.
* **Why this order**: the payslip and validation carry the differentiator and the "usable and verifiable results" criterion. Everything above them can be shown honestly as a file.

---

## 16. Growth path (one slide, zero build time)

* **Path**: run alongside existing tools as the business grows.
  1. **Solo student**: our agents keep the books in a portable ledger and produce the payslip.
  2. **First helper**: hours logged per person. The payslip answers "is paying a helper worth it?"
  3. **Using accounting or order software**: the ledger moves across once. Our agents then read from those tools and keep producing payslips and decisions.
* **Answer to have ready**: "What happens when they outgrow you?" They move their books to accounting software and keep using us for time and decisions.
* **More ways in**: WhatsApp beside Telegram, voice notes, a hosted service. Each is a new channel or a deployment, not a new engine (design section 6.5).
* **Only build work allowed for growth**: the `person` field and the fixed ledger columns (design section 3).

---

## 17. Demo storyline

One character, told across time. The whole story happens in her chat app.

1. **Week 0** (about 30 seconds): the plan. The hand written plan stands in for Day Zero unless it is built.
2. **Title card**: "Four weeks later…"
3. **The Night Shift**: one message before bed with the day's receipts. The agents at work, shown as the plan for the night and the tool calls (time lapse).
4. **Morning**: "Your board meeting is ready." The payslip arrives as a file.
5. **Climax**: the hourly rate, the debate, the ruling, plan versus reality, and the drafts.
6. **Close**: one reply to approve. The student goes to class.

---

## 18. Open decisions

* **Decided**
  * **Product name**: Lembur.
  * **Payslip day**: Sunday night.
  * **Data model and calculation rules**: as written in the design file.
  * **Branches**: README is the authority. Role A works on `dev-law`.
  * **Day Zero owner**: Sharon.
  * **The product is our own chat bot** (10 October): WorkBuddy is the build platform, not the host.
  * **Runtime models**: from the model gateway the organisers provided. The tools we build with are not part of the product.
  * **No agent framework and no third party package**: our own runner, the standard library, plain HTTPS.
  * **Agents act through tools in a short loop**, and each night starts with a written plan.
  * **Channel**: Telegram is the one we build. WhatsApp, a web app, hosting and voice notes are future work.
  * **Data files are CSV.** The demo CSV files are the source of truth.
  * **Payslip**: an HTML template filled by a command. PDF is optional.
  * **Approval**: by reply, a file move. The system posts and sends nothing.
  * **Shared figures and audit**: Payroll saves `audit/<week>/numbers.json`, and the Auditor compares a recomputation with that file. The payslip is built once.
  * **Agent style, decided by Damian**: professional colleagues, using role titles.
  * **Raise projection and Day Zero**: agreed as designs. Built only on Law's word.
* **Still open**
  * **The three way split** (section 13).
  * **Which model fills each role** (proofs 1 and 2).
  * **The organisers' exact wording of the rule change** (section 1).
