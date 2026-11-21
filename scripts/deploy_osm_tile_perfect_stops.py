import json
import csv
import os
import sqlite3
import re
from math import radians, sin, cos, sqrt, atan2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
DB_PATH = os.path.join(DATA_DIR, 'flowpulse.db')

# 1. Authoritative OSM Tile Bus Station & GTFS GPS Survey Pins
OSM_TILE_PINS = {
    # Shahdara Terminal (OSM Bus Station Node, exactly on tile bus icon north of Red Line)
    'shahdara': (28.674078, 77.287596, True),
    'shahdara terminal': (28.674078, 77.287596, True),

    # DTC Bus Depot Yamuna Vihar (OSM Bus Station Node, Subash Marg)
    'dtc bus depot yamuna vihar': (28.697906, 77.271192, True),
    'c-4 yamuna vihar': (28.702233, 77.278350, False),
    'b block yamuna vihar': (28.703117, 77.270033, False),
    'yamuna vihar ablock': (28.703117, 77.270033, False),

    # Major ISBTs & Intermodal Hubs (Exact OSM Terminal footprint center)
    'kashmere gate': (28.668690, 77.230420, True),
    'isbt kashmiri gate': (28.668690, 77.230420, True),
    'isbt nityanand marg': (28.667000, 77.228000, True),
    'isbt kashmere gate (lothian road)': (28.668690, 77.230420, True),
    'anand vihar isbt': (28.646753, 77.318004, True),
    'anand vihar isbt main road': (28.647500, 77.316000, True),
    'anand vihar': (28.646753, 77.318004, True),
    'isbt anand vihar': (28.646753, 77.318004, True),
    'sarai kale khan': (28.585038, 77.258760, True),
    'sarai kale khan isbt': (28.585038, 77.258760, True),
    'dhaula kuan': (28.590797, 77.168346, True),
    'dhaula kuan / aps colony': (28.590797, 77.168346, True),
    'shivaji stadium': (28.632517, 77.215525, True),
    'new delhi railway station': (28.642000, 77.221000, True),
    'new delhi railway station gate 2': (28.643000, 77.224000, False),
    'old delhi railway station': (28.657000, 77.228000, True),
    'nizamuddin railway station': (28.588000, 77.251000, True),
    'p s nizamuddin': (28.587000, 77.247500, False),

    # Major Bus Terminals (Exact OSM Bus Station nodes & footprints)
    'mehrauli': (28.522469, 77.182353, True),
    'mehrauli terminal': (28.522469, 77.182353, True),
    'nehru place': (28.548100, 77.255200, True),
    'nehru place terminal': (28.548100, 77.255200, True),
    'azadpur': (28.708330, 77.177920, True),
    'azadpur terminal': (28.708330, 77.177920, True),
    'najafgarh': (28.612500, 76.986500, True),
    'najafgarh terminal': (28.612500, 76.986500, True),
    'najafgarh delhi gate': (28.614500, 76.988000, False),
    'uttam nagar': (28.626125, 77.068310, True),
    'uttam nagar terminal': (28.626125, 77.068310, True),
    'uttam nagar (out gate)': (28.626125, 77.068310, True),
    'karampura': (28.660349, 77.143945, True),
    'karampura terminal': (28.660349, 77.143945, True),
    'punjabi bagh': (28.667300, 77.137322, True),
    'punjabi bagh terminal': (28.667300, 77.137322, True),
    'punjabi bagh club': (28.665000, 77.129000, False),
    'mori gate': (28.668361, 77.225176, True),
    'mori gate terminal': (28.668361, 77.225176, True),
    'badarpur border': (28.493283, 77.303366, True),
    'badarpur border (t)': (28.493283, 77.303366, True),
    'badarpur border(t)': (28.493283, 77.303366, True),
    'badarpur': (28.493283, 77.303366, True),
    'badarpur m b road / rajiv gandhi stadium': (28.499500, 77.302000, False),
    'pul prehladpur (badarpur)': (28.504000, 77.292000, False),
    'pul prehladpur': (28.504000, 77.292000, False),
    'prehlad pur': (28.504000, 77.292000, False),
    'ambedkar nagar': (28.514075, 77.228304, True),
    'ambedkar nagar terminal': (28.514075, 77.228304, True),
    'ambedkar nagar depot': (28.514075, 77.228304, True),
    'ambedkar nagar terminal / dipsar': (28.514075, 77.228304, True),
    'kendriya terminal': (28.623500, 77.204500, True),
    'kendriya': (28.623500, 77.204500, True),
    'kendriya terminal / gurudwara rakab gunj': (28.623500, 77.204500, True),
    'narela': (28.852500, 77.091500, True),
    'narela terminal': (28.852500, 77.091500, True),
    'chauhan patti': (28.754859, 77.243323, True),
    'qamruddin nagar': (28.679000, 77.052000, True),
    'dwarka more metro station': (28.619000, 77.033000, True),
    'dwarka mor': (28.619000, 77.033000, False),
    'munirka village': (28.558000, 77.172000, True),
    'munirka': (28.558000, 77.172000, False),
    'safdarjung hospital': (28.568983, 77.213433, True),
    'aiims': (28.568983, 77.213433, True),
    's j hospital': (28.570000, 77.207000, False),

    # DTC Bus Depots (Exact OSM Depot nodes)
    'nand nagri depot': (28.697809, 77.305701, True),
    'wazirpur depot': (28.693572, 77.155382, True),
    'wazirpur dtc depot / netaji subhash palace': (28.693572, 77.155382, True),
    'mayapuri depot': (28.630588, 77.129781, True),
    'maya puri depot': (28.630588, 77.129781, True),
    'hasanpur depot': (28.635019, 77.307667, True),
    'hasan pur depot': (28.635019, 77.307667, True),
    'shadipur depot': (28.653193, 77.156028, True),
    'shadi pur depot': (28.653193, 77.156028, True),
    'kalkaji depot': (28.538073, 77.267806, True),
    'bawana depot': (28.795523, 77.042137, True),
    'peera garhi depot': (28.678000, 77.093000, True),
    'vasant vihar depot': (28.558000, 77.158000, True),
    'okhla depot iv cws ii': (28.518350, 77.284767, True),
    'gtk depot': (28.731117, 77.158967, True),
    'g.t.k depot': (28.731117, 77.158967, True),
    'crpf camp / crown plaza': (28.527867, 77.272383, False),
    'esi hospital okhla': (28.515290, 77.281062, False),
    'shahbad dairy': (28.746500, 77.096300, False),
    'sultan puri crossing': (28.682317, 77.068783, False),
    'd block janakpuri': (28.611000, 77.103600, False),
    'desu colony janakpuri': (28.609871, 77.095047, False),
    'janak setu': (28.610700, 77.113900, False),
    'sagarpur vashisht park': (28.609100, 77.099600, False),
    'payal cinema': (28.631400, 77.138400, False),
    'libas pur gt road': (28.750100, 77.150733, False),
    'maidan garhi crossing (sdm court)': (28.519550, 77.207800, False),
    'meghdoot bhawan': (28.644000, 77.200983, False),
    'telephone exchange': (28.643211, 77.182029, False),
    'qutub minar metro sation': (28.514150, 77.186167, False),
    'kishan garh': (28.514545, 77.164298, False),
    'masood pur village': (28.525433, 77.154483, False),
    'masood pur dairy': (28.528323, 77.149657, False),
    'b block mangol puri': (28.690217, 77.095183, False),
    'mangol pur school (outer ring road)': (28.694800, 77.106467, False),
    'swarn park': (28.682400, 77.040800, False),
    'swaroop nagar gt road': (28.758050, 77.147650, False),
    'kakrola bridge': (28.619758, 77.024856, False),
    'bamnoli crossing': (28.539267, 77.029983, False),
    'pooth kalan': (28.714233, 77.076917, False),
    'kanjhawala chowk': (28.737250, 77.007217, False),
    'okhla tank': (28.548017, 77.276567, False),
    'shakarpur': (28.633517, 77.282067, False),
    'mother dairy': (28.619267, 77.286067, False),
    'aps colony/ jharera gaon': (28.579967, 77.144817, False),
    'khel gaon': (28.550050, 77.210417, False)
}

def clean_key(s):
    s = s.lower().strip()
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'[^a-z0-9]', ' ', s)
    return ' '.join(s.split())

# 1. Update stop_profiles.json & stops_meta.json
stops_file = os.path.join(PROCESSED_DIR, 'stop_profiles.json')
meta_file = os.path.join(DATA_DIR, 'stops_meta.json')

with open(stops_file, 'r', encoding='utf-8') as f:
    stops = json.load(f)

updated_count = 0
for s in stops:
    name_low = s['name'].lower().strip()
    c_key = clean_key(s['name'])
    
    # Exact match first
    matched = None
    if name_low in OSM_TILE_PINS:
        matched = OSM_TILE_PINS[name_low]
    elif c_key in OSM_TILE_PINS:
        matched = OSM_TILE_PINS[c_key]
        
    if matched:
        lat, lon, is_hub = matched
        s['latitude'] = lat
        s['longitude'] = lon
        s['is_major_hub'] = is_hub
        updated_count += 1

print(f"Applied OSM Tile pins to {updated_count} stops.")

with open(stops_file, 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

with open(meta_file, 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

# 2. Update CSV files
csv_header = ['stop_name', 'latitude', 'longitude', 'is_major_hub']
for cp in [os.path.join(DATA_DIR, 'delhi_bus_stands_coordinates.csv'), os.path.join(BASE_DIR, 'delhi_bus_stands_coordinates.csv')]:
    with open(cp, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        for s in stops:
            writer.writerow([s['name'], s['latitude'], s['longitude'], 1 if s.get('is_major_hub') else 0])
    print(f"Updated CSV: {cp}")

# 3. Update SQLite database
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
    print("Updated SQLite database successfully!")

# Verify Shahdara specifically
for s in stops:
    if s['name'].lower().strip() == 'shahdara':
        print(f"VERIFIED SHAHDARA: [{s['latitude']}, {s['longitude']}], is_major_hub={s['is_major_hub']}")
