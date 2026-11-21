import csv
from collections import defaultdict

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

name_counts = defaultdict(int)
named_stops = []

for r in gtfs:
    base_name = r['stop_name'].strip()
    name_counts[base_name] += 1
    cnt = name_counts[base_name]
    if cnt == 1:
        full_name = base_name
    else:
        full_name = f"{base_name} (Platform {cnt})"
    named_stops.append((full_name, float(r['stop_lat']), float(r['stop_lon'])))

print(f"Total processed stops: {len(named_stops)}")
unique_names = set(s[0] for s in named_stops)
print(f"Total unique names: {len(unique_names)} (Must equal {len(named_stops)})")
assert len(unique_names) == len(named_stops)
print("Sample multi-platform names:")
for s in named_stops:
    if "Platform" in s[0]:
        print("  ", s)
        break
