# import json
# import os
# from datetime import date , datetime , timedelta


# HABITS_FILE = os.path.join(os.path.dirname(os.path.abspath)(__file__)), "habits.json")
# DATE_FMP = "%Y-%m-%d"



# what this does:

# json and os let us read'write files on disk
# date and datetime are used to word with dates cleanly
# HABITS_FILE = points to the actual data file
# DATE_FMT = %Y-%m-%d" means dates are stored in a consistent format
# like.
# # 2026-08-24
# 2026-08-24
# 2026-08-25




# # if the project is habit-tracker then HABITS_FILE becomes soemthing like:


# # 2)

# # persistense: load and save

# def _load():
#     """reads habits.json. creates it on first-ever run"""
#     if not os.path.exists(HABITS_FILE):
#         _save({})
#         return {}
#     try:
#         with open(HABITS_FILE,"r") as f:
#             data = json.load(f)
#             return data if isinstance(data , dict) else {}
#     except (json.JSONDecodeError, OSError):
#         return {}


# def _save(data):
#     with open(HABITS_FILE , "w") as f:
#         json.dumps(data , f , indent = 2 , sort_keys= True)


# what this does-> 

# # _load() -> opens the JSON file and reads it
# # if the file does not exists , it creats the empty {}
# # if the JSON is broken or unreadable , it safaly returns {} instead of crashing
# #_save() writes the data back to disk in a neatly formatted JSON




# # real examples --> suppose the file looks like this 

# {
#     "meditate:": ["2026-08-20", "2026-08-21", "2026-08-22"]
# }



# # then  _load() would return a python dictionary:

# {
#     "meditate": ["2026-08-20", "2026-08-21", "2026-08-22"]
# }



