import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

hubs = [s for s in stops if s.get('is_major_hub', False)]

print(f"Total Major Bus Stands / Hubs: {len(hubs)}")
print("=" * 80)
print(f"{'#':<3} {'Hub Name':<38} {'Lat':<10} {'Lon':<10} {'Boardings':<10} {'Corridor'}")
print("=" * 80)

for i, h in enumerate(sorted(hubs, key=lambda x: x['monthly_boardings'], reverse=True)):
    print(f"{i+1:<3} {h['name']:<38} {h['latitude']:<10.6f} {h['longitude']:<10.6f} {h['monthly_boardings']:<10} {h.get('corridor', 'N/A')[:30]}")
