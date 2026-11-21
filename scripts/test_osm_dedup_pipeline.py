import json, math, re
from collections import defaultdict

# 1. Load OSM Stops
with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    raw_osm = json.load(f)

# Delhi NCT bounds
delhi_osm = []
for s in raw_osm:
    # Ensure point coordinate
    lat = s['latitude']
    lon = s['longitude']
    if isinstance(lat, list):
        if isinstance(lat[0], list):
            lat = sum(p[1] for p in lat) / len(lat)
        else:
            lat = sum(lat) / len(lat)
    if isinstance(lon, list):
        if isinstance(lon[0], list):
            lon = sum(p[0] for p in lon) / len(lon)
        else:
            lon = sum(lon) / len(lon)
    lat = float(lat)
    lon = float(lon)
    if not (28.40 <= lat <= 28.90 and 76.83 <= lon <= 77.35):
        continue
    delhi_osm.append({
        'name': s['name'],
        'latitude': round(lat, 6),
        'longitude': round(lon, 6),
        'is_hub': s['is_hub']
    })

print(f"Total OSM stops in Delhi NCT: {len(delhi_osm)}")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

# Deduplicate OSM stops that are opposite poles within 55m
sorted_osm = sorted(delhi_osm, key=lambda x: (not x['is_hub'], x['name']))
deduped_osm = []
used = set()

for i, s1 in enumerate(sorted_osm):
    if i in used:
        continue
    cluster = [s1]
    used.add(i)
    for j in range(i + 1, len(sorted_osm)):
        if j in used:
            continue
        s2 = sorted_osm[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d <= 55:
            cluster.append(s2)
            used.add(j)
            
    is_hub = any(x['is_hub'] for x in cluster)
    hub_stops = [x for x in cluster if x['is_hub']]
    if hub_stops:
        best_name = hub_stops[0]['name']
        best_lat = hub_stops[0]['latitude']
        best_lon = hub_stops[0]['longitude']
    else:
        named = [x for x in cluster if x['name'] != 'Unnamed']
        best_name = named[0]['name'] if named else cluster[0]['name']
        best_lat = round(sum(x['latitude'] for x in cluster) / len(cluster), 6)
        best_lon = round(sum(x['longitude'] for x in cluster) / len(cluster), 6)
        
    deduped_osm.append({
        'name': best_name,
        'latitude': best_lat,
        'longitude': best_lon,
        'is_hub': is_hub
    })

print(f"Deduped single-dot OSM stops in Delhi NCT: {len(deduped_osm)}")
print(f"  Major Bus Stands / Terminals / Depots (Black Dots): {sum(1 for s in deduped_osm if s['is_hub'])}")
print(f"  Regular Bus Stops (Blue Dots): {sum(1 for s in deduped_osm if not s['is_hub'])}")

# Check duplicate pairs within 50m in deduped_osm
close = 0
for i in range(len(deduped_osm)):
    for j in range(i+1, len(deduped_osm)):
        if haversine(deduped_osm[i]['latitude'], deduped_osm[i]['longitude'], deduped_osm[j]['latitude'], deduped_osm[j]['longitude']) < 50:
            close += 1

print(f"Pairs within 50m in deduped OSM: {close}")

# Inspect Yamuna Vihar
print("\nYamuna Vihar in deduped OSM:")
for s in deduped_osm:
    if 'yamuna vihar' in s['name'].lower():
        print(f"  • {s['name']}: [{s['latitude']}, {s['longitude']}] (Hub: {s['is_hub']})")
