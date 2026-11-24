import json

with open("data/processed/route_profiles.json", "r", encoding="utf-8") as f:
    profiles = json.load(f)
print("profiles[0]:", json.dumps(profiles[0], indent=2))
