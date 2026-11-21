import json
import math
import urllib.request
import time

print("=== DEPLOYING COMPLETE STREET-SNAPPED MASTER GEOMETRIES ===", flush=True)

# 1. Fetch street-snapped geometries for corridors that need OSRM
def fetch_osrm(waypoints):
    # Split into chunks of max 6 points if needed
    if len(waypoints) <= 6:
        chunks = [waypoints]
    else:
        chunks = [waypoints[:5], waypoints[4:]]
        
    full_geom = []
    for chunk in chunks:
        coords_str = ";".join(f"{p[1]:.6f},{p[0]:.6f}" for p in chunk)
        url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
        req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhiMaster/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode())
                if data.get('code') == 'Ok':
                    geom = [[p[1], p[0]] for p in data['routes'][0]['geometry']['coordinates']]
                    if full_geom and geom and full_geom[-1] == geom[0]:
                        full_geom.extend(geom[1:])
                    else:
                        full_geom.extend(geom)
        except Exception as e:
            print(f"OSRM error on chunk: {e}")
        time.sleep(0.4)
    return full_geom

# Define waypoints for the 8 corridors
CORRIDOR_WAYPOINTS = {
    "corridor-ring": [
        (28.6675, 77.2285), (28.6410, 77.2500), (28.6290, 77.2490),
        (28.5871, 77.2591), (28.5714, 77.2592), (28.5700, 77.2400),
        (28.5690, 77.2134), (28.5702, 77.2078), (28.5835, 77.1675), (28.6000, 77.1620)
    ],
    "corridor-mb": [
        (28.5217, 77.1827), (28.5205, 77.2027), (28.5180, 77.2320),
        (28.5126, 77.2485), (28.5030, 77.2880), (28.4984, 77.3045)
    ],
    "corridor-outer-ring": [
        (28.5580, 77.1720), (28.5458, 77.2025), (28.5470, 77.2250),
        (28.5485, 77.2571), (28.5395, 77.2662), (28.5350, 77.2750)
    ],
    "corridor-gtk": [
        (28.7072, 77.1783), (28.7180, 77.1750), (28.7255, 77.1635),
        (28.7520, 77.1550), (28.7981, 77.1352), (28.8250, 77.1200)
    ],
    "corridor-mathura": [
        (28.6373, 77.2412), (28.6180, 77.2440), (28.5880, 77.2530),
        (28.5714, 77.2592), (28.5350, 77.2800), (28.4984, 77.3045)
    ],
    "corridor-transyamuna": [
        (28.6743, 77.2871), (28.6729, 77.2699), (28.6313, 77.2789),
        (28.6483, 77.3178), (28.6041, 77.2944)
    ]
}

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

for c_id, wps in CORRIDOR_WAYPOINTS.items():
    print(f"Fetching street geometry for {c_id}...")
    geom = fetch_osrm(wps)
    if geom and len(geom) > 100:
        for c in corridors:
            if c['id'] == c_id:
                c['coordinates'] = geom
                print(f"  [OK] {c_id}: {len(geom)} street points.")

with open('data/processed/corridors_routed.json', 'w', encoding='utf-8') as f:
    json.dump(corridors, f, indent=2, ensure_ascii=False)

print("Saved updated street corridors to data/processed/corridors_routed.json!", flush=True)

# Snap all stops directly to route polylines
with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

stops_map = {s['name'].lower().strip(): s for s in stops}

snapped_count = 0
for c in corridors:
    pts = c['coordinates']
    for s_name in c['stops']:
        st = stops_map.get(s_name.lower().strip())
        if not st:
            for k, v in stops_map.items():
                if s_name.lower() in k or k in s_name.lower():
                    st = v
                    break
        if st:
            s_lat, s_lon = st['latitude'], st['longitude']
            best_p = min(pts, key=lambda p: (p[0]-s_lat)**2 + (p[1]-s_lon)**2)
            dist_m = math.hypot(best_p[0]-s_lat, best_p[1]-s_lon) * 111000
            if dist_m <= 1500:
                st['latitude'] = best_p[0]
                st['longitude'] = best_p[1]
                snapped_count += 1

print(f"Snapped {snapped_count} stop coordinates directly to street polylines.")

with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

print("=== ALL STREET POLYLINES & STOPS MASTER DEPLOYED SUCCESSFULLY ===", flush=True)
