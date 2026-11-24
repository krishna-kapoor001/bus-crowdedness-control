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

print(f"Total stops in catalog: {len(stops)}")
print(f"Total OSM bus stops in Delhi: {len(osm_stops)}")

# Find which stops in catalog are on a "khaali road" (far from any OSM bus stop)
khaali_road_stops = []
snapped_stops = []

for s in stops:
    min_d = 999999
    closest_osm = None
    # Spatial filter: only check OSM stops within 0.01 deg (~1.1 km)
    s_lat, s_lon = s['latitude'], s['longitude']
    for o_lat, o_lon, o_name in osm_stops:
        if abs(s_lat - o_lat) > 0.015 or abs(s_lon - o_lon) > 0.015:
            continue
        d = haversine(s_lat, s_lon, o_lat, o_lon)
        if d < min_d:
            min_d = d
            closest_osm = (o_lat, o_lon, o_name)
            
    if min_d > 80.0: # more than 80 meters away from ANY OSM bus stop!
        khaali_road_stops.append((min_d, s['name'], s['corridor'], s['latitude'], s['longitude'], closest_osm[2] if closest_osm else 'None'))
    else:
        snapped_stops.append((min_d, s['name'], closest_osm[2] if closest_osm else 'None'))

print(f"Stops sitting right on/near an authentic OSM bus stop (<= 80m): {len(snapped_stops)}")
print(f"Stops sitting on KHAALI ROAD (> 80m from any OSM bus stop): {len(khaali_road_stops)}")

print("\nSample 25 stops sitting on KHAALI ROAD:")
for k in khaali_road_stops[:25]:
    print(f"  '{k[1]}' ({k[2]}): {k[0]:.1f}m away from nearest OSM stop '{k[5]}'")
