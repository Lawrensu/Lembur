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

* None yet. Add one line per item: the file name, who added it, the date, and what was being built.

## Evidence already recorded elsewhere

These are real results, but they are not screenshots. Keep them as they are and do not restate them as session evidence.

* **Proof 3, photo half**: recorded under the proof in `docs/PLAN.md`, section 12. The bot was created, its token was saved locally and checked live against Telegram, and a photo sent from the phone landed in `workspaces/998236319/inbox/` as a valid JPEG, with the four baseline plan files seeded. The payslip half is not met: `app/runner.py` does not exist yet.
* **Package 3 tests**: 70 offline tests, 60 passed, 10 skipped for unavailable symlink support, no failures. Run from the repository root with `python -B -m unittest discover -s app/tests -p "test_bot*.py"`.
* **Payslip template**: `submission/payslip_template.html`, with a sample PDF printed from an installed browser and the look approved on 10 October.
* **What we already know**, listed under the proofs in `docs/PLAN.md`, section 12: scripts run from a skill, CSV was chosen, the agents' instructions were rehearsed against the answer key, and the payslip command filled the template with no placeholder left.

## Why this matters

The organisers changed the rule on 10 October: WorkBuddy does not have to be part of the final solution, but we must show proof that we used it while building, and explain in the presentation how, where and in what scenarios. The deck covers that story on its WorkBuddy slide. This folder is the evidence behind it.
