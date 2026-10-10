# Lembur package 3 handover: the Telegram connection

## What this document is

A self contained brief for the next agent picking up **package 3**, the Telegram connection of Lembur. It records the product context, the exact contract, what is built, what is verified, what is blocked, and the next steps. Read this file first, then the sources it names. Do not guess where this file disagrees with the repository.

## The project in one minute

Lembur is a back office team inside a student founder's chat app. She sends one message and her receipt photos before bed. In the morning she gets a payslip showing what she really earned per hour of her time, plus drafts of the changes that would earn her more. She approves each draft with a short reply.

Hackerdorm × BuilderX, Track 2, Agentic Solutions. Deadline is 9:00am and the team submits by 8:00am.

The product is **the team's own chat bot**. It is not hosted inside WorkBuddy. WorkBuddy is the platform the team builds with, and the presentation must say only what WorkBuddy really did.

Three layers:

1. **Bot**: the chat front door. Receives text and files, sends replies and files.
2. **Runner**: plans the night and runs the four agents in order. Each agent acts only by asking for tools.
3. **Tools**: the deterministic commands in `tools/lembur.py`. They are the only code that calculates or writes a figure.

Agents read and argue. Tools count. An agent has no way to act except through the tools the runner gives it.

## Sources of truth, in this order

1. `README.md`: overview, layout, roles, repo rules.
2. `docs/PLAN.md`: product, scope, validation, proofs, team split, schedule. See sections 12 and 13.
3. `docs/SYSTEM_DESIGN.md`: behaviour and data. See sections 3.1, 6.1 (approval), 6.3 (runtime and seams) and 6.5 (chat).

If the two docs disagree, SYSTEM_DESIGN wins on behaviour and data, PLAN wins on scope and schedule. Anything not written in either file: ask Law, do not assume.

## Package 3 assignment

- **Owner**: Damian.
- **Files**: `app/bot.py` and its tests in `app/tests/`.
- **What it is**: the chat front door of design section 6.5, and the fixed sentences the bot says.
- **Done when**: PLAN section 12 proof 3 passes.
- **Not owned**: `tools/`, `docs/` (except the proof result), `app/model.py`, `app/tools.py`, `app/runner.py`, `prompts/`. If a seam does not fit, tell Law; the seam changes in the design first, then in the code.

## The contract the bot must implement

From SYSTEM_DESIGN section 6.5 and 6.3.

**Transport.** Telegram only. Plain HTTPS calls to the Telegram bot interface with the standard library, asking for new messages in a loop. No bot library, no web framework, no server, no public address. The whole product has no third party package.

**Token.** `TELEGRAM_BOT_TOKEN` in `.env` at the repository root. `.env` is git ignored. A token never appears in a file, a prompt, a log, a reply or a commit.

**Per message**

- A file or photo: saved into `inbox/` of that chat's workspace. Original file name when Telegram gives one, otherwise a name made from the date and time received.
- `payslip`: sends the latest payslip file and the hourly rate.
- `review`: sends the review list.
- `approve N` and `skip N`: the approval behaviour below.
- Anything else: it is tonight's message. The bot calls `run_night` and reports back.

**A new student.** The first message from a chat creates `workspaces/<chat_id>/` with the layout of section 3.1. Day Zero is not built, so the bot copies the hand written plan `data/demo/plan_*.csv` into that workspace's `plan/` folder. An existing workspace is never reseeded.

**The night's date.** Today's date in Malaysia time. A message that starts with `YYYY-MM-DD` does **not** override it. (The dated demo replay in the design is marked `[confirm]` and was explicitly declined; all messages use today.)

**Approve and skip.** They act on the latest week that has drafts. The number is the one at the start of the draft's file name. `approve N` moves that numbered draft from `approvals/<week>/` into `approvals/<week>/approved/`. `skip N` leaves it where it is. The bot confirms either way. It is a file move done by the bot: no agent and no model is involved. Nothing is posted or sent by the system; the student sends an approved draft herself.

**Fixed words only.** The four words are matched by the code. The bot does not use a model to guess what the student meant. The bot calls no model and calculates nothing.

**What the bot says.** Figures are copied from `numbers.json` or from the night summary. The bot calculates nothing and words nothing beyond fixed sentences. The wording of those sentences belongs to Role C.

**One night at a time.** While a night is running for a student, a second message from her waits. Different chats may run at the same time.

## The seam: the night summary

`run_night(workspace, date, message, ask=None)` returns a dict. **Every key is always present.**

- `week`: the ISO week of the night.
- `payslip_day`: `true` or `false`.
- `steps`: a list in run order. Each item has `step`, `name`, `agent`, `status` (`done`, `failed` or `skipped`) and `note`.
- `figures`: `hourly_rate_rm`, `take_home_rm` and `hours_total`, copied as text from `numbers.json`. Empty text when there is no value.
- `payslip`: the workspace path of the payslip, or empty text.
- `drafts`: a list. Each item has `number` and `file`.
- `review`: the review list as a list of lines.
- `failed`: empty, or a dict with `step` and `reason`.

`workspace` is the path of one student's folder. `date` is `YYYY-MM-DD`. `message` is the student's text. `ask` is the scripted model hook used by tests; the bot does not pass it.

While `app/runner.py` is not in `dev`, build against a stand in `run_night` that returns this shape with every key present. **Keep the stand in inside the tests, never in the product code.**

For `payslip` and `review` the bot only reads: the payslip file, `numbers.json`, and the output of the `review` command. Nothing changes the ledger or the plan except a night started through `run_night`.

## What is already built

- `app/bot.py`: standard library Telegram transport and bot routing. Workspace creation, upload saving, fixed commands, approval file moves, night reporting, one night at a time per chat, a polling loop, and safe error handling that never stringifies exceptions or leaks the token.
- `app/tests/test_bot.py`: offline contract tests with a fake Telegram and an injected runner stand in.
- `app/tests/test_bot_transport.py`: offline transport tests for the HTTPS calls, token loading, error sanitising and polling.

## Status at 02:55 on 11 October

- Committed as `4d13715` on `dev-damian`, then merged `dev` into the branch as `c8dca0d`.
- The merge brought in **Sharon's tool layer**: `app/tools.py` and `app/tests/test_tool_layer.py`, plus a small SYSTEM_DESIGN clarification about `input_file` and what `run_tool` returns for `lembur`. **The bot to runner seam did not change**: `run_night(workspace, date, message, ask=None)` and the night summary are as written above.
- The package 3 tests were rerun after the merge: 70 run, 60 passed, 10 skipped, no failures. The merge did not break this package.
- The local `.env` now exists and the token is configured. It was checked live against Telegram: the token authenticates and the API is reachable, and the bot is `lembur_damian_bot`. No token value was printed, logged or committed.
- `app/runner.py` still does not exist, so **proof 3 cannot pass yet**. Its photo half can be checked live; its payslip half needs a night to have produced a payslip.
- **Proof 3 partial result, recorded under the proof in PLAN section 12.** The bot was run against Telegram and a photo sent from the phone arrived correctly: `workspaces/998236319/` was created, the four baseline plan files were copied into its `plan/`, the other six folders were made, and the upload was saved to `inbox/` as `photo_20261011_064620_3.jpg`, a valid 252,087 byte JPEG. The photo half of the pass condition is met. The payslip half is not, because no night has run. The proof is recorded as partial, not a pass.

## What is verified and what is not

- **Verified offline**: `python -B -m unittest discover -s app/tests -p "test_bot*.py"` ran 70 tests on 11 October 2026: 60 passed, 10 skipped, no failures or errors. The skips are symlink and junction cases: this Windows filesystem does not expose real symbolic links without extra privilege. They are skipped with a clear reason, not silently ignored. The passing tests cover routing, upload naming and collisions, approval moves, summary formatting, chat isolation, queueing, the HTTPS transport calls, token loading and error sanitising.
- **Not verified**: the live behaviour. **Proof 3 has not been run.** No real bot, no token and no real `app/runner.py` exist yet. Everything about the live Telegram round trip is still a claim, not evidence.
- **Not verified on a filesystem with real symlinks**: the isolation checks are written but skipped here. Run them on a machine where symlinks work before treating that part as proven.
- **Not built by this package**: the runner, the model module, the tool layer and the prompts.

## Blockers before proof 3

1. **No `app/runner.py`.** The bot needs the real `run_night` for a full night, and proof 3 needs a payslip to exist before it can arrive in the chat. Fixed commands and uploads work without it.
2. **The photo half needs a person at the phone.** Someone must send the bot a text and a photo, then the word `payslip`. An agent cannot send Telegram messages as the student.
3. **The token is now configured.** This blocker is cleared; the live token check passed.
1. **No `.env`.** The token is not configured locally. Someone must create the bot with `@BotFather` and save the token as `TELEGRAM_BOT_TOKEN` in `D:\Github\Lembur\.env`. Never paste the token into chat, a file, a screenshot or a commit.
2. **No `app/runner.py`.** The bot needs the real `run_night` for a full night. Fixed commands and uploads work without it.
3. **Backend not in `dev`.** `app/tools.py` and `app/model.py` are another package's work.

## Proof 3, as written in PLAN section 12

- **Why**: the chat is the whole interface.
- **Steps**: create a bot with `@BotFather`. Put its token in `.env`. Send the bot a text and a photo, then the word `payslip`.
- **Pass when**: the photo is in the inbox of that chat's workspace, and the payslip file arrives in the chat.
- **Fallback**: run the night from the command line and show the files.
- **Owner**: Damian.
- Write the result under the proof in this shape: `**Result, <date> <time>, <name>**: pass, fail or fallback taken. What was done. What happened.`

## Rules the next agent must keep

- Work on `dev-damian`. Pull `origin/dev` first and before every pull request. Target `dev`, never `main`.
- Small, clear commits. No attribution lines. No mention of any tool or assistant in the code, comments or commits.
- Install nothing. Standard library only.
- Stay inside `app/bot.py` and `app/tests/`. Do not edit `tools/`, the docs (except the proof result), `app/model.py`, `app/tools.py`, `app/runner.py` or `prompts/`.
- Never print, log or commit the token. `.env` stays out of git.
- Do not stage anything under `.workbuddy-ai/` or any generated report.
- Demo data only. No real receipts, bank statements or personal details.
- If something is missing or contradictory, stop and ask Law. Do not guess.

## Suggested next steps, in order

1. Rerun the offline tests and confirm they pass. They currently pass: 70 run, 60 passed, 10 skipped for missing symlink support. Fix only `app/bot.py` if a later run fails.
2. Create the bot with `@BotFather` and save the token to `.env` (never share it).
3. Capture screenshots of the build session for the evidence pack, with credentials hidden.
4. Commit `app/bot.py` and its tests, pull `origin/dev`, push `dev-damian` and open a pull request into `dev`.
5. When `app/runner.py` is available and the token is saved, run proof 3 and write the result under the proof.
6. Report any seam that does not fit to Law before changing code.

## Environment notes

- Managed Python: `C:\Users\Damian\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe`.
- Run the offline tests from the repository root:
  `python -B -m unittest discover -s app/tests -p "test_bot*.py"`
- The full tool suite is separate:
  `python -B -m unittest discover -s tools/tests -p "test_*.py"`
- One workspace per student lives in `workspaces/<chat_id>/`, which git ignores. Tests and the demo replay use `workspace/`.
