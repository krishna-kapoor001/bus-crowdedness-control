import json
import csv
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

# Import the high-precision geo-dictionary from fix_all_stop_coordinates
import sys
sys.path.append(os.path.join(BASE_DIR, 'scripts'))
from fix_all_stop_coordinates import LOCALITY_GEO

def clean_name(name: str) -> str:
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def get_category(name: str) -> str:
    name_low = name.lower()
    if 'isbt' in name_low:
        return 'Inter-State Bus Terminal (ISBT)'
    if 'terminal' in name_low or '(t)' in name_low:
        return 'Major Bus Terminal'
    if 'depot' in name_low:
        return 'Bus Depot & Terminal'
    if 'metro station' in name_low or 'metro' in name_low:
        return 'Metro Transit Bus Stand'
    if 'railway station' in name_low or 'railway' in name_low:
        return 'Railway Inter-Modal Bus Stand'
    return 'Bus Stand'

# 1. Load official stop profiles
stops_profile_file = os.path.join(PROCESSED_DIR, 'stop_profiles.json')
with open(stops_profile_file, 'r', encoding='utf-8') as f:
    profile_stops = json.load(f)

# 2. Load edge stops from transit graph
edges_file = os.path.join(PROCESSED_DIR, 'transit_graph_edges.json')
edge_stops = set()
if os.path.exists(edges_file):
    with open(edges_file, 'r', encoding='utf-8') as f:
        for e in json.load(f):
            edge_stops.add(e.get('start_stop', '').strip())
            edge_stops.add(e.get('end_stop', '').strip())

records = {}

# Priority 1: Ground-truth curated 349 stops
for s in profile_stops:
    raw_name = clean_name(s['name'])
    key = raw_name.lower()
    records[key] = {
        'name': raw_name,
        'latitude': round(float(s['latitude']), 6),
        'longitude': round(float(s['longitude']), 6),
        'corridor_locality': s.get('corridor', 'Delhi Transit Network'),
        'category': get_category(raw_name),
        'region': 'Delhi NCT'
    }

# Priority 2: All additional verified Delhi stops from transit network
sorted_localities = sorted(LOCALITY_GEO.items(), key=lambda x: len(x[0]), reverse=True)

for raw_name in sorted(edge_stops):
    if not raw_name:
        continue
    name = clean_name(raw_name)
    key = name.lower()
    if key in records:
        continue
    
    # Match locality
    for loc, (lat, lon, corr) in sorted_localities:
        if loc in key:
            # Strictly verify Delhi NCT bounding box
            if 28.38 <= lat <= 28.92 and 76.84 <= lon <= 77.40:
                records[key] = {
                    'name': name,
                    'latitude': round(float(lat), 6),
                    'longitude': round(float(lon), 6),
                    'corridor_locality': corr,
                    'category': get_category(name),
                    'region': 'Delhi NCT'
                }
            break

# Sort records: Major Terminals & ISBTs first, then alphabetical by name
def sort_key(item):
    cat_order = {
        'Inter-State Bus Terminal (ISBT)': 1,
        'Major Bus Terminal': 2,
        'Bus Depot & Terminal': 3,
        'Railway Inter-Modal Bus Stand': 4,
        'Metro Transit Bus Stand': 5,
        'Bus Stand': 6
    }
    return (cat_order.get(item['category'], 99), item['name'])

sorted_records = sorted(records.values(), key=sort_key)

# Add stand_id
for idx, r in enumerate(sorted_records, 1):
    r['stand_id'] = idx

# Output files
out_paths = [
    os.path.join(DATA_DIR, 'delhi_bus_stands_coordinates.csv'),
    os.path.join(BASE_DIR, 'delhi_bus_stands_coordinates.csv')
]

fieldnames = ['stand_id', 'bus_stand_name', 'latitude', 'longitude', 'category', 'corridor_locality', 'region']

for path in out_paths:
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in sorted_records:
            writer.writerow({
                'stand_id': r['stand_id'],
                'bus_stand_name': r['name'],
                'latitude': f"{r['latitude']:.6f}",
                'longitude': f"{r['longitude']:.6f}",
                'category': r['category'],
                'corridor_locality': r['corridor_locality'],
                'region': r['region']
            })
    print(f"Exported {len(sorted_records)} bus stands to: {path}")

print("\n--- Summary of Categories ---")
from collections import Counter
counts = Counter(r['category'] for r in sorted_records)
for cat, cnt in counts.items():
    print(f"  {cat}: {cnt}")
