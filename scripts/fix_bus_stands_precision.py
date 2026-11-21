import json
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
DB_PATH = os.path.join(DATA_DIR, 'flowpulse.db')

# Ground-truth verified coordinates for all true major bus stands & terminals in Delhi
VERIFIED_MAJOR_TERMINALS = {
    # ISBTs
    'isbt kashmiri gate': (28.6685, 77.2295, 'Kashmere Gate Terminal'),
    'kashmere gate isbt': (28.6685, 77.2295, 'Kashmere Gate Terminal'),
    'isbt nityanand marg': (28.6670, 77.2280, 'Kashmere Gate Terminal'),
    'kashmere gate': (28.6675, 77.2285, 'Kashmere Gate Terminal'),
    'anand vihar isbt': (28.6469, 77.3160, 'East Interstate Transit Hub (ISBT)'),
    'isbt anand vihar': (28.6469, 77.3160, 'East Interstate Transit Hub (ISBT)'),
    'anand vihar isbt main road': (28.6469, 77.3160, 'East Interstate Transit Hub (ISBT)'),
    'sarai kale khan isbt': (28.5886, 77.2530, 'Ring Road East Hub'),
    'sarai kale khan': (28.5886, 77.2530, 'Ring Road East Hub'),
    
    # Major Bus Terminals
    'mehrauli terminal': (28.5195, 77.1818, 'South Mehrauli Corridor'),
    'badarpur border (t)': (28.4984, 77.3045, 'Mathura Road / Faridabad Border'),
    'badarpur border(t)': (28.4984, 77.3045, 'Mathura Road / Faridabad Border'),
    'badarpur border': (28.4984, 77.3045, 'Mathura Road / Faridabad Border'),
    'shivaji stadium': (28.6304, 77.2177, 'Central Bus Terminal'),
    'kendriya terminal / gurudwara rakab gunj': (28.6240, 77.2040, 'Central Bus Terminal'),
    'nehru place terminal': (28.5494, 77.2528, 'Outer Ring Road Hub'),
    'ambedkar nagar terminal': (28.5262, 77.2346, 'BRT Corridor'),
    'ambedkar nagar terminal / dipsar': (28.5262, 77.2346, 'BRT Corridor'),
    'ambedkar nagar depot': (28.5262, 77.2346, 'BRT Corridor'),
    'azadpur terminal': (28.7070, 77.1790, 'GT Karnal Agricultural Hub'),
    'mori gate terminal': (28.6610, 77.2240, 'North Corridor Terminal'),
    'najafgarh terminal': (28.6120, 76.9850, 'South-West Rural Hub'),
    'uttam nagar terminal': (28.6220, 77.0560, 'West Corridor Hub'),
    'uttam nagar terminal (out gate)': (28.6220, 77.0560, 'West Corridor Hub'),
    'shahdara terminal': (28.6730, 77.2880, 'Trans-Yamuna North Hub'),
    'shahdara': (28.6730, 77.2880, 'Trans-Yamuna North Hub'),
    'karampura terminal': (28.6560, 77.1480, 'West Corridor'),
    'punjabi bagh terminal': (28.6610, 77.1264, 'West Ring Road Hub'),
    'narela terminal': (28.8530, 77.0920, 'North Border Terminal'),
    'dwarka more metro station (terminal)': (28.6190, 77.0330, 'West Sub-city Hub'),
    'munirka village (t)': (28.5580, 77.1720, 'Ring Road South'),
    'chauhan patti (terminal)': (28.7380, 77.2340, 'Burari Yamuna Border'),
    'qamruddin nagar terminal': (28.6790, 77.0520, 'Outer Ring Road West'),
    'cargo / express terminal gate 6': (28.5490, 77.1180, 'Airport Sector'),

    # DTC Bus Depots
    'wazirpur depot': (28.6980, 77.1620, 'North-West Industrial'),
    'wazirpur dtc depot / netaji subhash palace': (28.6980, 77.1620, 'North-West Industrial'),
    'maya puri depot': (28.6360, 77.1240, 'West Industrial'),
    'mayapuri depot crossing': (28.6360, 77.1240, 'West Industrial'),
    'kalkaji depot': (28.5520, 77.2610, 'Outer Ring Road East'),
    'nand nagri depot': (28.7050, 77.3080, 'North-East Depot Hub'),
    'peera garhi depot': (28.6780, 77.0930, 'Outer Ring Road West'),
    'hasan pur depot': (28.6420, 77.3080, 'East Delhi Depot Hub'),
    'shadipur depot': (28.6510, 77.1550, 'West Corridor'),
    'shadi pur depot': (28.6510, 77.1550, 'West Corridor'),
    'g.t.k depot': (28.7180, 77.1680, 'GT Karnal Corridor Depot'),
    'gtk depot': (28.7180, 77.1680, 'GT Karnal Corridor Depot'),
    'vasant vihar depot': (28.5580, 77.1580, 'South-West Arterial'),

    # Key Inter-Modal Transit Hubs (Major Railway & Ring Road Intercepts)
    'new delhi railway station': (28.6420, 77.2210, 'Central Transit Sector'),
    'old delhi railway station': (28.6570, 77.2280, 'Old Delhi Sector'),
    'nizamuddin railway station': (28.5886, 77.2530, 'Ring Road East Hub'),
    'dhaula kuan': (28.5921, 77.1614, 'Ring Road / Airport Hub'),
    'aiims': (28.5672, 77.2100, 'Ring Road Medical Corridor'),
    'safdarjung hospital': (28.5700, 77.2080, 'Ring Road Medical Corridor'),
    'connaught place': (28.6315, 77.2167, 'Central Delhi CBD')
}

# Corrections for misaligned stop coordinates
SPECIFIC_STOP_CORRECTIONS = {
    'nangloi (najafgarh road)': (28.6820, 77.0650, 'West Corridor (Nangloi Rohtak Road)'),
    'palam airport / igi airport t1': (28.5680, 77.1120, 'IGI Airport Terminal 1'),
    'iit gate': (28.5440, 77.1930, 'Outer Ring Road South'),
    'hauz khas': (28.5435, 77.2060, 'Outer Ring Road South'),
    'saket metro station': (28.5204, 77.2015, 'Mehrauli-Badarpur Corridor'),
    'malviya nagar': (28.5280, 77.2060, 'South Delhi Sector'),
    'lajpat nagar': (28.5700, 77.2400, 'Ring Road South'),
    'ito': (28.6290, 77.2490, 'Institutional East Arterial'),
    'ito ring road': (28.6290, 77.2490, 'Institutional East Arterial'),
    'delhi gate': (28.6360, 77.2430, 'Old Delhi Southern Gate'),
    'ashram': (28.5700, 77.2550, 'Ring Road East Hub')
}

# Load current stops
stops_file = os.path.join(PROCESSED_DIR, 'stop_profiles.json')
with open(stops_file, 'r', encoding='utf-8') as f:
    stops = json.load(f)

updated_stops = []
hub_count = 0
stop_count = 0

for s in stops:
    name_clean = s['name'].strip()
    name_low = name_clean.lower()

    # 1. Check if it is a verified major terminal/hub
    is_hub = False
    for t_name, (t_lat, t_lon, t_corr) in VERIFIED_MAJOR_TERMINALS.items():
        if name_low == t_name or (len(t_name) > 6 and t_name in name_low):
            s['latitude'] = t_lat
            s['longitude'] = t_lon
            s['corridor'] = t_corr
            is_hub = True
            break
    
    # 2. Check for specific stop location corrections
    for c_name, (c_lat, c_lon, c_corr) in SPECIFIC_STOP_CORRECTIONS.items():
        if name_low == c_name or (len(c_name) > 6 and c_name in name_low):
            s['latitude'] = c_lat
            s['longitude'] = c_lon
            s['corridor'] = c_corr
            break

    s['is_major_hub'] = is_hub
    if is_hub:
        hub_count += 1
    else:
        stop_count += 1

    updated_stops.append(s)

print(f"Total stops processed: {len(updated_stops)}")
print(f"True Major Bus Stands (Black Dots, is_hub=True): {hub_count}")
print(f"Regular Bus Stops (Blue Dots, is_hub=False): {stop_count}")

# Save updated stop_profiles.json
with open(stops_file, 'w', encoding='utf-8') as f:
    json.dump(updated_stops, f, indent=2, ensure_ascii=False)
print(f"Updated: {stops_file}")

# Save stops_meta.json
meta_file = os.path.join(DATA_DIR, 'stops_meta.json')
with open(meta_file, 'w', encoding='utf-8') as f:
    json.dump(updated_stops, f, indent=2, ensure_ascii=False)
print(f"Updated: {meta_file}")

# Update SQLite Database
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for s in updated_stops:
        cur.execute("""
            UPDATE stops 
            SET latitude = ?, longitude = ?, corridor = ?, is_major_hub = ?
            WHERE name = ?
        """, (s['latitude'], s['longitude'], s['corridor'], 1 if s['is_major_hub'] else 0, s['name']))
    conn.commit()
    conn.close()
    print(f"Updated SQLite database: {DB_PATH}")

print("Ground-truth bus stands precision fix completed!")
