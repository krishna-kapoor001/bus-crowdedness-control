import csv
import re

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

def clean_stop_name(name):
    s = name.strip()
    # Replace Metro Station / Stn
    s = re.sub(r'\bMetro\s+Station\b', 'Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'\bMetro\s+Stn\b', 'Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'\(Metro\s+Station\)', 'Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'\(Metro\)', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bMetro\b', 'Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

metro_left = []
for r in gtfs:
    c = clean_stop_name(r['stop_name'])
    if 'metro' in c.lower():
        metro_left.append((r['stop_name'], c))

print(f"Remaining metro names count: {len(metro_left)}")
for m in metro_left:
    print("  Original:", m[0], "--> Cleaned:", m[1])
