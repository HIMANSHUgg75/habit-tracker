"""Plan-act loop over GitHub Models. Falls back to an offline mock when no GITHUB_TOKEN."""

import json
import os

from tools import TOOL_REGISTRY, TOOL_SCHEMAS, TIER_HINTS
from mock_llm import MockLLM

BASE_URL = "https://models.github.ai/inference"
MODEL = os.environ.get("MODEL_NAME", "openai/gpt-4o")
MAX_STEPS = 6

SYSTEM_PROMPT = f"""You are a habit-streak coach agent.

You have tools: log_habit(name), get_streak(name), most_consistent().

How to work:
1. If the user says they did a habit, call log_habit first.
2. Then call get_streak for that habit to confirm the real streak from memory.
3. Only then reply, with ONE short encouraging line chosen from the live streak number.

Encouragement tiers (you decide which one applies from the tool output):
- streak 0 or broken -> {TIER_HINTS['restart']}
- streak 1-2 -> {TIER_HINTS['started']}
- streak 3-6 -> {TIER_HINTS['momentum']}
- streak 7+ -> {TIER_HINTS['strong']}

The tool output also contains a "tier" field computed in code; use it as a sanity check
but phrase the message yourself. Never invent habit names or streak numbers -- only use
what the tools returned. If a habit has no record, say so and offer to start it today.
Keep replies under 35 words.
"""


def _client():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return None
    from openai import OpenAI
    return OpenAI(base_url=BASE_URL, api_key=token)


def dispatch(name, raw_args):
    """Validate tool name + parse JSON args defensively (models hallucinate both)."""
    if name not in TOOL_REGISTRY:
        return {"ok": False, "error": f"Unknown tool '{name}'. Available: {list(TOOL_REGISTRY)}"}
    try:
        args = json.loads(raw_args) if raw_args else {}
        if not isinstance(args, dict):
            raise ValueError("arguments must be a JSON object")
    except (json.JSONDecodeError, ValueError) as e:
        return {"ok": False, "error": f"Could not parse arguments for {name}: {e}"}

    fn = TOOL_REGISTRY[name]
    allowed = fn.__code__.co_varnames[: fn.__code__.co_argcount]
    args = {k: v for k, v in args.items() if k in allowed}
    try:
        return fn(**args)
    except TypeError as e:
        return {"ok": False, "error": f"Bad arguments for {name}: {e}"}


def run_agent(goal, verbose=True, client=None):
    """The plan-act loop: model -> tool_calls -> results -> model -> ... -> final text."""
    client = client or _client() or MockLLM()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": goal},
    ]
    trace = []
    if verbose:
        print(f"USER GOAL: {goal}")

    for step in range(1, MAX_STEPS + 1):
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SCHEMAS, temperature=0.4
        )
        msg = resp.choices[0].message
        calls = msg.tool_calls or []

        if not calls:
            final = (msg.content or "").strip()
            if verbose:
                print(f"[step {step}] FINAL: {final}\n")
            trace.append({"step": step, "type": "final", "content": final})
            return {"final": final, "trace": trace, "messages": messages}

        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {"id": c.id, "type": "function",
                 "function": {"name": c.function.name, "arguments": c.function.arguments}}
                for c in calls
            ],
        })

        for c in calls:
            result = dispatch(c.function.name, c.function.arguments)
            if verbose:
                print(f"[step {step}] TOOL {c.function.name}({c.function.arguments}) -> {result}")
            trace.append({"step": step, "type": "tool", "tool": c.function.name,
                          "args": c.function.arguments, "result": result})
            messages.append({"role": "tool", "tool_call_id": c.id,
                             "content": json.dumps(result, default=str)})

    return {"final": "Stopped: step limit reached.", "trace": trace, "messages": messages}


if __name__ == "__main__":
    run_agent("I meditated today")
    run_agent("Which habit am I most consistent with?")
