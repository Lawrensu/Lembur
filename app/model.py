"""The only code that talks to a language model (docs/SYSTEM_DESIGN.md section 6.3).

One function, ask(role, messages, images=None), returns the model's text.
Standard library only. Settings come from the environment, loaded from .env.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROLES = {"reason": "LEMBUR_MODEL_REASON", "read": "LEMBUR_MODEL_READ"}
MAX_TOKENS = {"reason": 8000, "read": 1500}
ATTEMPTS = 3
TIMEOUT_SECONDS = 180


class ModelError(Exception):
    """The gateway could not give an answer. The message never holds the key."""


def load_env(path=None) -> None:
    """Read NAME=value lines from .env without overwriting what is already set."""
    path = Path(path) if path else ROOT / ".env"
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip())


def _setting(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ModelError("Set %s in the local .env file." % name)
    return value


def _with_images(messages: list, images: list) -> list:
    """Attach the images to the last user message as content parts."""
    messages = [dict(message) for message in messages]
    last = next((m for m in reversed(messages) if m.get("role") == "user"), None)
    if last is None:
        raise ModelError("An image needs a user message to go with.")
    parts = [{"type": "text", "text": str(last.get("content", ""))}]
    for image in images:
        path = Path(image)
        kind = mimetypes.guess_type(path.name)[0] or "image/png"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        parts.append({"type": "image_url",
                      "image_url": {"url": "data:%s;base64,%s" % (kind, data)}})
    last["content"] = parts
    return messages


def _post(url: str, key: str, model: str, body: dict):
    request = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json", "x-user-id": key, "x-model": model})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace")
    except Exception as error:  # network trouble; the name is safe to report
        return 0, type(error).__name__


def ask(role: str, messages: list, images=None) -> str:
    """Return the model's text for one request. Raises ModelError after the retries."""
    if role not in ROLES:
        raise ModelError("Unknown role %r; use reason or read." % (role,))
    if images and role != "read":
        raise ModelError("Images go to the read role only.")
    load_env()
    url = _setting("LEMBUR_GATEWAY_URL")
    key = _setting("LEMBUR_GATEWAY_KEY")
    model = _setting(ROLES[role])
    body = {
        "messages": _with_images(messages, images) if images else messages,
        "temperature": 0,
        "max_tokens": int(os.environ.get("LEMBUR_MAX_TOKENS", MAX_TOKENS[role])),
    }

    reason = "no answer"
    for attempt in range(ATTEMPTS):
        if attempt:
            time.sleep(2 * attempt)
        status, text = _post(url, key, model, body)
        if status != 200:
            reason = "the gateway answered with status %s" % status
            continue
        try:
            reply = json.loads(text)
        except ValueError:
            reason = "the gateway did not answer with JSON"
            continue
        message = reply.get("message") if isinstance(reply, dict) else None
        if isinstance(message, str) and message.strip():
            return message
        reason = "the model gave an empty answer (%s)" % (
            reply.get("finishReason", "no reason given") if isinstance(reply, dict) else "bad reply")
    raise ModelError("The %s model failed: %s." % (role, reason))
