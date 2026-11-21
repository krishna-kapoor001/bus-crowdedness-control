import json
import math

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

stops_map = {s['name'].lower().strip(): (s['latitude'], s['longitude'], s['name']) for s in stops}

print("=== AUDIT OF CORRIDOR STOPS & GEOMETRY ===")
for c in corridors:
    c_id = c['id']
    c_stops = c.get('stops', [])
    pts = c.get('coordinates', [])
    
    stop_coords = []
    for s in c_stops:
        sc = stops_map.get(s.lower().strip())
        if sc:
            stop_coords.append((sc[0], sc[1], sc[2]))
        else:
            # find partial
            found = False
            for k, v in stops_map.items():
                if s.lower() in k or k in s.lower():
                    stop_coords.append((v[0], v[1], v[2]))
                    found = True
                    break
            if not found:
                stop_coords.append((None, None, s))
                
    # Calculate distances between consecutive stops
    jumps = []
    for i in range(len(stop_coords)-1):
        c1 = stop_coords[i]
        c2 = stop_coords[i+1]
        if c1[0] and c2[0]:
            d = math.hypot(c1[0]-c2[0], c1[1]-c2[1]) * 111
            if d > 12.0: # jump > 12km
                jumps.append(f"{c1[2]} -> {c2[2]} ({d:.1f}km)")
                
    if jumps:
        print(f"Corridor {c_id}: Suspicious large jumps: {jumps}")
    else:
        print(f"Corridor {c_id}: OK ({len(c_stops)} stops, {len(pts)} pts)")
