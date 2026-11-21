import json
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def min_dist_to_line(lat, lon, polyline):
    if not polyline:
        return 999.0
    return min(haversine(lat, lon, p[0], p[1]) for p in polyline)

with open('data/processed/corridors_routed.json', encoding='utf-8') as f:
    corridors = json.load(f)

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

stop_coord_map = {s['name']: (s['latitude'], s['longitude']) for s in stops}

corridor_deviations = []
all_corridor_stop_names = set()

for c in corridors:
    c_name = c['name']
    c_coords = c.get('coordinates', [])
    c_stops = c.get('stops', [])
    for s_name in c_stops:
        all_corridor_stop_names.add(s_name)
        if s_name in stop_coord_map:
            lat, lon = stop_coord_map[s_name]
            d = min_dist_to_line(lat, lon, c_coords)
            if d > 1.5: # stop is more than 1.5 km away from the corridor line!
                corridor_deviations.append((c_name, s_name, (lat, lon), d))
        else:
            print(f"MISSING STOP IN PROFILES: '{s_name}' in corridor '{c_name}'")

print(f"Total unique corridor stops: {len(all_corridor_stop_names)}")
print(f"Corridor stop deviations > 1.5km from their corridor line: {len(corridor_deviations)}")
for c_name, s_name, coords, d in corridor_deviations:
    print(f"DEVIATION: Corridor '{c_name}' -> Stop '{s_name}' {coords} is {round(d, 2)} km away from line!")
