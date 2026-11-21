import csv
import json
import re

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

with open('data/all_stop_names.txt', 'r', encoding='utf-8') as f:
    stops = [s.strip() for s in f if s.strip()]

print(f"Loaded {len(stops)} stops from all_stop_names.txt")
print(f"Loaded {len(gtfs)} GTFS stops")

# Let's inspect each stop and find best matches
perfect_matches = 0
manual_needed = []

for s in stops:
    s_clean = s.strip()
    s_low = s_clean.lower()
    
    # 1. Exact match
    exact = [g for g in gtfs if g['stop_name'].lower().strip() == s_low]
    if exact:
        perfect_matches += 1
        continue
    
    # 2. Normalized match (remove / () - .)
    norm_s = re.sub(r'[^a-z0-9]', '', s_low)
    norm_matches = [g for g in gtfs if re.sub(r'[^a-z0-9]', '', g['stop_name'].lower()) == norm_s]
    if norm_matches:
        perfect_matches += 1
        continue
        
    manual_needed.append(s)

print(f"Exact/Normalized matches: {perfect_matches} / {len(stops)}")
print(f"Stops needing precise lookup: {len(manual_needed)}")
print("\nFirst 30 needing lookup:")
for m in manual_needed[:30]:
    print(f"  '{m}'")
