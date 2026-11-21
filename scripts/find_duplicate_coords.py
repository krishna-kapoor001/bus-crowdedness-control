import json
from collections import Counter

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

coords = [(round(s['latitude'], 4), round(s['longitude'], 4)) for s in stops]
counts = Counter(coords)

duplicates = {c: cnt for c, cnt in counts.items() if cnt > 1}
print(f"Total stops: {len(stops)}")
print(f"Unique coordinates: {len(counts)}")
print(f"Coordinates shared by >1 stop: {len(duplicates)}")
print("\nTop shared coordinates:")
for c, cnt in sorted(duplicates.items(), key=lambda x: -x[1])[:15]:
    matching_stops = [s['name'] for s in stops if (round(s['latitude'], 4), round(s['longitude'], 4)) == c]
    print(f"  {c} ({cnt} stops): {matching_stops}")
