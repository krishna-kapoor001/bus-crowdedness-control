import json
import math

data = json.load(open('data/processed/corridors_routed.json', encoding='utf-8'))

print("=== CHECKING ALL 28 CORRIDORS & ROUTES FOR SPURS / HOOKS / DETOURS ===")
for c in data:
    pts = c['coordinates']
    stops = c.get('stops', [])
    
    # Check total length vs straight line distance from first to last
    d_straight = math.hypot(pts[0][0]-pts[-1][0], pts[0][1]-pts[-1][1]) * 111000
    d_total = sum(math.hypot(pts[i][0]-pts[i+1][0], pts[i][1]-pts[i+1][1]) * 111000 for i in range(len(pts)-1))
    ratio = d_total / max(1, d_straight)
    
    # Check if there are segments where line doubles back on itself
    backtracks = 0
    for i in range(len(pts)-2):
        v1 = (pts[i+1][0] - pts[i][0], pts[i+1][1] - pts[i][1])
        v2 = (pts[i+2][0] - pts[i+1][0], pts[i+2][1] - pts[i+1][1])
        dot = v1[0]*v2[0] + v1[1]*v2[1]
        if dot < -0.000001: # angle > 90 degrees
            backtracks += 1
            
    print(f"{c['id']:<24}: len={len(pts):>4} | straight={d_straight/1000:>5.1f}km | actual={d_total/1000:>5.1f}km | ratio={ratio:.2f} | backtracks={backtracks}")
