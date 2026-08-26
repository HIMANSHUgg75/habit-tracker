# Habit Streak Tracker

The agent provides two required tools: `log_habit(name)` records today's date and returns the current streak, while `get_streak(name)` reads the saved history and returns the current streak, all-time best, and status. The bonus `most_consistent()` compares all habits. `agent.py` runs a plan-act loop: the model selects a tool, the dispatcher executes it, the result is returned to the model, and the model continues until it replies.

Memory is stored in `habits.json` as `{habit_name: [ISO dates]}`. It is loaded for every tool call, so data survives restarts. The first implementation counted duplicate logs on the same day as separate progress; this inflated streaks. The fix treats the calendar date as the unit of truth, deduplicates dates, and returns `already_logged_today` so the agent reports that the log was already counted.

Group contribution: solo submission; the project code, tools, agent loop, persistence, and notebook demo were implemented together. Run `python agent.py` for the offline demo, or set `GITHUB_TOKEN` to use GitHub Models.
