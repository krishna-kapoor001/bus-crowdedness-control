import json

with open('data/stops_meta.json', encoding='utf-8') as f:
    stops = json.load(f)

# Corridors check:
# 1. NH-48 corridor (lat: 28.50 - 28.60, lon: 77.08 - 77.17)
# 2. Delhi-Meerut Expressway / NH-9 corridor (lat: 28.60 - 28.64, lon: 77.27 - 77.34)
# 3. Barapullah corridor (lat: 28.575 - 28.595, lon: 77.22 - 77.26)
# 4. DND Flyway (lat: 28.565 - 28.585, lon: 77.26 - 77.31)
# 5. Dwarka Expressway (lat: 28.52 - 28.56, lon: 77.02 - 77.08)

nh9_stops = [s for s in stops if 28.61 <= s['latitude'] <= 28.64 and 77.27 <= s['longitude'] <= 77.34]
nh48_stops = [s for s in stops if 28.52 <= s['latitude'] <= 28.56 and 77.08 <= s['longitude'] <= 77.13]
dnd_stops = [s for s in stops if 28.565 <= s['latitude'] <= 28.585 and 77.26 <= s['longitude'] <= 77.31]
barapullah_stops = [s for s in stops if 28.575 <= s['latitude'] <= 28.592 and 77.22 <= s['longitude'] <= 77.26]

print(f"NH-9 (Delhi-Meerut Exp) corridor stops: {len(nh9_stops)}")
for s in nh9_stops:
    print(f"  {s['name']}: ({s['latitude']}, {s['longitude']})")

print(f"\nNH-48 corridor stops: {len(nh48_stops)}")
for s in nh48_stops:
    print(f"  {s['name']}: ({s['latitude']}, {s['longitude']})")

print(f"\nDND corridor stops: {len(dnd_stops)}")
for s in dnd_stops:
    print(f"  {s['name']}: ({s['latitude']}, {s['longitude']})")

print(f"\nBarapullah corridor stops: {len(barapullah_stops)}")
for s in barapullah_stops:
    print(f"  {s['name']}: ({s['latitude']}, {s['longitude']})")
