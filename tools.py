"""Habit tracking tools + streak logic. No LLM here on purpose."""

import json
import os
from datetime import date, datetime, timedelta

HABITS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "habits.json")
DATE_FMT = "%Y-%m-%d"

# This file is basically a tiny habit-tracker engine. It stores dates in habits.json, calculates streaks, and exposes a few tools that an LLM or app can call.

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
# if we move in past days in forward directions and we subtract current - past day and we get 1 then we  can  take that is in the streak.

def longest_streak(dates):
    """All-time best run of consecutive calendar days, anywhere in the history."""
    if not dates:
        return 0
    days = sorted({_parse(d) for d in dates})
    best = run = 1
    for prev, nxt in zip(days, days[1:]):
        run = run + 1 if (nxt - prev).days == 1 else 1
        best = max(best, run)
    return best


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

    stored = data.get(key, dates)
    streak = current_streak(stored)
    return {
        "ok": True,
        "habit": key,
        "date": today,
        "already_logged_today": already,
        "streak": streak,
        "longest_streak": longest_streak(stored),
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
                "longest_streak": 0, "tier": "restart",
                "message": "No record yet for this habit.",
                "known_habits": sorted(data.keys())}

    dates = sorted(set(data[key]))
    streak = current_streak(dates)
    return {
        "ok": True,
        "habit": key,
        "exists": True,
        "streak": streak,
        "longest_streak": longest_streak(dates),
        "at_personal_best": streak > 0 and streak == longest_streak(dates),
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
    rows = [{"habit": h, "streak": current_streak(d),
             "longest_streak": longest_streak(d), "total_days": len(set(d))}
            for h, d in data.items()]
    rows.sort(key=lambda r: (-r["streak"], -r["longest_streak"], r["habit"]))
    best = rows[0]
    # -r["steak"] -> largest current steak first
    # -r["longest_steak"] -> choose the better all-time steak
    # r["habit"] -> sort alphabetically
    # if still tied:
    # r["habit"]
    # sort alphabetically 
    

    # after sorting , the first item is the most consistent currently.

    
    all_time = max(rows, key=lambda r: (r["longest_streak"], r["total_days"]))
    return {"ok": True, "best": best["habit"], "streak": best["streak"],
            "longest_streak": best["longest_streak"],
            "all_time_best_habit": all_time["habit"],
            "all_time_best_streak": all_time["longest_streak"],
            "tier": tier_for(best["streak"]), "habits": rows}


# this finds the best habit in all history.
# priority:
# Longest all-time steak
# if tied, more total completed days
 


# ---------- demo seeding ----------

def seed_demo_data():
    """Seed 7 days of 'meditate' and 3 of 'read' (both ending yesterday), plus a broken 'gym'."""
    today = _today()
    # get today 

    data = {
        "meditate": [(today - timedelta(days=i)).strftime(DATE_FMT) for i in range(1, 8)],
        "read": [(today - timedelta(days=i)).strftime(DATE_FMT) for i in range(1, 4)]
                + [(today - timedelta(days=i)).strftime(DATE_FMT) for i in range(20, 26)],
        "gym": [(today - timedelta(days=i)).strftime(DATE_FMT) for i in range(5, 9)],
    }
    # this creates dates: 
    # yesterdays
    # 2 days ago
    # 7 days ago

    # so it creates a 7-day consecutive history ending yesterday.

    # read -> it crrates -> one recent 3-day streak
    # another older 6-day streak
    # this is useful for testing the difference betweeen:
    # current_streak

    # and longest_streak


    # gym -> 
    # range(5 , 9)
    # creates logs from 5-8 days ago
    # since the last log is older than yesterday

    # current_streak 
    # and longest_strek
     
    #  gym -> 
    # range(5 , 9)
    # creates logs from 5 - 8 days ago
    # current_streak = 0
    # so it tests a broken streak

    # _save(data) -> persist the demo date into habits.json


    for k in data:
        data[k] = sorted(data[k])
    _save(data)
    return data

# reset_memoy

def reset_memory():
    _save({})
    return {}
# this completely clears  all the habit data

# it saves JSON {}
# then returns an empty dictionary

TOOL_REGISTRY = {
    "log_habit": log_habit,
    "get_streak": get_streak,
    "most_consistent": most_consistent,
}
# gives you the function:
# log_habits
# so another part of your applications can dynamically call
# tool_name ="log_habits"
# functions = TOOL_REGISTRY[tool_name]
# result = function("mediate")

# this is especially useful when connecting these functions to an LLM tool-calling system


# this maps tool names as string to actual Python functions

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
            "description": "Get the current streak AND the all-time best (longest ever) streak for a habit. Returns 'no record yet' if unknown.",
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
            "description": "Scan all tracked habits and return the one with the longest current streak, plus each habit's current and all-time best streak.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


# this part is not the actual tool implementation.
# this actualy implementations is

# def logic_habit(name):
    # and the other functions:

# TOOL_SCHEMAS instead tells an LLM/API:

# what tools exist, what they do ,and and what arguements they need.

# for example:

# "name": "log_habits"
# tells the LLM the tool's name

# "descriptions" : Record that the user did a habit today..."

# explains when the LLM should use the tool

# "parameter":{
#     "type": "object",
# }

# # says the arguements will comes as object
 
# for example:
# {
#     "name": "meditate"
# }
# # says:
# # this tools aceepts a name , and it must be a string/

# "required": ["name"]

# means the LLM must provide name when calling the tool.

# the flow 
# supose user says -> 
# i meditated today 
# the LLM/applications could follow this flow:


# user -> "log meditate" 

# -> TOOL_SCHEMA tells LLM:
# log_habit requires {"name": string}

# -> LLM chooses:
# {"name": "mediate"}

# -> TOOL_REGISTRY finds: "log_habits" -> log_habits function

# -> log_habits("meditate")

# -> -clean_name()

# ->  _load() <- loads habits.json

# -> check if today already exists

# -> add today if necessary


#-> _save() <- PERSISTENCE 

# -> current_steak()

# -> longest_streak()

# current_streak()

# tier_for()

# -> Return result to LLM/app


# the mist important thing to understand is 

# _load() -> gets old saved() date
# _save() -> permanently saved data(persistence)
# log_habit() -> records today's habits
# current_streak() -> calculates the best streak ever
# longest_streak() -> calculates the best streak ever
# get_streak() -> only checks informations
# most_consistent() -> connected a tool name to Python code
# TOOL_SCHEMAS -> tells the LLM how to call those tools


# The whole file is essentially a small backend engine for habit tracking, with the JSON file acting as its tiny persistent database.


