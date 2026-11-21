import csv
import json
import re
from difflib import SequenceMatcher

def clean_name(s):
    if not s:
        return ""
    s = s.lower().strip()
    s = re.sub(r'[/\\()\-.,_]', ' ', s)
    s = re.sub(r'\b(bus stand|bus stop|stand|stop|terminal|isbt|metro station|station|depot|crossing|more|chowk|gate|village|road)\b', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Load GTFS stops
gtfs_stops = []
with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            lat = float(row['stop_lat'])
            lon = float(row['stop_lon'])
            # Delhi NCT bounds: 28.38 to 28.88 lat, 76.84 to 77.38 lon
            if 28.35 <= lat <= 28.92 and 76.80 <= lon <= 77.40:
                name = row['stop_name'].strip()
                gtfs_stops.append({
                    'id': row['stop_id'],
                    'code': row['stop_code'],
                    'name': name,
                    'clean': clean_name(name),
                    'lat': lat,
                    'lon': lon
                })
        except Exception:
            continue

print(f"Loaded {len(gtfs_stops)} valid Delhi GTFS stops.")

# Load our 349 stop names
with open('data/all_stop_names.txt', 'r', encoding='utf-8') as f:
    our_stops = [line.strip() for line in f if line.strip()]

print(f"Loaded {len(our_stops)} stops from all_stop_names.txt.")

matched = 0
unmatched = []

for stop in our_stops:
    s_clean = clean_name(stop)
    best_match = None
    best_score = 0.0

    # 1. Exact match (case insensitive)
    for g in gtfs_stops:
        if stop.lower() == g['name'].lower():
            best_match = g
            best_score = 1.0
            break
    
    # 2. Exact cleaned match
    if not best_match and s_clean:
        for g in gtfs_stops:
            if s_clean == g['clean']:
                best_match = g
                best_score = 0.99
                break

    # 3. Substring match
    if not best_match and s_clean:
        for g in gtfs_stops:
            if s_clean in g['clean'] or g['clean'] in s_clean:
                score = similar(s_clean, g['clean'])
                if score > best_score:
                    best_score = score
                    best_match = g

    # 4. Fuzzy similarity
    if not best_match or best_score < 0.75:
        for g in gtfs_stops:
            score = similar(s_clean, g['clean'])
            if score > best_score:
                best_score = score
                best_match = g

    if best_match and best_score >= 0.7:
        matched += 1
    else:
        unmatched.append((stop, best_match['name'] if best_match else "None", best_score))

print(f"Matched {matched} / {len(our_stops)} ({matched/len(our_stops)*100:.1f}%)")
print(f"Unmatched count: {len(unmatched)}")
if unmatched[:15]:
    print("Sample unmatched / low score:")
    for u in unmatched[:15]:
        print(f"  '{u[0]}' -> best guess '{u[1]}' (score: {u[2]:.2f})")
