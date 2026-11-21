import json
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

# Load EXACT_OSM_PINS from apply_exact_osm_pins.py
import sys
sys.path.insert(0, '.')
from scripts.apply_exact_osm_pins import EXACT_OSM_PINS

stops = json.load(open('data/processed/stop_profiles.json', encoding='utf-8'))

print("Auditing major hubs against exact OSM terminal pins...")
offsets = []
for s in stops:
    name_low = s['name'].lower().strip()
    matched_k = None
    if name_low in EXACT_OSM_PINS:
        matched_k = name_low
    else:
        for k in EXACT_OSM_PINS:
            if k == name_low or (len(k) >= 5 and k in name_low):
                matched_k = k
                break
    
    if matched_k:
        target_lat, target_lon = EXACT_OSM_PINS[matched_k]
        cur_lat, cur_lon = s['latitude'], s['longitude']
        dist_m = haversine(cur_lat, cur_lon, target_lat, target_lon) * 1000 # in meters
        if dist_m > 30: # more than 30 meters offset from exact OSM pin
            offsets.append((s['name'], matched_k, (cur_lat, cur_lon), (target_lat, target_lon), round(dist_m, 1)))

print(f"Total hubs offset > 30m from exact OSM pin: {len(offsets)}")
for o in sorted(offsets, key=lambda x: x[4], reverse=True):
    print(f"'{o[0]}' (matched '{o[1]}'): Cur {o[2]} -> OSM {o[3]} | Offset: {o[4]} meters")
