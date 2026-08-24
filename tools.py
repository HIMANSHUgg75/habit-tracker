"""Habit tracking tools + streak logic. No LLM here on purpose."""

import json
import os
from datetime import date, datetime, timedelta

HABITS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "habits.json")
DATE_FMT = "%Y-%m-%d"


# ---------- persistence ----------

def _load():
    """Read habits.json. Creates it on first-ever run."""
    if not os.path.exists(HABITS_FILE):
        _save({})
        return {}
    try:
        with open(HABITS_FILE, "r") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data):
    with open(HABITS_FILE, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


# ---------- helpers ----------

def _clean_name(name):
    if not isinstance(name, str) or not name.strip():
        return None
    return name.strip().lower()


def _today():
    return date.today()


def _parse(d):
    return datetime.strptime(d, DATE_FMT).date()


def current_streak(dates):
    """Consecutive calendar days ending today or yesterday. 0 if broken."""
    if not dates:
        return 0
    days = sorted({_parse(d) for d in dates}, reverse=True)
    today = _today()
    gap = (today - days[0]).days
    if gap > 1:
        return 0  # broken: last log is older than yesterday
    streak = 1
    for prev, nxt in zip(days, days[1:]):
        if (prev - nxt).days == 1:
            streak += 1
        else:
            break
    return streak


def tier_for(streak):
    """Tier computed in code; the LLM phrases it."""
    if streak <= 0:
        return "restart"
    if streak <= 2:
        return "started"
    if streak <= 6:
        return "momentum"
    return "strong"


TIER_HINTS = {
    "restart": "gentle restart nudge, no guilt",
    "started": "you started, keep going",
    "momentum": "building momentum",
    "strong": "strong streak, protect it",
}


# ---------- the two real tools ----------

def log_habit(name):
    """Record today's date for a habit. Same-day logs are deduped."""
    key = _clean_name(name)
    if key is None:
        return {"ok": False, "error": "Habit name is empty. Give me a name like 'meditate'."}

    data = _load()
    today = _today().strftime(DATE_FMT)
    dates = data.get(key, [])
    already = today in dates
    if not already:
        dates.append(today)
        data[key] = sorted(set(dates))
        _save(data)

    streak = current_streak(data.get(key, dates))
    return {
        "ok": True,
        "habit": key,
        "date": today,
        "already_logged_today": already,
        "streak": streak,
        "tier": tier_for(streak),
        "message": ("Already logged today, streak unchanged."
                    if already else "Logged for today."),
    }


def get_streak(name):
    """Current streak for a habit, or a safe 'no record' response."""
    key = _clean_name(name)
    if key is None:
        return {"ok": False, "error": "Habit name is empty."}

    data = _load()
    if key not in data or not data[key]:
        return {"ok": True, "habit": key, "exists": False, "streak": 0,
                "tier": "restart", "message": "No record yet for this habit.",
                "known_habits": sorted(data.keys())}

    dates = sorted(set(data[key]))
    streak = current_streak(dates)
    return {
        "ok": True,
        "habit": key,
        "exists": True,
        "streak": streak,
        "active": streak > 0,
        "tier": tier_for(streak),
        "last_logged": dates[-1],
        "total_days": len(dates),
    }


def most_consistent():
    """Scan all habits, return the one with the longest current streak."""
    data = _load()
    if not data:
        return {"ok": True, "habits": [], "message": "No habits tracked yet."}
    rows = [{"habit": h, "streak": current_streak(d), "total_days": len(set(d))}
            for h, d in data.items()]
    rows.sort(key=lambda r: (-r["streak"], -r["total_days"], r["habit"]))
    best = rows[0]
    return {"ok": True, "best": best["habit"], "streak": best["streak"],
            "tier": tier_for(best["streak"]), "habits": rows}


# ---------- demo seeding ----------

def seed_demo_data():
    """Seed 7 days of 'meditate' and 3 of 'read' (both ending yesterday), plus a broken 'gym'."""
    today = _today()
    data = {
        "meditate": [(today - timedelta(days=i)).strftime(DATE_FMT) for i in range(1, 8)],
        "read": [(today - timedelta(days=i)).strftime(DATE_FMT) for i in range(1, 4)],
        "gym": [(today - timedelta(days=i)).strftime(DATE_FMT) for i in range(5, 9)],
    }
    for k in data:
        data[k] = sorted(data[k])
    _save(data)
    return data


def reset_memory():
    _save({})
    return {}


TOOL_REGISTRY = {
    "log_habit": log_habit,
    "get_streak": get_streak,
    "most_consistent": most_consistent,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "log_habit",
            "description": "Record that the user did a habit today. Deduped per calendar day. Returns the new current streak and tier.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": "Habit name, e.g. meditate"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_streak",
            "description": "Get the current streak for a habit. Returns 'no record yet' if unknown.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "most_consistent",
            "description": "Scan all tracked habits and return the one with the longest current streak.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]
