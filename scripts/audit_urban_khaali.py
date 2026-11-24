import json
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_raw = json.load(f)

osm_stops = []
for o in osm_raw:
    lat = o.get('latitude')
    lon = o.get('longitude')
    if isinstance(lat, list) and len(lat) == 2:
        lon, lat = lat[0], lat[1]
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        osm_stops.append((float(lat), float(lon), o.get('name', '')))

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

urban_khaali = []
for s in stops:
    lat, lon = s['latitude'], s['longitude']
    # Urban Delhi bounds
    if 28.50 <= lat <= 28.75 and 77.05 <= lon <= 77.32:
        min_d = 999999
        closest = None
        for o_lat, o_lon, o_name in osm_stops:
            if abs(lat - o_lat) > 0.02 or abs(lon - o_lon) > 0.02:
                continue
            d = haversine(lat, lon, o_lat, o_lon)
            if d < min_d:
                min_d = d
                closest = (o_lat, o_lon, o_name)
        if min_d > 80.0:
            urban_khaali.append((min_d, s['name'], s['corridor'], lat, lon, closest[2] if closest else 'None', closest[0] if closest else 0, closest[1] if closest else 0))

urban_khaali.sort(key=lambda x: x[0], reverse=True)
print(f"Urban Delhi stops on KHAALI ROAD (> 80m from any OSM bus stop): {len(urban_khaali)}")
print("\nTop 30 worst urban khaali road stops:")
for u in urban_khaali[:30]:
    print(f"  '{u[1]}' ({u[2]}): {u[0]:.1f}m away from '{u[5]}' at ({u[3]:.5f}, {u[4]:.5f}) vs OSM ({u[6]:.5f}, {u[7]:.5f})")
