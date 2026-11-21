import json

with open("data/processed/corridors_routed.json", "r", encoding="utf-8") as f:
    corridors = json.load(f)

print(f"Total corridors: {len(corridors)}")
for c in corridors[:5]:
    print(f"ID: {c.get('id')}, Name: {c.get('name')}")
    print(f"  Stops ({len(c.get('stops', []))}): {c.get('stops')}")
