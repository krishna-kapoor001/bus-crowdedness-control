import csv
from collections import Counter

with open('delhi_bus_stands_coordinates.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print(f"Total Bus Stands in CSV: {len(rows)}")
cat_counts = Counter(r['category'] for r in rows)
for cat, cnt in cat_counts.items():
    print(f"  {cat}: {cnt}")

print("\nFirst 10 records:")
for r in rows[:10]:
    print(f"  #{r['stand_id']} | {r['bus_stand_name']} | {r['latitude']}, {r['longitude']} | {r['category']}")
