import json
import math

data = json.load(open('data/processed/corridors_routed.json', encoding='utf-8'))

def angle_between(v1, v2):
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.hypot(v1[0], v1[1])
    mag2 = math.hypot(v2[0], v2[1])
    if mag1 == 0 or mag2 == 0:
        return 0
    cos_val = max(-1.0, min(1.0, dot / (mag1 * mag2)))
    return math.degrees(math.acos(cos_val))

print(f"{'CORRIDOR ID':<24} | {'PTS':<5} | {'SHARP U-TURNS (>135 deg)':<25}")
print("-" * 60)

for c in data:
    pts = c['coordinates']
    u_turns = 0
    for i in range(1, len(pts)-1):
        v_in = (pts[i][0] - pts[i-1][0], pts[i][1] - pts[i-1][1])
        v_out = (pts[i+1][0] - pts[i][0], pts[i+1][1] - pts[i][1])
        d_in = math.hypot(v_in[0], v_in[1]) * 111000
        d_out = math.hypot(v_out[0], v_out[1]) * 111000
        # If segment is longer than 15 meters and turns back > 135 degrees
        if d_in > 15 and d_out > 15:
            ang = angle_between(v_in, v_out)
            if ang > 135:
                u_turns += 1
    print(f"{c['id']:<24} | {len(pts):<5} | {u_turns:<25}")
