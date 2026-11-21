import json
import csv
import re
import os
import sqlite3
from math import radians, sin, cos, sqrt, atan2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
DB_PATH = os.path.join(DATA_DIR, 'flowpulse.db')

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def clean_key(s):
    s = s.lower().strip()
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'[^a-z0-9]', ' ', s)
    return ' '.join(s.split())

def root_key(s):
    s = s.lower().strip()
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'[^a-z0-9]', ' ', s)
    stopwords = {'terminal', 'depot', 'crossing', 'stand', 'stop', 'station', 'metro', 'isbt', 'chowk', 'cluster', 'road', 'marg', 'near', 'opp', 'gate', 'village', 'block', 'phase', 'sec', 'sector', 'more', 'mor', 't'}
    return ' '.join([t for t in s.split() if t not in stopwords and len(t) > 2])

# 1. Load GTFS stops (3,465 official Delhi Govt GPS points)
gtfs_exact = {}
gtfs_list = []
with open(os.path.join(DATA_DIR, 'gtfs_delhi_stops.txt'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        name = row['stop_name']
        lat = float(row['stop_lat'])
        lon = float(row['stop_lon'])
        ck = clean_key(name)
        rk = root_key(name)
        item = {'name': name, 'clean': ck, 'root': rk, 'lat': lat, 'lon': lon}
        gtfs_list.append(item)
        if ck not in gtfs_exact:
            gtfs_exact[ck] = []
        gtfs_exact[ck].append(item)

# 2. Authoritative Manual Ground-Truth Coordinates for critical Delhi hubs and stops
MANUAL_EXACT_COORDS = {
    # Yamuna Vihar
    'dtc bus depot yamuna vihar': (28.697906, 77.271192, True),
    'c-4 yamuna vihar': (28.702233, 77.278350, False),
    'b block yamuna vihar': (28.703117, 77.270033, False),
    'yamuna vihar ablock': (28.703117, 77.270033, False),
    
    # Badarpur & MB Road
    'pul prehladpur (badarpur)': (28.5040, 77.2920, False),
    'pul prehladpur': (28.5040, 77.2920, False),
    'prehlad pur': (28.5040, 77.2920, False),
    'badarpur border': (28.4983, 77.3046, True),
    'badarpur border (t)': (28.4983, 77.3046, True),
    'badarpur': (28.4983, 77.3046, True),
    'badarpur m b road / rajiv gandhi stadium': (28.4995, 77.3020, False),
    'maidan garhi crossing (sdm court)': (28.51955, 77.2078, False),
    'mehrauli': (28.5214, 77.1830, True),
    'mehrauli terminal': (28.5214, 77.1830, True),
    'saket crossing': (28.5179, 77.2163, False),
    'saket metro sation / said-ul-ajaib': (28.5190, 77.1990, False),
    'said ul zeb village': (28.5190, 77.1990, False),
    'devoli road crossing': (28.5180, 77.2320, False),
    'khanpur village': (28.5180, 77.2320, False),
    'hamdard nagar / sangam vihar': (28.5126, 77.2485, False),
    'ambedkar nagar terminal': (28.5153, 77.2285, True),
    'ambedkar nagar depot': (28.5153, 77.2285, True),
    'ambedkar nagar terminal / dipsar': (28.5153, 77.2285, True),
    
    # South Delhi & Okhla
    'crpf camp / crown plaza': (28.527867, 77.272383, False),
    'esi hospital okhla': (28.51529, 77.281062, False),
    'okhla depot iv cws ii': (28.51835, 77.284767, True),
    'okhla tank': (28.548017, 77.276567, False),
    'kalkaji depot': (28.539467, 77.266233, True),
    'nehru place terminal': (28.5494, 77.2528, True),
    'nehru place': (28.5485, 77.2515, False),
    'kali mata mandir': (28.5480, 77.2550, False),
    'masjid moth': (28.54085, 77.236067, False),
    'qutub minar metro sation': (28.51415, 77.186167, False),
    'kishan garh': (28.514545, 77.164298, False),
    'masood pur village': (28.525433, 77.154483, False),
    'masood pur dairy': (28.528323, 77.149657, False),
    'khel gaon': (28.55005, 77.210417, False),
    'panchsheel club (sarv priya vihar)': (28.5445, 77.2010, False),
    'aiims': (28.5672, 77.2100, True),
    'safdarjung hospital': (28.5700, 77.2070, True),
    's j hospital': (28.5700, 77.2070, False),
    's.j. hospital': (28.5700, 77.2070, False),
    'munirka': (28.5580, 77.1720, False),
    'munirka village': (28.5580, 77.1720, False),
    'munirka village (t)': (28.5580, 77.1720, True),
    'vasant vihar depot': (28.558917, 77.172067, True),
    
    # West Delhi & Airport
    'palam colony flyover': (28.5835, 77.0870, False),
    'samalkha xing': (28.5290, 77.0980, False),
    'samalkha crossing': (28.5290, 77.0980, False),
    'samalkha village': (28.5290, 77.0980, False),
    'bamnoli crossing': (28.539267, 77.029983, False),
    'dhaula kuan': (28.5921, 77.1614, True),
    'dhaula kuan / aps colony': (28.5921, 77.1614, True),
    'aps colony/ jharera gaon': (28.579967, 77.144817, False),
    'palam airport / igi airport t1': (28.5680, 77.1120, True),
    'igi airport terminal 1': (28.5680, 77.1120, True),
    'igi airport terminal 2': (28.557092, 77.091787, True),
    'igi airport terminal 3': (28.5560, 77.0850, True),
    'igi airport t2 (air india office)': (28.557092, 77.091787, True),
    'cargo / express terminal gate 6': (28.5490, 77.1180, True),
    'najafgarh': (28.6135, 76.9858, True),
    'najafgarh terminal': (28.6135, 76.9858, True),
    'najafgarh delhi gate': (28.6145, 76.9880, False),
    'd block janakpuri': (28.6110, 77.1036, False),
    'desu colony janakpuri': (28.609871, 77.095047, False),
    'desu colony janak puri': (28.609871, 77.095047, False),
    'janak setu': (28.6107, 77.1139, False),
    'sagarpur vashisht park': (28.6091, 77.0996, False),
    'sagar pur vashishth park': (28.6091, 77.0996, False),
    'payal cinema': (28.6314, 77.1384, False),
    'loha mandi': (28.6395, 77.143933, False),
    'maya puri depot': (28.6360, 77.1240, True),
    'mayapuri depot crossing': (28.6360, 77.1240, True),
    'shadipur depot': (28.6510, 77.1550, True),
    'shadi pur depot': (28.6510, 77.1550, True),
    'shadi pur metro station': (28.6515, 77.1570, False),
    'karampura': (28.6560, 77.1480, True),
    'karampura terminal': (28.6560, 77.1480, True),
    'punjabi bagh': (28.6630, 77.1275, False),
    'punjabi bagh terminal': (28.6610, 77.1264, True),
    'punjabi bagh club': (28.6650, 77.1290, False),
    'peera garhi depot': (28.6780, 77.0930, True),
    'peera garhi': (28.6780, 77.0930, False),
    'peera garhi chowk': (28.6780, 77.0930, False),
    'peeragarhi': (28.6780, 77.0930, False),
    'swarn park': (28.6824, 77.0408, False),
    'sultan puri crossing': (28.682317, 77.068783, False),
    'pooth kalan': (28.714233, 77.076917, False),
    'kanjhawala chowk': (28.73725, 77.007217, False),
    'mangol puri b block (orr)': (28.69005, 77.096517, False),
    'b block mangol puri': (28.690217, 77.095183, False),
    'mangol pur school (outer ring road)': (28.6948, 77.106467, False),
    'mangol pur khurd': (28.699967, 77.094383, False),
    
    # North Delhi & GT Karnal Road
    'azadpur': (28.7070, 77.1790, True),
    'azadpur terminal': (28.7070, 77.1790, True),
    'wazirpur depot': (28.692033, 77.153767, True),
    'wazirpur dtc depot / netaji subhash palace': (28.69415, 77.151033, True),
    'ashok vihar crossing': (28.701433, 77.164083, False),
    'richi rich shalimar bagh': (28.701783, 77.164383, False),
    'gtk depot': (28.731117, 77.158967, True),
    'g.t.k depot': (28.731117, 77.158967, True),
    'libas pur gt road': (28.7501, 77.150733, False),
    'swaroop nagar gt road': (28.75805, 77.14765, False),
    'shahbad dairy': (28.7465, 77.0963, False),
    'narela terminal': (28.8530, 77.0920, True),
    'narela': (28.8530, 77.0920, True),
    
    # Central Delhi & Railway Hubs
    'isbt kashmiri gate': (28.6687, 77.2304, True),
    'isbt nityanand marg': (28.6670, 77.2280, True),
    'kashmere gate': (28.6687, 77.2304, True),
    'mori gate terminal': (28.6610, 77.2240, True),
    'mori gate': (28.6610, 77.2240, True),
    'shivaji stadium': (28.6290, 77.2113, True),
    'kendriya terminal / gurudwara rakab gunj': (28.6240, 77.2040, True),
    'kendriya terminal': (28.6240, 77.2040, True),
    'new delhi railway station': (28.6420, 77.2210, True),
    'new delhi railway station gate 2': (28.6430, 77.2240, False),
    'ajmeri gate': (28.6430, 77.2240, False),
    'old delhi railway station': (28.6570, 77.2280, True),
    'sarai kale khan': (28.5886, 77.2530, True),
    'sarai kale khan isbt': (28.5886, 77.2530, True),
    'nizamuddin railway station': (28.5880, 77.2510, True),
    'p s nizamuddin': (28.5870, 77.2475, False),
    'tilak bridge': (28.6260, 77.2420, False),
    'tilak pul': (28.6260, 77.2420, False),
    'meghdoot bhawan': (28.6440, 77.200983, False),
    'telephone exchange': (28.643211, 77.182029, False),
    'prem nursary': (28.5920, 77.2480, False),
    
    # East Delhi & Trans-Yamuna
    'anand vihar isbt': (28.6490, 77.3183, True),
    'anand vihar': (28.6490, 77.3183, True),
    'isbt anand vihar': (28.6490, 77.3183, True),
    'anand vihar isbt main road': (28.6475, 77.3160, True),
    'shahdara terminal': (28.6730, 77.2880, True),
    'shahdara': (28.6730, 77.2880, True),
    'nand nagri depot': (28.7050, 77.3080, True),
    'hasan pur depot': (28.6420, 77.3080, True),
    'seelampur': (28.6650, 77.2750, False),
    'seelam pur': (28.6650, 77.2750, False),
    'new seema puri': (28.6850, 77.3250, True),
    'bhajan pura': (28.6990, 77.2640, False),
    'bhajanpura': (28.6990, 77.2640, False),
    'kalyan puri': (28.6180, 77.3150, False),
    'kalyanpuri': (28.6180, 77.3150, False),
    'mayur vihar phase 1': (28.6040, 77.2940, False),
    'mayur vihar phase 3': (28.6010, 77.3320, True),
    'mother dairy': (28.619267, 77.286067, False),
    'laxmi nagar': (28.6310, 77.2770, False),
    'laxmi nagar (vikas marg) / laxmi nagar metro station': (28.6310, 77.2770, False),
    'shakarpur': (28.633517, 77.282067, False),
    'shakarpur (vikas marg)': (28.633517, 77.282067, False),
    'nirman vihar': (28.6360, 77.2840, False),
    'noida sector 37': (28.5640, 77.3370, True),
    'kalindi kunj border': (28.5440, 77.3120, False)
}

# 3. Load current 429 stops
with open(os.path.join(PROCESSED_DIR, 'stop_profiles.json'), encoding='utf-8') as f:
    stops = json.load(f)

print(f"Aligning {len(stops)} stops with zero synthetic additions...")

updated_count = 0
for s in stops:
    name = s['name']
    cur_lat = s['latitude']
    cur_lon = s['longitude']
    
    k_clean = clean_key(name)
    k_root = root_key(name)
    
    # Priority 1: Check MANUAL_EXACT_COORDS
    matched_exact = False
    if k_clean in MANUAL_EXACT_COORDS:
        lat, lon, is_hub = MANUAL_EXACT_COORDS[k_clean]
        s['latitude'] = lat
        s['longitude'] = lon
        s['is_major_hub'] = is_hub
        matched_exact = True
        updated_count += 1
    elif k_root in MANUAL_EXACT_COORDS:
        lat, lon, is_hub = MANUAL_EXACT_COORDS[k_root]
        s['latitude'] = lat
        s['longitude'] = lon
        s['is_major_hub'] = is_hub
        matched_exact = True
        updated_count += 1
        
    if not matched_exact:
        # Priority 2: Check GTFS exact clean match
        if k_clean in gtfs_exact:
            cands = gtfs_exact[k_clean]
            # Pick candidate closest to current position
            cands.sort(key=lambda g: haversine(cur_lat, cur_lon, g['lat'], g['lon']))
            g = cands[0]
            # Verify sanity (within 12km)
            d = haversine(cur_lat, cur_lon, g['lat'], g['lon'])
            if d < 12.0:
                s['latitude'] = g['lat']
                s['longitude'] = g['lon']
                updated_count += 1
        elif k_root and len(k_root) >= 4:
            # Check GTFS root match
            root_matches = [g for g in gtfs_list if g['root'] == k_root]
            if root_matches:
                root_matches.sort(key=lambda g: haversine(cur_lat, cur_lon, g['lat'], g['lon']))
                g = root_matches[0]
                d = haversine(cur_lat, cur_lon, g['lat'], g['lon'])
                if d < 8.0:
                    s['latitude'] = g['lat']
                    s['longitude'] = g['lon']
                    updated_count += 1

print(f"Successfully verified/updated coordinates for stops: {updated_count} / {len(stops)}")

# 4. Save to processed and root files
with open(os.path.join(PROCESSED_DIR, 'stop_profiles.json'), 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

with open(os.path.join(DATA_DIR, 'stops_meta.json'), 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

# Update CSV files
csv_header = ['stop_name', 'latitude', 'longitude', 'is_major_hub']
with open(os.path.join(DATA_DIR, 'delhi_bus_stands_coordinates.csv'), 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(csv_header)
    for s in stops:
        writer.writerow([s['name'], s['latitude'], s['longitude'], 1 if s.get('is_major_hub') else 0])

with open(os.path.join(BASE_DIR, 'delhi_bus_stands_coordinates.csv'), 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(csv_header)
    for s in stops:
        writer.writerow([s['name'], s['latitude'], s['longitude'], 1 if s.get('is_major_hub') else 0])

# Update SQLite Database
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for s in stops:
        cur.execute("""
            UPDATE stops 
            SET latitude = ?, longitude = ?, is_major_hub = ?
            WHERE name = ?
        """, (s['latitude'], s['longitude'], 1 if s.get('is_major_hub') else 0, s['name']))
    conn.commit()
    conn.close()

print("All metadata files and SQLite database successfully updated!")
