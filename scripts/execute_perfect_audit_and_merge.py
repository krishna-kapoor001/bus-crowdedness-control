import json, math, os, re, sqlite3, csv
from difflib import SequenceMatcher
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'flowpulse.db')

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def normalize(name):
    s = name.strip()
    s = re.sub(r'\(.*?\)', '', s).strip()
    s = re.sub(r'\bbus\s+stop\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bbus\s+stand\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bterminal\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bxing\b', 'crossing', s, flags=re.IGNORECASE)
    s = re.sub(r'\bmor\b', 'crossing', s, flags=re.IGNORECASE)
    s = re.sub(r'\bmore\b', 'crossing', s, flags=re.IGNORECASE)
    s = re.sub(r'\bchowk\b', 'crossing', s, flags=re.IGNORECASE)
    s = re.sub(r'[-_/]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

def words_overlap(n1, n2):
    w1 = set(normalize(n1).split())
    w2 = set(normalize(n2).split())
    ignore = {'road', 'marg', 'block', 'phase', 'sec', 'sector', 'delhi', 'crossing', 'stand', 'stop', 'gate', 'near', 'opp', 'opposite'}
    w1_sig = w1 - ignore
    w2_sig = w2 - ignore
    if not w1_sig or not w2_sig:
        return 0.0
    intersection = w1_sig.intersection(w2_sig)
    return len(intersection) / min(len(w1_sig), len(w2_sig))

# Load stops_meta.json
with open(os.path.join(DATA_DIR, 'stops_meta.json'), 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Starting with {len(stops)} stops.")

# Pre-defined preferred canonical names for well-known pairs
PREFERRED_NAMES = {
    'barar square': 'Brar Square',
    'brar square': 'Brar Square',
    'kanjhawla chowk': 'Kanjhawala Chowk',
    'kanjhawala chowk': 'Kanjhawala Chowk',
    'padhmini enclave': 'Padmini Enclave',
    'padmani enclave': 'Padmini Enclave',
    'chhawni hospital': 'Chhawani Hospital',
    'chhawani hospital': 'Chhawani Hospital',
    'mangol pur school': 'Mangolpuri School',
    'mangolpuri school': 'Mangolpuri School',
    'c 5a janakpuri': 'Janakpuri C-5A',
    'janakpuri c 5a': 'Janakpuri C-5A',
    'mukund pur chowk': 'Mukundpur Chowk',
    'mukund pur crossing': 'Mukundpur Chowk',
    'jaitpur crossing': 'Jaitpur Mor',
    'jaitpur mor': 'Jaitpur Mor',
    'madhuban chowk outer ring road': 'Madhuban Chowk',
    'madhuban chowk': 'Madhuban Chowk',
    'kapashera crossing': 'Kapashera Crossing',
    'kapashera more': 'Kapashera Crossing',
    'najafgarh dhansa stand': 'Najafgarh Dhansa Stand',
    'nazafgarh dhansa more': 'Najafgarh Dhansa Stand',
    'haryana shakti school kanjhawala': 'Haryana Shakti School Kanjhawala',
    'kanjhawala haryana shakti c school': 'Haryana Shakti School Kanjhawala',
    'jhilmil crossing dilshad garden gt road': 'Jhilmil Crossing',
    'jhilmil crossing': 'Jhilmil Crossing',
    'q block mangol puri terminal': 'Q Block Mangol Puri Terminal',
    'q block mangolpuri': 'Q Block Mangol Puri Terminal',
    'tara apartments terminal': 'Tara Apartments Terminal',
    'tara apartment': 'Tara Apartments Terminal',
    'west enclave terminal': 'West Enclave Terminal',
    'west enclave': 'West Enclave Terminal',
    'natthupura crossing terminal': 'Natthupura Crossing Terminal',
    'natthupura': 'Natthupura Crossing Terminal',
    'shahbad daulatpur gaon': 'Shahbad Daulatpur Gaon',
    'shahbad gaon': 'Shahbad Daulatpur Gaon',
    'khel gaon': 'Khel Gaon',
    'khel gaon siri fort road': 'Khel Gaon',
    'dev nagar': 'Dev Nagar Khalsa College',
    'dev nagar khalsa college': 'Dev Nagar Khalsa College',
    'hansraj college': 'Hansraj College',
    'hansraj college malka ganj': 'Hansraj College',
    'shakur pur': 'Shakurpur JJ Colony Britannia',
    'shakur pur jj colony britannia': 'Shakurpur JJ Colony Britannia',
    'pg dav college sri niwaspuri': 'PG DAV College Sri Niwaspuri',
    'sri niwaspuri pg dav college lajpat nagar': 'PG DAV College Sri Niwaspuri',
    'shastri park': 'Shastri Park Pusta Road',
    'shastri park pusta road': 'Shastri Park Pusta Road',
    'rr hospital': 'RR Hospital Maharana Pratap Chowk',
    'rr hospital maharana pratap chowk': 'RR Hospital Maharana Pratap Chowk',
    'lokesh cinema nangloi jj colony': 'Lokesh Cinema Nangloi JJ Colony',
    'nangloi jj colony': 'Lokesh Cinema Nangloi JJ Colony',
    'gtb nagar': 'GTB Nagar (Haqiqat Nagar)',
    'gtb nagar haqiqat nagar': 'GTB Nagar (Haqiqat Nagar)',
    'shani mandir vasant village': 'Vasant Village',
    'vasant village': 'Vasant Village',
    'naraina vihar': 'Naraina Vihar Indra Market',
    'naraina vihar indra market': 'Naraina Vihar Indra Market',
    'meera bagh': 'Meera Bagh',
    'meera bagh apartment': 'Meera Bagh',
    'sheikh sarai more': 'Sheikh Sarai Phase 2',
    'sheikh sarai phase 2': 'Sheikh Sarai Phase 2',
    'sheikh sarai ph ii': 'Sheikh Sarai Phase 2',
    'zakhira': 'Zakhira',
    'zakhira flyover': 'Zakhira',
    'ridge road': 'Upper Ridge Road',
    'upper ridge road': 'Upper Ridge Road',
    'shalimar bagh (2)': 'Shalimar Bagh A Block',
    'shalimar bagh a block': 'Shalimar Bagh A Block',
    'police station roop nagar banglow road': 'Roop Nagar',
    'roop nagar': 'Roop Nagar',
    'wazirabad crossing': 'Wazirabad Crossing GT Road',
    'wazirabad crossing gt road': 'Wazirabad Crossing GT Road',
    'laxmi nagar': 'Laxmi Nagar Shakarpur Crossing',
    'laxmi nagar shakarpur crossing': 'Laxmi Nagar Shakarpur Crossing',
    'khajuri': 'Khajuri Circle',
    'khajuri circle': 'Khajuri Circle',
    'chhoturam park rohini sec 5': 'Rohini Sec 5',
    'rohini sec 5': 'Rohini Sec 5',
    'jahangirpuri b block': 'Jahangirpuri B Block',
    'jahangirpuri': 'Jahangirpuri B Block'
}

# Graph-based clustering of duplicates
parent = list(range(len(stops)))
def find(i):
    if parent[i] == i: return i
    parent[i] = find(parent[i])
    return parent[i]

def union(i, j):
    root_i = find(i)
    root_j = find(j)
    if root_i != root_j:
        parent[root_i] = root_j

merged_count = 0
for i in range(len(stops)):
    s1 = stops[i]
    for j in range(i + 1, len(stops)):
        s2 = stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        
        # Check explicit duplicate pairs or close semantic duplicates
        n1_lower = s1['name'].strip().lower()
        n2_lower = s2['name'].strip().lower()
        
        explicit_dup = (n1_lower in PREFERRED_NAMES and n2_lower in PREFERRED_NAMES and PREFERRED_NAMES[n1_lower] == PREFERRED_NAMES[n2_lower])
        
        if explicit_dup or d <= 180:
            norm1 = normalize(s1['name'])
            norm2 = normalize(s2['name'])
            sim = SequenceMatcher(None, norm1, norm2).ratio()
            overlap = words_overlap(s1['name'], s2['name'])
            
            if explicit_dup or norm1 == norm2 or norm1 in norm2 or norm2 in norm1 or (overlap >= 0.8 and d <= 150) or (sim >= 0.70 and d <= 120):
                # Don't merge distinct hubs unless they are the same terminal
                if s1.get('is_major_hub', False) and s2.get('is_major_hub', False):
                    continue
                union(i, j)
                merged_count += 1

groups = defaultdict(list)
for i in range(len(stops)):
    groups[find(i)].append(stops[i])

print(f"Grouped into {len(groups)} distinct master stops (merged {len(stops) - len(groups)} duplicate stops).")

merged_stops = []
for root, member_stops in groups.items():
    if len(member_stops) == 1:
        merged_stops.append(member_stops[0])
    else:
        # Pick the best canonical stop
        # 1. Prefer major hub
        hub_members = [m for m in member_stops if m.get('is_major_hub', False)]
        if hub_members:
            chosen = hub_members[0]
        else:
            # 2. Check if any matches PREFERRED_NAMES
            chosen = member_stops[0]
            for m in member_stops:
                m_low = m['name'].strip().lower()
                if m_low in PREFERRED_NAMES:
                    chosen = m
                    break
        
        # Determine master name
        c_low = chosen['name'].strip().lower()
        master_name = PREFERRED_NAMES.get(c_low, chosen['name'])
        
        # Coordinate: keep chosen or average if neither is a hub
        if chosen.get('is_major_hub', False):
            master_lat = chosen['latitude']
            master_lon = chosen['longitude']
        else:
            # Keep the one closest to OSM if available, or chosen
            master_lat = chosen['latitude']
            master_lon = chosen['longitude']
            
        total_boardings = sum(m.get('monthly_boardings', 1000) for m in member_stops)
        total_alightings = sum(m.get('monthly_alightings', 950) for m in member_stops)
        is_hub = any(m.get('is_major_hub', False) for m in member_stops)
        
        merged_stops.append({
            'name': master_name,
            'latitude': round(master_lat, 6),
            'longitude': round(master_lon, 6),
            'corridor': chosen.get('corridor', 'Delhi Transit Region'),
            'monthly_boardings': total_boardings,
            'monthly_alightings': total_alightings,
            'is_major_hub': is_hub
        })

print(f"Final pristine merged stops count: {len(merged_stops)}")

# Sort by name
merged_stops.sort(key=lambda s: s['name'])

# Save to stops_meta.json
with open(os.path.join(DATA_DIR, 'stops_meta.json'), 'w', encoding='utf-8') as f:
    json.dump(merged_stops, f, indent=2)

# Save to processed/stop_profiles.json
with open(os.path.join(DATA_DIR, 'processed', 'stop_profiles.json'), 'w', encoding='utf-8') as f:
    json.dump(merged_stops, f, indent=2)

# Save to CSV files
csv_rows = []
for s in merged_stops:
    csv_rows.append({
        'bus_stand_name': s['name'],
        'latitude': s['latitude'],
        'longitude': s['longitude'],
        'corridor': s['corridor'],
        'is_major_hub': 'True' if s['is_major_hub'] else 'False'
    })

fieldnames = ['bus_stand_name', 'latitude', 'longitude', 'corridor', 'is_major_hub']
for cp in [os.path.join(DATA_DIR, 'delhi_bus_stands_coordinates.csv'), os.path.join(BASE_DIR, 'delhi_bus_stands_coordinates.csv')]:
    with open(cp, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

# Update SQLite flowpulse.db
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS stops")
cursor.execute("""
    CREATE TABLE stops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        latitude REAL,
        longitude REAL,
        corridor TEXT,
        monthly_boardings INTEGER,
        monthly_alightings INTEGER,
        is_major_hub BOOLEAN
    )
""")
for s in merged_stops:
    cursor.execute("""
        INSERT OR REPLACE INTO stops (name, latitude, longitude, corridor, monthly_boardings, monthly_alightings, is_major_hub)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (s['name'], s['latitude'], s['longitude'], s['corridor'], s['monthly_boardings'], s['monthly_alightings'], s['is_major_hub']))

conn.commit()
conn.close()
print("All files and SQLite flowpulse.db updated successfully.")
