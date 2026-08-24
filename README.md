# Habit Streak Tracker — Agentic AI (CSE476 CA1)

A tiny Python agent that keeps one person consistent on their habits. It exposes two real
tools — `log_habit(name)` records today's calendar date for a habit and returns the new
streak, and `get_streak(name)` reads the stored history back and reports the current streak,
the habit's all-time best (longest ever) streak, and whether it is active or broken (a third
bonus tool, `most_consistent()`, scans every habit and returns the one with the longest live
streak plus a current-vs-best table). The agent runs a plan-act loop in
`agent.py`: it sends the goal and the tool schemas to the model, detects `tool_calls`,
executes them through a validated dispatcher, appends the results as `tool` messages and
calls the model again — so "I meditated today" becomes `log_habit` → look at the result →
`get_streak` → then speak. Every step is printed, so the trace is visible.

Memory is a plain `habits.json` file of `{habit_name: [ISO dates]}`, auto-created on the
first run and re-read on every tool call, so it survives notebook restarts and is used in
later turns: asking "which habit am I most consistent with?" answers purely from dates
written on earlier turns. The encouragement message is agentic in two ways — the tiers
(0/broken → gentle restart, 1–2 → you started, 3–6 → momentum, 7+ → protect it) live in the
system prompt so the LLM picks one from the live streak number, and `tools.tier_for()`
computes the same tier in code as a sanity check the model can cross-reference. Nothing about
the reply is hardcoded per call; change the streak and the message changes. Edge cases are
handled in `tools.py`: same-day double logs are deduped by date, a gap of more than one
calendar day resets the streak to 0, unknown habits return "no record yet", blank names are
rejected, and `agent.dispatch()` validates the tool name and `json.loads` the arguments in a
try/except before executing anything.

**One honest failure.** The first version appended today's date on every `log_habit` call, so
telling the agent "I meditated" twice in one session pushed the streak from 3 to 5 — the
model happily read the inflated number back and congratulated a streak that never happened.
The fix was to make the date the unit of truth rather than the call: store dates in a sorted
`set`, check whether today is already present, and return `already_logged_today: true` so the
model says "already counted" instead of celebrating twice. A second, smaller failure came
from the model inventing habit names (`get_streak("meditation")` when the stored key was
`meditate`), which is why names are normalised (trimmed + lowercased) and unknown habits
return a safe "no record yet" payload that also lists the habits that do exist.

---

## Files
- `tools.py` — the tools, streak/date logic, JSON persistence, tier helper, demo seeding
- `agent.py` — plan-act loop, system prompt with the tiers, validated tool dispatch
- `mock_llm.py` — offline stand-in client so the loop runs before a token is added
- `habits.json` — persistent memory (auto-created, seeded for the demo)
- `demo.ipynb` — three goals with the full multi-step trace

## Run
```bash
pip install openai
export GITHUB_TOKEN=ghp_...        # PAT with models:read
python agent.py                     # or open demo.ipynb
```
Model: `openai/gpt-4o` via `https://models.github.ai/inference`.
Without `GITHUB_TOKEN` the loop runs against `MockLLM` (same interface, same trace) so the
tools and memory can be demoed offline; set the token and the real model takes over with no
code change.

## Viva pointers
| Question | Where |
|---|---|
| Plan-act loop decides next step | `agent.run_agent()` — the `for step` loop checking `msg.tool_calls` |
| One full tool call | user msg → `tool_calls` → `dispatch()` → `tool` message → re-call model |
| Memory read back later | `get_streak` / `most_consistent` → `tools._load()` reads `habits.json` |
| Why agentic, not a chatbot | multi-step from tool output + persistent reused memory |
| Encouragement is agentic | tier chosen from live streak (`tier_for` + tiers in system prompt) |
| Double-log same day | `log_habit` date dedupe → `already_logged_today` |
| Broken streak | `current_streak()` returns 0 if last log is older than yesterday |
| Unknown habit | `get_streak` returns `exists: false`, "no record yet" |
| Why JSON | transparent, zero setup, survives restart, enough for one user |
| Current vs all-time best streak | `tools.longest_streak()` scans full history; surfaced as `longest_streak` / `at_personal_best` |
