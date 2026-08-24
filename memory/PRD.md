# Habit Streak Tracker — Agentic AI (CSE476 CA1)

## Problem statement
Minimal Python agent (notebook + .py) that keeps a user consistent on habits: logs habits,
computes real-date streaks, persists memory across sessions, and decides an encouraging
message from streak length. Solo scope, GitHub Models lane. Deliberately NO web/mobile stack.

## User choices (confirmed)
- Tier decision: BOTH (code helper `tier_for()` + tiers in system prompt so LLM chooses)
- Model: `openai/gpt-4o` via https://models.github.ai/inference
- No GITHUB_TOKEN yet -> offline MockLLM fallback built in
- No separate test_tools.py (edge cases proven in notebook)
- Seeded demo data in habits.json

## Architecture
- `tools.py` — log_habit, get_streak, most_consistent, current_streak, tier_for, JSON persistence, seed_demo_data
- `agent.py` — plan-act loop (`run_agent`), validated `dispatch()`, system prompt with tiers
- `mock_llm.py` — offline OpenAI-SDK-shaped client (log -> get_streak -> phrase)
- `habits.json` — persistent memory {habit: [ISO dates]}, auto-created
- `demo.ipynb` — 6 sections: seed, log, double-log, grow/broken, most_consistent, edge cases, persistence
- `README.md` — 3 paragraphs + viva pointer table

## Implemented (2026-06)
- Two real tools + bonus most_consistent, all verified
- Multi-step plan-act trace printed per step
- Edge cases verified: same-day dedupe, >1 day gap resets to 0, unknown habit "no record yet",
  blank name rejected, first-run file creation, hallucinated tool name, malformed JSON args, extra args stripped

## Backlog
- P1: run against real gpt-4o once GITHUB_TOKEN is added (only env change needed)
- P2: longest-ever streak (historical max) alongside current streak
- P2: weekly summary / reminder tiers
