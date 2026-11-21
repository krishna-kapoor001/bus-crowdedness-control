import sqlite3, math
from collections import defaultdict

conn = sqlite3.connect('data/flowpulse.db')
c = conn.cursor()
c.execute('SELECT id, name, latitude, longitude, is_major_hub FROM stops')
stops = c.fetchall()
conn.close()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

# Find dense clusters: any stop that has 2 or more other stops within 120 meters
dense_clusters = []
for i in range(len(stops)):
    s1 = stops[i]
    neighbors = [s1]
    for j in range(len(stops)):
        if i == j: continue
        s2 = stops[j]
        d = haversine(s1[2], s1[3], s2[2], s2[3])
        if d <= 120:
            neighbors.append((s2[0], s2[1], s2[2], s2[3], round(d, 1)))
    if len(neighbors) >= 3:
        dense_clusters.append(neighbors)

print(f"Total stops in DB: {len(stops)}")
print(f"Stops that have 2+ neighbors within 120m (cluttered clusters): {len(dense_clusters)}")

# Print some distinct clusters
seen_ids = set()
printed = 0
for cluster in dense_clusters:
    center = cluster[0]
    if center[0] in seen_ids: continue
    print(f"\n--- Cluster around '{center[1]}' ({center[2]}, {center[3]}) ---")
    for s in cluster:
        if isinstance(s, tuple) and len(s) == 5:
            print(f"   • {s[1]} -> ({s[2]}, {s[3]}) | Dist: {s[4]}m")
            seen_ids.add(s[0])
        else:
            print(f"   • {s[1]} -> ({s[2]}, {s[3]}) [CENTER]")
            seen_ids.add(s[0])
    printed += 1
    if printed >= 12:
        break
