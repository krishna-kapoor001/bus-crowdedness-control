import json
import math
import re

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

def get_tokens(name):
    clean = re.sub(r'[^a-zA-Z0-9]', ' ', (name or '').lower())
    ignore = {'bus', 'stop', 'stand', 'terminal', 'crossing', 'xing', 'more', 'road', 'marg', 'delhi', 'village', 'cluster', 'depot', 'cws', 'ii', 'iv'}
    return set(w for w in clean.split() if len(w) > 2 and w not in ignore)

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_raw = json.load(f)

# Collect all genuine highway=bus_stop / platform nodes
platforms = []
for o in osm_raw:
    tags = o.get('tags', {})
    if tags.get('highway') == 'bus_stop' or tags.get('public_transport') == 'platform':
        name = (o.get('name') or tags.get('name') or '').strip()
        if not name or name.lower() in ['unnamed', 'bus stop']:
            continue
        lat, lon = extract_coords(o)
        if lat and lon and 28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.6:
            platforms.append({
                'name': name,
                'tokens': get_tokens(name),
                'lat': lat,
                'lon': lon,
                'tags': tags,
                'shelter': tags.get('shelter') == 'yes'
            })

print(f"Total authentic platform/shelter bus stop nodes in Delhi: {len(platforms)}")

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

# For each of the 72 stops that are currently on in-roadway stop_positions:
can_snap_to_platform = []
no_nearby_platform = []

for s in catalog:
    # check if s is sitting on a roadway stop_position
    # Find matching platform within 80m
    s_toks = get_tokens(s['name'])
    best_p = None
    best_d = 999999
    
    for p in platforms:
        d = haversine(s['latitude'], s['longitude'], p['lat'], p['lon'])
        if d <= 90.0:
            # check token match or substring match
            overlap = s_toks & p['tokens']
            is_sub = (s['name'].lower() in p['name'].lower()) or (p['name'].lower() in s['name'].lower())
            if overlap or is_sub:
                # Prioritize platforms with shelter
                bonus = 10 if p['shelter'] else 0
                effective_d = d - bonus
                if effective_d < best_d:
                    best_d = effective_d
                    best_p = (d, p)
                    
    if best_p and best_p[0] > 1.5:  # currently offset from the platform
        can_snap_to_platform.append((s, best_p[0], best_p[1]))

print(f"Stops currently offset from physical platform that CAN snap to OSM platform: {len(can_snap_to_platform)}")
for s, d, p in can_snap_to_platform[:25]:
    print(f"  '{s['name']}' at ({s['latitude']}, {s['longitude']}) -> Move {d:.1f}m onto Platform: '{p['name']}' at ({p['lat']}, {p['lon']}) [shelter={p['shelter']}]")
