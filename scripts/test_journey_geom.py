import re
import json
import math

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    routed_corridors = {c['id']: c for c in json.load(f)}

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops_meta = {s['name'].lower().strip(): s for s in json.load(f)}

def get_route_geometry(orig_name: str, dest_name: str, bus_routes: list[str]):
    for r in bus_routes:
        r_clean = re.sub(r'[^a-zA-Z0-9]', '', r.lower())
        r_base = re.sub(r'(up|down|stl|a)$', '', r_clean)
        for cid, cdata in routed_corridors.items():
            cid_clean = cid.replace('route-', '').replace('corridor-', '')
            if r_clean == cid_clean or r_clean in cid_clean or cid_clean in r_clean or (len(r_base) >= 3 and r_base in cid_clean):
                pts = cdata.get('coordinates', [])
                if pts and len(pts) >= 2:
                    orig_info = stops_meta.get(orig_name.lower().strip())
                    if orig_info:
                        o_lat, o_lon = orig_info['latitude'], orig_info['longitude']
                        d_start = math.hypot(pts[0][0]-o_lat, pts[0][1]-o_lon)
                        d_end = math.hypot(pts[-1][0]-o_lat, pts[-1][1]-o_lon)
                        if d_end < d_start:
                            return list(reversed(pts))
                    return pts
    return []

# Test Saket to Dhaula Kuan with 546DOWN
geom = get_route_geometry("Saket Metro Station", "Dhaula Kuan", ["546DOWN"])
print(f"Matched points count: {len(geom)}")
if geom:
    print("Start point:", geom[0])
    print("End point:", geom[-1])
    print("Sample middle points:", geom[len(geom)//2])
