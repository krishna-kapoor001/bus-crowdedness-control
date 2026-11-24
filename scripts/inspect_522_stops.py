import json

with open("data/corridors_routed.json", "r", encoding="utf-8") as f:
    corr = json.load(f)

for item in corr:
    print(f"ID: {item.get('id'):<25} | Name: {item.get('name', ''):<30} | Stops: {len(item.get('stops', []))} | Pts: {len(item.get('coordinates', []))}")
