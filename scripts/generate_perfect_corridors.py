import os
import sys
import json
import urllib.request
import time

# Load calibrated stops
with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops_data = json.load(f)

stops_map = {}
for s in stops_data:
    stops_map[s['name'].lower().strip()] = (s['latitude'], s['longitude'])

print(f"Loaded {len(stops_map)} calibrated stops.")

# Helper to find stop coordinate
def get_coords(name):
    low = name.lower().strip()
    if low in stops_map:
        return stops_map[low]
    # Try fuzzy / partial
    for k, v in stops_map.items():
        if low in k or k in low:
            return v
    return None

# Route between waypoints using OSRM
def route_osrm(waypoints):
    # waypoints: list of (lat, lon)
    if len(waypoints) < 2:
        return [[pt[0], pt[1]] for pt in waypoints]
    
    # OSRM expects lon,lat; limit batch to avoid URL length issues
    coords_str = ";".join(f"{pt[1]:.6f},{pt[0]:.6f}" for pt in waypoints)
    url = f"https://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
    req = urllib.request.Request(url, headers={'User-Agent': 'DelhiTransportStack/2.0'})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('code') == 'Ok':
                geom = data['routes'][0]['geometry']['coordinates']
                # Convert [lon, lat] to [lat, lon]
                return [[round(pt[1], 6), round(pt[0], 6)] for pt in geom]
    except Exception as e:
        print(f"  OSRM batch error ({e}), falling back to linear segments between waypoints")
    
    # Fallback: connect consecutive waypoints
    return [[round(pt[0], 6), round(pt[1], 6)] for pt in waypoints]

# Load current corridors list to preserve metadata
with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

# Update corridor-airport specifically to ensure ALL its stops are present and on the highway
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

updated_corridors = []

for idx, c in enumerate(corridors):
    print(f"Processing ({idx+1}/{len(corridors)}) {c['id']}: {c['name']}...")
    stops_list = c.get('stops', [])
    waypoints = []
    resolved_stops = []
    
    for s_name in stops_list:
        pt = get_coords(s_name)
        if pt:
            waypoints.append(pt)
            resolved_stops.append(s_name)
        else:
            print(f"  Warning: could not resolve stop '{s_name}'")

    if len(waypoints) >= 2:
        # Route through waypoints
        time.sleep(0.3) # Avoid hammering public OSRM
        routed_coords = route_osrm(waypoints)
        print(f"  Routed {len(waypoints)} stops -> {len(routed_coords)} street-snapped coordinates")
        c['coordinates'] = routed_coords
    else:
        print(f"  Insufficient waypoints for {c['id']}")
    
    updated_corridors.append(c)

# Save back to data/processed/corridors_routed.json
with open('data/processed/corridors_routed.json', 'w', encoding='utf-8') as f:
    json.dump(updated_corridors, f, indent=2, ensure_ascii=False)

print("\nSUCCESS! Successfully generated and saved all street-snapped corridors & routes!")
