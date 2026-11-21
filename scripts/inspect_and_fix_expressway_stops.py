import json, math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

with open('data/stops_meta.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_stops = json.load(f)

# Filter OSM stops with valid float lat/lon
valid_osm = []
for s in osm_stops:
    lat = s.get('latitude')
    lon = s.get('longitude')
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        valid_osm.append(s)

print(f"Total valid OSM bus stops: {len(valid_osm)}")

# Let's inspect the 6 flagged stops
flagged = ['Khichdipur', 'Lalita Park', 'Pusta Crossing Akhardham Temple', 'Samaspur Jagir Village', 'Sanjay Lake Trilokpuri', 'Shiv Murti']

for fname in flagged:
    matching_meta = [s for s in stops if s['name'].lower() == fname.lower()]
    if matching_meta:
        ms = matching_meta[0]
        print(f"\n--- {fname} (Current: {ms['latitude']}, {ms['longitude']}) ---")
        # Find nearest OSM ground-truth stops
        nearest_osm = sorted(valid_osm, key=lambda x: haversine(ms['latitude'], ms['longitude'], x['latitude'], x['longitude']))[:5]
        for o in nearest_osm:
            dist = haversine(ms['latitude'], ms['longitude'], o['latitude'], o['longitude'])
            print(f"  OSM match: '{o.get('name')}' at ({o['latitude']}, {o['longitude']}) - {dist:.1f}m away")
