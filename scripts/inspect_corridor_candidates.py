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

valid_osm = [s for s in osm_stops if isinstance(s.get('latitude'), (int, float)) and isinstance(s.get('longitude'), (int, float))]

# Let's inspect all stops along NH-48 and NH-9
check_names = [
    'Khichdipur', 'Sanjay Lake Trilokpuri', 'Shiv Murti', 'Shiv Murti II NH 8 Dawrcka More',
    'Lalita Park', 'Pusta Crossing Akhardham Temple', 'Samaspur Jagir Village',
    'NHW 24 crossing', 'National Highway 24 Crossing', 'NHW 8',
    'Rangpuri', 'Mahipal Pur Village', 'Radisson Hotel Mahipal Pur Crossing', 'Rajokari Crossing'
]

for name in check_names:
    matches = [s for s in stops if s['name'].lower() == name.lower()]
    if matches:
        s = matches[0]
        # Find nearest 3 OSM bus stops with names
        osm_candidates = sorted(
            [o for o in valid_osm if o.get('name') and o['name'].strip() != 'Unnamed'],
            key=lambda o: haversine(s['latitude'], s['longitude'], o['latitude'], o['longitude'])
        )[:3]
        print(f"\nStop: {s['name']} at ({s['latitude']}, {s['longitude']})")
        for oc in osm_candidates:
            d = haversine(s['latitude'], s['longitude'], oc['latitude'], oc['longitude'])
            print(f"   OSM: '{oc['name']}' at ({oc['latitude']}, {oc['longitude']}) - {d:.1f}m")
