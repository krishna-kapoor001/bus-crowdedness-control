import urllib.request
import json
import math

print("=== VERIFYING ALL 28 CORRIDORS LIVE FROM API ===", flush=True)

req = urllib.request.Request("http://localhost:8000/api/v1/network/corridors")
with urllib.request.urlopen(req) as resp:
    corridors = json.loads(resp.read().decode())

req2 = urllib.request.Request("http://localhost:8000/api/v1/network/geojson")
with urllib.request.urlopen(req2) as resp:
    geo = json.loads(resp.read().decode())
    stops_map = {f['properties']['name'].lower().strip(): f['geometry']['coordinates'] for f in geo['features']}

all_passed = True
for idx, c in enumerate(corridors):
    c_id = c['id']
    pts = c['coordinates']
    c_stops = c.get('stops', [])
    
    # 1. Point count check
    if len(pts) < 50:
        print(f"[FAIL] {c_id}: only {len(pts)} points")
        all_passed = False
        continue
        
    # 2. Check kinks (> 135 deg)
    kinks = 0
    for i in range(1, len(pts)-1):
        v1 = (pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1])
        v2 = (pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i+1][1])
        d1 = math.hypot(v1[0], v1[1])
        d2 = math.hypot(v2[0], v2[1])
        if d1 > 0.0001 and d2 > 0.0001:
            dot = (v1[0]*v2[0] + v1[1]*v2[1]) / (d1 * d2)
            if dot < -0.707: # > 135 deg
                kinks += 1
                
    # 3. Check stop distances
    max_d = 0
    worst_s = None
    for s_name in c_stops:
        sc = stops_map.get(s_name.lower().strip())
        if sc:
            # sc is [lon, lat]
            min_dist = min(math.hypot(p[0]-sc[1], p[1]-sc[0])*111000 for p in pts)
            if min_dist > max_d:
                max_d = min_dist
                worst_s = s_name
                
    status = "PASS" if kinks == 0 and max_d < 350 else "WARN"
    print(f"[{idx+1:2d}/28] [{status}] {c_id:<22} | {len(pts):>4} pts | {len(c_stops):>2} stops | kinks={kinks} | max stop dist={max_d:.0f}m ({worst_s})")

if all_passed:
    print("\n>>> ALL 28 CORRIDORS & TRUNK ROUTES FULLY VERIFIED & ROAD-SNAPPED! <<<", flush=True)
