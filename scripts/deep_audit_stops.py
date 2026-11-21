import json, math
from collections import defaultdict

with open('data/stops_meta.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

print(f"Total stops loaded: {len(stops)}")

# 1. Check for stops that have '(Area' or numbers
area_stops = [s for s in stops if '(Area' in s['name'] or '(1)' in s['name'] or '(2)' in s['name']]
print(f"\n1. Stops with (Area X) or (N) suffixes: {len(area_stops)}")
for s in area_stops[:15]:
    print(f"   • {s['name']} -> ({s['latitude']}, {s['longitude']})")

# 2. Check for stops with similar base names within 300 meters
base_name_clusters = defaultdict(list)
for s in stops:
    base = s['name'].split('(')[0].strip().lower()
    base_name_clusters[base].append(s)

similar_close = []
for base, group in base_name_clusters.items():
    if len(group) > 1:
        for i in range(len(group)):
            for j in range(i+1, len(group)):
                d = haversine(group[i]['latitude'], group[i]['longitude'], group[j]['latitude'], group[j]['longitude'])
                if d < 300:
                    similar_close.append((group[i]['name'], group[j]['name'], d))

print(f"\n2. Same/similar base name stops within 300m of each other: {len(similar_close)}")
for sc in similar_close[:25]:
    print(f"   • {sc[0]}  <--->  {sc[1]}  ({sc[2]:.1f}m)")

# 3. Check for any stops within 50m of each other regardless of name
close_50m = []
for i in range(len(stops)):
    s1 = stops[i]
    for j in range(i+1, len(stops)):
        s2 = stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d < 60:
            close_50m.append((s1['name'], s2['name'], d))

print(f"\n3. Any two stops within 60m of each other: {len(close_50m)}")
for c in close_50m[:25]:
    print(f"   • {c[0]}  <--->  {c[1]}  ({c[2]:.1f}m)")
