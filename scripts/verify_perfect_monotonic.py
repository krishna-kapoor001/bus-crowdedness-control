import urllib.request
import json
import math

req = urllib.request.Request("http://localhost:8000/api/v1/network/corridors")
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    auro = [c for c in data if c['id'] == 'corridor-aurobindo'][0]
    pts = auro['coordinates']
    print(f"Total points: {len(pts)}")
    # Check if latitude decreases monotonically
    lat_increases = sum(1 for i in range(len(pts)-1) if pts[i+1][0] > pts[i][0])
    print(f"Latitude backtracks: {lat_increases}")
    # Check max angle
    max_turn = 0
    for i in range(1, len(pts)-1):
        v1 = (pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1])
        v2 = (pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i+1][1])
        d1 = math.hypot(v1[0], v1[1])
        d2 = math.hypot(v2[0], v2[1])
        if d1 > 0 and d2 > 0:
            dot = (v1[0]*v2[0] + v1[1]*v2[1]) / (d1 * d2)
            dot = max(-1.0, min(1.0, dot))
            ang = math.degrees(math.acos(dot))
            if ang > max_turn: max_turn = ang
    print(f"Max turn angle between consecutive segments: {max_turn:.1f} degrees")
    if lat_increases == 0 and max_turn < 45:
        print("[PERFECT] Sri Aurobindo Marg is completely straight & unidirectional along the roadway!")
