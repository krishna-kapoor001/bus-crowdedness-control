import json
import math

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total stops in database: {len(stops)}")

# 1. Check coordinates
valid_coords = 0
invalid_coords = []
for s in stops:
    lat = s.get('latitude', 0)
    lon = s.get('longitude', 0)
    # Delhi NCT bounds: Lat [28.40, 28.88], Lon [76.84, 77.38]
    if 28.38 <= lat <= 28.92 and 76.80 <= lon <= 77.42:
        valid_coords += 1
    else:
        invalid_coords.append((s['name'], lat, lon))

print(f"Valid Delhi Coordinates: {valid_coords} / {len(stops)}")
if invalid_coords:
    print("Invalid coordinates:", invalid_coords)

# 2. Check duplicates
seen = {}
duplicates = []
for idx, s in enumerate(stops):
    key = s['name'].lower().strip()
    if key in seen:
        duplicates.append((s['name'], seen[key], idx))
    else:
        seen[key] = idx

print(f"Exact Duplicate Names: {len(duplicates)}")
for name, first_idx, dup_idx in duplicates:
    s1 = stops[first_idx]
    s2 = stops[dup_idx]
    dist_m = math.hypot((s1['latitude'] - s2['latitude']) * 111000, (s1['longitude'] - s2['longitude']) * 100000)
    print(f"  - '{name}' (Stop #{first_idx+1} vs #{dup_idx+1}) -> Distance: {dist_m:.1f} meters")

# 3. Major Hubs vs Regular Stops
hubs = [s for s in stops if s.get('is_major_hub')]
regular = [s for s in stops if not s.get('is_major_hub')]
print(f"Major Hubs (Black Dots): {len(hubs)}")
print(f"Regular Stops (Blue Dots): {len(regular)}")

# 4. Check Yamuna Vihar entries specifically
yv = [s for s in stops if 'yamuna' in s['name'].lower()]
print(f"\nYamuna Vihar related stops ({len(yv)}):")
for s in yv:
    print(f"  - {s['name']}: [{s['latitude']}, {s['longitude']}], is_hub={s.get('is_major_hub')}, corridor={s.get('corridor')}")
