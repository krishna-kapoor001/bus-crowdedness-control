import csv
from collections import Counter

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

names = [r['stop_name'].strip() for r in gtfs]
c = Counter(names)
multi = [item for item in c.items() if item[1] > 1]
print(f"Total names with multiple platforms: {len(multi)}")
print("Examples of multi-platform stops:")
for m in multi[:5]:
    matches = [r for r in gtfs if r['stop_name'].strip() == m[0]]
    print(f"  '{m[0]}' ({m[1]} poles):")
    for r in matches:
        print(f"     ID: {r['stop_id']}, lat={r['stop_lat']}, lon={r['stop_lon']}")
