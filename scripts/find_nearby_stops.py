import json
import math

with open("data/stops_meta.json", "r", encoding="utf-8") as f:
    stops = json.load(f)

# Find all stops near Shahdara (28.674, 77.287)
print(f"Total stops in stops_meta.json: {len(stops)}")
near = []
for s in stops:
    lat = s['latitude']
    lon = s['longitude']
    dist = math.hypot(lat - 28.674, lon - 77.287)
    if dist < 0.03: # within ~3km
        near.append((dist, s))

near.sort(key=lambda x: x[0])
for d, s in near:
    print(f"Dist {d*111:.2f}km: {s['name']} -> ({s['latitude']}, {s['longitude']}), Hub: {s.get('corridor')}")
