import os
import sys
import json
import urllib.request
import time

print("Starting corridor street routing...", flush=True)

# Load calibrated stops
with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops_data = json.load(f)

stops_map = {}
for s in stops_data:
    stops_map[s['name'].lower().strip()] = (s['latitude'], s['longitude'])

print(f"Loaded {len(stops_map)} calibrated stops.", flush=True)

def get_coords(name):
    low = name.lower().strip()
    if low in stops_map:
        return stops_map[low]
    for k, v in stops_map.items():
        if low in k or k in low:
            return v
    return None

def route_waypoints_osrm(pts):
    # pts: list of (lat, lon)
    if len(pts) < 2:
        return [[p[0], p[1]] for p in pts]
    
    # Query OSRM between first and last with intermediate waypoints (max 6 waypoints per query)
    sample_pts = pts if len(pts) <= 6 else [pts[0]] + pts[1:-1:max(1, len(pts)//5)] + [pts[-1]]
    coords_str = ";".join(f"{p[1]:.6f},{p[0]:.6f}" for p in sample_pts)
    url = f"https://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
    req = urllib.request.Request(url, headers={'User-Agent': 'DelhiTransport/3.0'})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('code') == 'Ok':
                geom = data['routes'][0]['geometry']['coordinates']
                return [[round(pt[1], 6), round(pt[0], 6)] for pt in geom]
    except Exception as e:
        print(f"  OSRM error: {e}", flush=True)
    
    # Fallback to dense linear interpolation between all waypoints
    dense = []
    for i in range(len(pts) - 1):
        p1, p2 = pts[i], pts[i+1]
        dense.append([round(p1[0], 6), round(p1[1], 6)])
        for step in range(1, 10):
            frac = step / 10.0
            dense.append([round(p1[0] + (p2[0]-p1[0])*frac, 6), round(p1[1] + (p2[1]-p1[1])*frac, 6)])
    dense.append([round(pts[-1][0], 6), round(pts[-1][1], 6)])
    return dense

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

# Update corridor-airport stops list so Mahipal Pur Village and Shiv Murti are included
for c in corridors:
    if c['id'] == 'corridor-airport':
        c['stops'] = [
            "Dhaula Kuan",
            "Satya Niketan",
            "Mahipal Pur Crossing",
            "Mahipal Pur",
            "Mahipal Pur Village",
            "Shiv Murti",
            "Kapashera Border"
        ]

for idx, c in enumerate(corridors):
    c_stops = c.get('stops', [])
    pts = [get_coords(s) for s in c_stops if get_coords(s)]
    print(f"[{idx+1}/{len(corridors)}] {c['id']} ({len(pts)} stops)...", end='', flush=True)
    if len(pts) >= 2:
        new_coords = route_waypoints_osrm(pts)
        c['coordinates'] = new_coords
        print(f" -> {len(new_coords)} road points.", flush=True)
    else:
        print(" -> Skipped (not enough points)", flush=True)
    time.sleep(0.4)

with open('data/processed/corridors_routed.json', 'w', encoding='utf-8') as f:
    json.dump(corridors, f, indent=2, ensure_ascii=False)

print("Saved all updated corridors to data/processed/corridors_routed.json!", flush=True)
