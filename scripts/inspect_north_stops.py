import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total stops: {len(stops)}")
north_stops = [s for s in stops if s['latitude'] > 28.70]
print(f"North Delhi stops (lat > 28.70): {len(north_stops)}")
print("-" * 70)
for s in sorted(north_stops, key=lambda x: x['latitude'], reverse=True):
    print(f"{s['name']:<40}: ({s['latitude']:.5f}, {s['longitude']:.5f}) | Hub: {s.get('is_major_hub', False)}")
