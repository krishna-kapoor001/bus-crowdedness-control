import json
import math
import re
from collections import defaultdict

print("=" * 80)
print("  DEEP SCAN: DUPLICATES & EMPTY/UNWANTED ROAD AUDIT")
print("=" * 80)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def clean_name(s):
    clean = re.sub(r'[^a-zA-Z0-9]', ' ', s.lower())
    ignore = {'bus', 'stop', 'stand', 'terminal', 'crossing', 'xing', 'more', 'mor', 'road', 'marg', 'delhi', 'village', 'near', 'opp', 'opposite', 'depot', 'isbt', 'dtc', 'cluster', 'colony', 'block', 'phase', 'sec', 'sector', 'hub'}
    return [w for w in clean.split() if len(w) > 2 and w not in ignore]

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total catalog stops to audit: {len(stops)}")

# -------------------------------------------------------------
# PART 1: Spatial & Semantic Duplicate Check
# -------------------------------------------------------------
print("\n[PART 1] Detailed Duplicate Analysis across various radii:")

# 1. Check under 35m
pairs_under_35m = []
pairs_35_to_60m = []
pairs_60_to_100m_semantic = []

for i in range(len(stops)):
    s1 = stops[i]
    toks1 = set(clean_name(s1['name']))
    for j in range(i + 1, len(stops)):
        s2 = stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        toks2 = set(clean_name(s2['name']))
        
        if d < 35.0:
            pairs_under_35m.append((d, s1['name'], s2['name']))
        elif d < 60.0:
            overlap = toks1 & toks2
            pairs_35_to_60m.append((d, s1['name'], s2['name'], list(overlap)))
        elif d < 120.0:
            overlap = toks1 & toks2
            if overlap:
                pairs_60_to_100m_semantic.append((d, s1['name'], s2['name'], list(overlap)))

print(f"  • Stop pairs < 35m apart:                    {len(pairs_under_35m)}")
for d, n1, n2 in pairs_under_35m:
    print(f"    - {d:.1f}m: '{n1}' vs '{n2}'")

print(f"  • Stop pairs 35m–60m apart:                  {len(pairs_35_to_60m)}")
for d, n1, n2, ov in pairs_35_to_60m:
    print(f"    - {d:.1f}m: '{n1}' vs '{n2}' (shared tokens: {ov})")

print(f"  • Stop pairs 60m–120m with shared keywords:  {len(pairs_60_to_100m_semantic)}")
for d, n1, n2, ov in pairs_60_to_100m_semantic[:10]:
    print(f"    - {d:.1f}m: '{n1}' vs '{n2}' (shared: {ov})")

# -------------------------------------------------------------
# PART 2: Check Road Type & OSM Node Authenticity ("Khaali/Faltu Road")
# -------------------------------------------------------------
print("\n[PART 2] Road Type & Physical Bus Shelter Inspection:")

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_raw = json.load(f)

# Build map of OSM nodes
osm_map = []
for o in osm_raw:
    tags = o.get('tags', {})
    lat = o.get('latitude') or o.get('lat')
    lon = o.get('longitude') or o.get('lon')
    if isinstance(lat, list):
        lon, lat = lat[0], lat[1]
    if lat and lon and isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        osm_map.append({
            'name': o.get('name') or tags.get('name') or '',
            'lat': float(lat),
            'lon': float(lon),
            'tags': tags
        })

# For each stop in our catalog, find the exact OSM node it sits on
sheltered_count = 0
highway_bus_stop_count = 0
platform_count = 0
unknown_node_count = 0
low_demand_stops = []

for s in stops:
    # Find matching OSM node <= 1.0m
    best_o = None
    best_d = 999999
    for o in osm_map:
        d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
        if d < best_d:
            best_d = d
            best_o = o
    
    tags = best_o['tags'] if best_o else {}
    if tags.get('shelter') == 'yes':
        sheltered_count += 1
    if tags.get('highway') == 'bus_stop':
        highway_bus_stop_count += 1
    if tags.get('public_transport') == 'platform':
        platform_count += 1
        
    b = s.get('monthly_boardings', 0)
    if b < 50:
        low_demand_stops.append((s['name'], b, s['corridor']))

print(f"  • Stops matched to OSM highway=bus_stop:     {highway_bus_stop_count} / {len(stops)}")
print(f"  • Stops matched to OSM public platform:      {platform_count} / {len(stops)}")
print(f"  • Stops with verified physical shelter:      {sheltered_count} / {len(stops)}")
print(f"  • Stops with suspiciously low demand (<50):  {len(low_demand_stops)}")
if low_demand_stops:
    print("    Low demand sample:")
    for n, b, c in low_demand_stops[:5]:
        print(f"      '{n}': {b} pax/month ({c})")

print("\n" + "=" * 80)
print("  SCAN COMPLETED SUCCESSFULLY!")
print("=" * 80)
