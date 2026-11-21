import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

airport_stops = ["Dhaula Kuan", "Satya Niketan", "Mahipal Pur", "Mahipal Pur Village", "Kapashera Border"]

print("Airport corridor stops:")
for s_name in airport_stops:
    found = [s for s in stops if s['name'].lower() == s_name.lower()]
    if found:
        s = found[0]
        print(f"  {s['name']}: lat={s['latitude']}, lon={s['longitude']}")
    else:
        print(f"  NOT FOUND: {s_name}")
