import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.test_stage1_stage2 import stage2_stops, haversine

for i in range(len(stage2_stops)):
    s1 = stage2_stops[i]
    for j in range(i+1, len(stage2_stops)):
        s2 = stage2_stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d < 70:
            print(f"Remaining close: {s1['name']} <-> {s2['name']} ({d:.1f}m)")
