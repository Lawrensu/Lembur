# Getting started

This doc gets Lembur running on your machine. Read it if you are a teammate, a judge or someone picking the project up later.

* **What Lembur is and how it works**: [System design](SYSTEM_DESIGN.md).
* **Back to the overview**: [README](../README.md).

## Requirements

* **Git**.
* **Python 3.12 or newer**: https://www.python.org/downloads/
* **Nothing else to install**: the whole product uses the standard library only.
* **Only to run the bot**: a Telegram account and a bot token from `@BotFather`.
* **Only to run with the real models**: the address and a key of the model gateway. The tests need neither.

## Install

```bash
git clone https://github.com/Lawrensu/Lembur.git
```

```bash
cd Lembur
```

* **No install step**: there is no package to add.
* **Run every command from the repository root**: the tools find the payslip template relative to it.

## Configure

* **Copy the example file and fill it in**: `.env` is ignored by git.

```bash
cp .env.example .env
```

* **`LEMBUR_GATEWAY_URL`**: the one HTTPS address of the model gateway.
* **`LEMBUR_GATEWAY_KEY`**: your gateway key.
* **`LEMBUR_MODEL_REASON`**: the model that drives the agents. The demo used `GPT-OSS 120B`.
* **`LEMBUR_MODEL_READ`**: the model that reads images. The demo used `Qwen 27B`.
* **`TELEGRAM_BOT_TOKEN`**: the token `@BotFather` gives you for your bot.
* **Never share a key or a token**: not in a file, a prompt, a log, a chat or a commit.

## Test

* **No key and no network needed**: the tests use a scripted model.
* **The deterministic tools**, 82 tests, about a minute.

```bash
python -B -m unittest discover -s tools/tests -p "test_*.py"
```

* **The tool layer, the runner and the bot**, 160 tests, about a minute.

```bash
python -B -m unittest discover -s app/tests -p "test_*.py"
```

## Run the bot

* **Start it**: it asks Telegram for new messages until you stop it with Ctrl+C.

```bash
python -B -m app.bot
```

* **In Telegram, open your bot and send** `/start`. It replies with a short welcome.
* **Send your files**: receipt photos, order screenshots or a bank statement. Each is saved to your inbox.
* **Send one message about your day**: that starts the night shift. The bot replies with your figures.
* **On a Sunday**: the same message also produces the payslip and the drafts.
* **Words the bot understands**: `payslip`, `review`, `approve N`, `skip N`, `help`. Anything else is tonight's message.
* **Where your files go**: `workspaces/<chat_id>/`, which git ignores.
* **To try the demo week in the chat**: send a day's files from `data/demo/inbox/`, then that day's message from `data/demo/messages.md` with its date in front, for example `2026-10-05 Two Instagram keychain orders today...`. The date makes the message run as that night.

## Replay the demo week

This runs the seven recorded nights with the real models and checks the result against the answer key. It needs the gateway settings in `.env`, not the bot token.

* **Empty the workspace and copy in the plan**.

```bash
python -B data/test_harness/reset_workspace.py --full
```

* **Replay the seven nights**, about five minutes.

```bash
python -B data/test_harness/replay_week.py
```

* **Compare the run with the answer key**: it prints PASS or FAIL with every difference.

```bash
python -B data/test_harness/compare_outputs.py
```

* **What to open afterwards**
  * `workspace/payslips/2026-W41.html`: the payslip.
  * `workspace/boardroom/2026-W41/`: the two recommendations and the ruling.
  * `workspace/audit/2026-W41/`: the plan for each night, the trace of every tool call and the audit report.
  * `workspace/approvals/2026-W41/`: the drafts waiting for approval.
* **If it prints FAIL**: the models do not answer the same way every time. Read the differences, then replay again. A mismatch that repeats is a bug.
* **Check the comparator itself**: this proves it catches eleven kinds of error. It works in a temporary folder.

```bash
python -B data/test_harness/mutation_test.py
```

## Run one tool by hand

* **Every figure comes from `tools/lembur.py`**: each command prints JSON and exits 0 on success, 1 on failure.

```bash
python -B tools/lembur.py review --workspace workspace --week 2026-W41
```

* **The full list of commands and their rules**: [System design, Deterministic Tools](SYSTEM_DESIGN.md#deterministic-tools).

## Team workflow

* **Branches**
  * `main`: only receives merges from `dev`.
  * `dev`: integration. It must run end to end before it goes to `main`.
  * `dev-<your name>`: your working branch. Pull `dev` often and open a pull request back into `dev`.
* **Change the design first, then the code**: [System design](SYSTEM_DESIGN.md) is the source of truth for behaviour and data.
* **Check before a pull request**: both test suites pass, and a replayed week prints PASS.
* **Repo rules**: listed in the [README](../README.md#repo-rules).
