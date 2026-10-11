# WorkBuddy evidence pack

PLAN section 11 asks for this folder. WorkBuddy is the platform we built Lembur with, not part of the running product, so the presentation must show what it really did. Session history is easy to lose, so each person adds their own evidence here as they go.

## How to add an item

* One file per piece of evidence, named for what it shows.
* Add one line to the list below: the file name, who added it, the date, and what was being built.
* Screenshots must not contain the bot token, the model key, or any real receipt, bank statement or personal detail.
* Say only what WorkBuddy actually did. Work done or checked another way is not presented as WorkBuddy's.

## What each person adds

* **Law**: the runner, the model module and the prompts being built.
* **Sharon**: the tool layer and its tests; the dataset, the answer key and the comparator work.
* **Damian**: the payslip template, the agent identities, the story documents, and the Telegram bot.

## Items added so far

* `workbuddy_session_payslip_template.png`, Damian, 11 October: the WorkBuddy session that moved the checklist and built the HTML payslip template, including the ten section order and the field contract.
* `workbuddy_session_story_drafts.png`, Damian, 11 October: the WorkBuddy session that produced `deck_outline.md`, `video_script.md` and `qa_sheet.md`, and tightened the evidence rule in `identities.md`.

**One thing to fix on the first image:** the left sidebar shows the signed in account email address. Crop or blur that strip before this folder goes to judges. No token, key or real document is visible.

## The built product and the deck

* **Telegram bot**: `http://t.me/lembur_damian_bot`. The live proof 3 photo check used this bot.
* **Slides**: built in Canva at `https://www.canva.com/design/DAHXkXwiQ1I/7QHnAhURM2yN16ytu5gxtg/edit`. The content behind them is `submission/deck_outline.md`.

## Evidence already recorded elsewhere

These are real results, but they are not screenshots. Keep them as they are and do not restate them as session evidence.

* **Proof 3, photo half**: recorded under the proof in `docs/PLAN.md`, section 12. The bot was created, its token was saved locally and checked live against Telegram, and a photo sent from the phone landed in `workspaces/998236319/inbox/` as a valid JPEG, with the four baseline plan files seeded. The payslip half was blocked then because `app/runner.py` did not exist. The runner is now on `dev` and the chat run is still to be recorded.
* **Package 3 tests**: 71 offline tests, 61 passed, 10 skipped for unavailable symlink support, no failures. Run from the repository root with `python -B -m unittest discover -s app/tests -p "test_bot*.py"`.
* **Payslip template**: `submission/payslip_template.html`, with a sample PDF printed from an installed browser and the look approved on 10 October.
* **What we already know**, listed under the proofs in `docs/PLAN.md`, section 12: scripts run from a skill, CSV was chosen, the agents' instructions were rehearsed against the answer key, and the payslip command filled the template with no placeholder left.

## Why this matters

The organisers changed the rule on 10 October: WorkBuddy does not have to be part of the final solution, but we must show proof that we used it while building, and explain in the presentation how, where and in what scenarios. The deck covers that story on its WorkBuddy slide. This folder is the evidence behind it.
