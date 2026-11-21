import csv, json, re, math
from collections import defaultdict

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

# Load OSM authoritative
auth_dict = {}
with open('scripts/perfect_street_snapping_all_428.py', 'r', encoding='utf-8') as f:
    code = f.read()
    match = re.search(r'OSM_AUTHORITATIVE\s*=\s*\{([^}]+)\}', code, re.DOTALL)
    if match:
        for line in match.group(1).splitlines():
            line = line.strip()
            m = re.match(r"['\"]([^'\"]+)['\"]\s*:\s*\(([^,]+),\s*([^,]+),\s*(True|False)\)", line)
            if m:
                auth_dict[m.group(1).lower().strip()] = (float(m.group(2)), float(m.group(3)), m.group(4) == 'True')

def clean_stop_name(name):
    s = name.strip()
    s = re.sub(r'Metro\s*(?:Station|Stn)?', ' Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'\(Bus Stop\)', 'Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'Bus Stop\s+Bus Stop', 'Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'\(\s*\)', '', s).strip()
    return s

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

# Group by clean name
name_groups = defaultdict(list)
for r in gtfs:
    lat = float(r['stop_lat'])
    lon = float(r['stop_lon'])
    if not (28.40 <= lat <= 28.90 and 76.83 <= lon <= 77.35):
        continue
    cname = clean_stop_name(r['stop_name'])
    name_groups[cname].append((lat, lon))

unified_stops = []
for name, poles in name_groups.items():
    key = name.lower().strip()
    is_hub = any(t in key for t in ['terminal', 'depot', 'isbt', 'bus stand'])
    
    if key in auth_dict:
        lat, lon, is_h = auth_dict[key]
        if is_h: is_hub = True
        unified_stops.append({'name': name, 'lat': lat, 'lon': lon, 'is_hub': is_hub, 'source': 'authoritative'})
    elif len(poles) == 1:
        unified_stops.append({'name': name, 'lat': poles[0][0], 'lon': poles[0][1], 'is_hub': is_hub, 'source': 'single_pole'})
    else:
        clusters = []
        for p_lat, p_lon in poles:
            placed = False
            for c in clusters:
                c_lat = sum(p[0] for p in c) / len(c)
                c_lon = sum(p[1] for p in c) / len(c)
                if haversine(p_lat, p_lon, c_lat, c_lon) <= 150:
                    c.append((p_lat, p_lon))
                    placed = True
                    break
            if not placed:
                clusters.append([(p_lat, p_lon)])
        
        for c_idx, c in enumerate(clusters):
            avg_lat = sum(p[0] for p in c) / len(c)
            avg_lon = sum(p[1] for p in c) / len(c)
            cluster_name = name if len(clusters) == 1 else f'{name} ({c_idx + 1})'
            unified_stops.append({'name': cluster_name, 'lat': round(avg_lat, 6), 'lon': round(avg_lon, 6), 'is_hub': is_hub, 'source': 'merged_cluster'})

# Also add missing authoritative hubs
for k, (m_lat, m_lon, m_hub) in auth_dict.items():
    if not any(s['name'].lower() == k for s in unified_stops):
        unified_stops.append({'name': k.title(), 'lat': m_lat, 'lon': m_lon, 'is_hub': m_hub, 'source': 'auth_extra'})

print(f'Total unified stops: {len(unified_stops)}')

# Let us verify Yamuna Vihar
yv = [s for s in unified_stops if 'yamuna vihar' in s['name'].lower()]
print(f'Yamuna Vihar stops ({len(yv)}):')
for s in yv:
    print(f"  - {s['name']}: [{s['lat']}, {s['lon']}] (is_hub={s['is_hub']})")
