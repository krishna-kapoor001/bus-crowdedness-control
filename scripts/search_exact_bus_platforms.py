import json
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def extract_coords(obj):
    lat = obj.get('latitude') or obj.get('lat')
    lon = obj.get('longitude') or obj.get('lon')
    if isinstance(lat, list) and isinstance(lon, list):
        if len(lat) > 0 and isinstance(lat[0], (int, float)):
            val1 = float(lat[0])
            val2 = float(lat[1]) if len(lat) > 1 else float(lon[0])
            if 28.0 <= val1 <= 29.0:
                return val1, val2
            elif 28.0 <= val2 <= 29.0:
                return val2, val1
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        l1, l2 = float(lat), float(lon)
        if 28.0 <= l1 <= 29.0:
            return l1, l2
        elif 28.0 <= l2 <= 29.0:
            return l2, l1
    return None, None

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm = json.load(f)

def search_bus_stop(query):
    print(f"\n--- Search for: {query} ---")
    results = []
    for o in osm:
        tags = o.get('tags', {})
        if tags.get('highway') == 'bus_stop' or tags.get('public_transport') == 'platform':
            name = (o.get('name') or tags.get('name') or '').strip()
            if query.lower() in name.lower():
                lat, lon = extract_coords(o)
                if lat and lon:
                    results.append((name, lat, lon, tags.get('shelter') == 'yes'))
    for r in results[:5]:
        print(f"  '{r[0]}' at ({r[1]}, {r[2]}) [shelter={r[3]}]")

search_bus_stop('kashmere gate')
search_bus_stop('isbt')
search_bus_stop('shivaji stadium')
search_bus_stop('badarpur')
search_bus_stop('igi airport')
search_bus_stop('punjabi bagh')
search_bus_stop('rajouri garden')
search_bus_stop('tagore garden')
search_bus_stop('chhatarpur')
search_bus_stop('nehru place')
