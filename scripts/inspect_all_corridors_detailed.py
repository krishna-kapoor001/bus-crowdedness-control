import json
import math

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

stops_map = {s['name'].lower().strip(): (s['latitude'], s['longitude']) for s in stops}

def dist_m(p1, p2):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1]) * 111000

print("=== DETAILED CORRIDOR AUDIT ===")
for c in corridors:
    c_id = c['id']
    pts = c['coordinates']
    c_stops = c.get('stops', [])
    
    # Check max distance from any stop to the polyline
    max_stop_dist = 0
    worst_stop = None
    for s_name in c_stops:
        sc = stops_map.get(s_name.lower().strip())
        if not sc:
            for k, v in stops_map.items():
                if s_name.lower() in k or k in s_name.lower():
                    sc = v
                    break
        if sc:
            min_d = min(dist_m(sc, p) for p in pts)
            if min_d > max_stop_dist:
                max_stop_dist = min_d
                worst_stop = (s_name, min_d)
                
    # Check sharp directional changes (turns > 120 deg)
    kinks = 0
    for i in range(1, len(pts)-1):
        v1 = (pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1])
        v2 = (pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i+1][1])
        d1 = math.hypot(v1[0], v1[1])
        d2 = math.hypot(v2[0], v2[1])
        if d1 > 0.0002 and d2 > 0.0002: # > 20 meters
            dot = (v1[0]*v2[0] + v1[1]*v2[1]) / (d1 * d2)
            if dot < -0.5: # angle > 120 deg
                kinks += 1
                
    ws_name = worst_stop[0] if worst_stop else 'None'
    ws_dist = f"{worst_stop[1]:.0f}m" if worst_stop else "0m"
    print(f"{c_id:<22}: {len(pts):>4} pts | {len(c_stops):>2} stops | kinks={kinks:>2} | worst stop={ws_name} ({ws_dist})")
