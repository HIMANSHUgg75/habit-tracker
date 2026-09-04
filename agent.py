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
but phrase the message yourself. Tool output also has "longest_streak" (the habit's all-time
best) -- mention it alongside the current streak, and call it out when the user is matching
or beating their personal best ("at_personal_best": true). Never invent habit names or streak
numbers -- only use what the tools returned. If a habit has no record, say so and offer to
start it today.
Keep replies under 45 words.
"""


def _client():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return None
    try:
        from openai import OpenAI
    except ModuleNotFoundError:
        print("[warning] openai is not installed; using offline mock.")
        return None
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
        try:
            resp = client.chat.completions.create(
                model=MODEL, messages=messages, tools=TOOL_SCHEMAS, temperature=0.4
            )
        except Exception as exc:
            if isinstance(client, MockLLM):
                raise
            print(f"[warning] Model unavailable ({exc}); using offline mock.")
            client = MockLLM()
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

# the file is the agent/brain layer that sits on top of the habit-tracking code we showed earlier

# the previous file for responsible for storing and calculating habits.

# the file is responsible for talking to the LLM , dec deciding which tool to call , executing it and giving the result back to the LLM.
# orchestrates the plan-act loop ties the LLM , tools , and habitslogic together.

# implements the coaching systems prompt and error 



# implement the coaching system prompt  and error handling for dispatch

# the fallback to MockLLM means offline demos even without


# user -> Agent -> LLM decides what to do -> Tools ( log_habits / get_streak / most_consistent) 


# -> Results -> LLM sees result -> final result -> final response to the user

# import json 
# import os 

# from tools import TOOL_REGISTRY , TOOL_SHEMAS , TIER_HINTS 

# from mock_llm import MOCKLLM 


# from mocl_llm import MockLLM

# import json

# Used to word with JSON 

# this is needed the LLM gives given , the LLM gives tools LLM  


# from mock_llm import MockLLM

# import json  used to work with JSON.


# this is needed beacuse the llm gives toool arguenents in JSSON form.


# import json
# used to word with JSON 

# This is needed  because the LLM given tools  arguments in JSON forms
# for examples:

# {"name"} -> "mediated"

# your python code needs to turn that into a python dictionary.



# import os

# used to access envirornt variable-> 


# os.evirorn.get("GITHUB_TOKEN")


# gets your GITHUB token from the envirornment 

# these import:

# from tools TOOL_REGISTRY , TOOL_SCHEMA , TIER_HINTS


# come from your previous file

# Remember 
# TOOL_ REGISTRY 

# connect ->

# "log_habits" -> log_habits()
# "get_stream" -> get_stream()
# "most_consistent" -> most_consistent()


# TOOLS_SCHEMA tells the LLM:

# what tools exists and what and what arguement. they accepts


# TIER_HINT contains messsages such as:

# contain ->  contain message such as:


# restart -> gets restart nudge started 


#started -> you started , keep going 
#momentum -> builing momentum 
# strong -> streak , protect it

# MOCKLLM 
# from mock_llm import MockLLM 
# this iis yout offline backup LLM
# if github
#  Models isn't  available, your programme can your, 

# github models cofiguration:

# BASE_URL = 'http://models.github.ai/inferece'


# this tells the OPen AI client:


# intead of talking to OPenAI''s normal API , communicate with GitHub Model' 

# inferrence endpoint


