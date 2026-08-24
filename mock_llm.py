"""Offline stand-in for the GitHub Models client so the loop runs without GITHUB_TOKEN.

Same interface as the OpenAI SDK: client.chat.completions.create(...) -> choices[0].message
with .content and .tool_calls. It plans like the real model would: log -> get_streak -> speak.
"""

import json
import re
import uuid

from tools import TIER_HINTS

LOG_WORDS = r"(did|done|finished|completed|logged|log|went to|i)\b"
KNOWN_VERBS = ["meditate", "meditated", "gym", "read", "run", "ran", "journal", "walk", "study"]
STEM = {"meditated": "meditate", "ran": "run", "read": "read"}


class _Fn:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class _Call:
    def __init__(self, name, args):
        self.id = f"call_{uuid.uuid4().hex[:8]}"
        self.type = "function"
        self.function = _Fn(name, json.dumps(args))


class _Msg:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls


class _Choice:
    def __init__(self, message):
        self.message = message


class _Resp:
    def __init__(self, message):
        self.choices = [_Choice(message)]


def _extract_habit(text):
    t = text.lower()
    for w in KNOWN_VERBS:
        if w in t:
            return STEM.get(w, w)
    m = re.search(r"(?:habit|streak|for|my)\s+['\"]?([a-z][a-z ]{1,20})['\"]?", t)
    return m.group(1).strip() if m else ""


def _phrase(habit, streak, tier, extra=""):
    hint = TIER_HINTS.get(tier, "")
    if tier == "restart":
        return f"No streak on {habit} right now - {hint}. Do it today and we're back at day 1. {extra}".strip()
    return f"{habit}: {streak} day streak - {hint}. {extra}".strip()


class _Completions:
    def create(self, model=None, messages=None, tools=None, temperature=None, **kw):
        goal = next((m["content"] for m in messages if m["role"] == "user"), "")
        tool_msgs = [m for m in messages if m["role"] == "tool"]
        called = [c["function"]["name"]
                  for msg in messages if msg["role"] == "assistant" and msg.get("tool_calls")
                  for c in msg["tool_calls"]]
        low = goal.lower()
        habit = _extract_habit(goal)

        # --- consistency / summary question ---
        if any(k in low for k in ["most consistent", "which habit", "summary", "longest"]):
            if "most_consistent" not in called:
                return _Resp(_Msg(tool_calls=[_Call("most_consistent", {})]))
            r = json.loads(tool_msgs[-1]["content"])
            if not r.get("habits"):
                return _Resp(_Msg(content="Nothing tracked yet - name one habit and I'll start it today."))
            rows = ", ".join(f"{h['habit']} {h['streak']}d" for h in r["habits"])
            return _Resp(_Msg(content=_phrase(r["best"], r["streak"], r["tier"], f"(all: {rows})")))

        # --- pure streak question ---
        asking = any(k in low for k in ["streak", "how am i", "how many days"]) and \
            not re.search(r"\b(did|done|log|logged|completed|finished|went)\b", low)
        if asking:
            if "get_streak" not in called:
                return _Resp(_Msg(tool_calls=[_Call("get_streak", {"name": habit})]))
            r = json.loads(tool_msgs[-1]["content"])
            if not r.get("exists", False):
                return _Resp(_Msg(content=f"No record yet for '{r.get('habit', habit)}'. Want to log it today?"))
            return _Resp(_Msg(content=_phrase(r["habit"], r["streak"], r["tier"])))

        # --- log flow: log_habit -> get_streak -> speak ---
        if "log_habit" not in called:
            return _Resp(_Msg(tool_calls=[_Call("log_habit", {"name": habit})]))
        if "get_streak" not in called:
            logged = json.loads(tool_msgs[0]["content"])
            if not logged.get("ok"):
                return _Resp(_Msg(content="I need a habit name - try 'I meditated today'."))
            return _Resp(_Msg(tool_calls=[_Call("get_streak", {"name": logged["habit"]})]))
        r = json.loads(tool_msgs[-1]["content"])
        logged = json.loads(tool_msgs[0]["content"])
        extra = "Already counted for today." if logged.get("already_logged_today") else ""
        return _Resp(_Msg(content=_phrase(r["habit"], r["streak"], r["tier"], extra)))


class _Chat:
    def __init__(self):
        self.completions = _Completions()


class MockLLM:
    """Drop-in offline client. Swapped out automatically once GITHUB_TOKEN is set."""

    def __init__(self):
        self.chat = _Chat()
