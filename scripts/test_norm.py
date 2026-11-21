import csv, json, re, math
from collections import defaultdict

def normalize_name(s):
    s = s.strip()
    # Remove Metro Station
    s = re.sub(r'Metro\s*(?:Station|Stn)?', ' Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'\(Bus Stop\)', 'Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'Bus Stop\s+Bus Stop', 'Bus Stop', s, flags=re.IGNORECASE)
    # Normalize hyphens and multiple spaces
    s = re.sub(r'[-_/]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def clean_key(s):
    # canonical key for matching
    return re.sub(r'[^a-z0-9]', '', s.lower())

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

# Authoritative dictionary
auth_dict = {}
with open('scripts/perfect_street_snapping_all_428.py', 'r', encoding='utf-8') as f:
    code = f.read()
    match = re.search(r'OSM_AUTHORITATIVE\s*=\s*\{([^}]+)\}', code, re.DOTALL)
    if match:
        for line in match.group(1).splitlines():
            line = line.strip()
            m = re.match(r"['\"]([^'\"]+)['\"]\s*:\s*\(([^,]+),\s*([^,]+),\s*(True|False)\)", line)
            if m:
                auth_dict[clean_key(m.group(1))] = (m.group(1), float(m.group(2)), float(m.group(3)), m.group(4) == 'True')

print(f"OSM Auth count: {len(auth_dict)}")

# Group by normalized key
norm_groups = defaultdict(list)
display_names = {}
for r in gtfs:
    lat = float(r['stop_lat'])
    lon = float(r['stop_lon'])
    if not (28.40 <= lat <= 28.90 and 76.83 <= lon <= 77.35):
        continue
    raw = r['stop_name']
    norm = normalize_name(raw)
    ckey = clean_key(norm)
    norm_groups[ckey].append((lat, lon, norm))
    if ckey not in display_names:
        display_names[ckey] = norm

print(f"Total raw GTFS rows: {sum(len(v) for v in norm_groups.values())}")
print(f"Unique canonical stop clusters: {len(norm_groups)}")

# Inspect Yamuna Vihar canonical clusters
for ckey, poles in norm_groups.items():
    if 'yamunavihar' in ckey:
        print(f"Key: {ckey} | Display: {display_names[ckey]} | Poles: {len(poles)}")
        for p in poles:
            print(f"    lat={p[0]}, lon={p[1]}, raw_norm='{p[2]}'")
