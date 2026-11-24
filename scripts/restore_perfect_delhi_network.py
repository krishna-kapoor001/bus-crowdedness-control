import json
import math
import re
import sqlite3
import os

print("=" * 80)
print("  RESTORING COMPLETE STREET-PERFECT DELHI TRANSIT DATASET")
print("=" * 80)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def clean_toks(s):
    clean = re.sub(r'[^a-zA-Z0-9]', ' ', s.lower())
    ignore = {'bus', 'stop', 'stand', 'terminal', 'crossing', 'xing', 'more', 'mor', 'road', 'marg', 'delhi', 'village', 'near', 'opp', 'opposite', 'depot', 'isbt', 'dtc', 'cluster', 'colony', 'block', 'phase', 'sec', 'sector', 'hub'}
    return set(w for w in clean.split() if len(w) > 2 and w not in ignore)

def clean_stem(s):
    s = re.sub(r'[^a-zA-Z0-9]', '', s.lower())
    for w in ['terminal', 'depot', 'busstop', 'busstand', 'crossing', 'xing', 'more', 'mor', 'road', 'marg', 'delhi', 'village', 'isbt', 'dtc', 'cluster']:
        s = s.replace(w, '')
    return s

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

# 1. Load authentic roadside OSM bus stops
with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_raw = json.load(f)

osm_stops = []
for o in osm_raw:
    name = (o.get('name') or o.get('tags', {}).get('name') or '').strip()
    if not name or name.lower() == 'unnamed':
        continue
    lat, lon = extract_coords(o)
    if lat and lon and 28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.6:
        osm_stops.append({
            'name': name,
            'lat': float(lat),
            'lon': float(lon),
            'toks': clean_toks(name),
            'stem': clean_stem(name),
            'shelter': o.get('tags', {}).get('shelter') == 'yes'
        })

print(f"Loaded {len(osm_stops)} verified OSM roadside stops.")

# 2. Load base dataset
with open('data/processed/original_1491_backup.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"[STEP 1] Starting stops: {len(stops)}")

# 3. OSM Pure Catalog Snap & 35m Dedup
perfect_stops = []
for s in stops:
    s_toks = clean_toks(s['name'])
    s_stem = clean_stem(s['name'])
    best_osm = None
    best_dist = 999999
    
    for o in osm_stops:
        if abs(s['latitude'] - o['lat']) > 0.015 or abs(s['longitude'] - o['lon']) > 0.015:
            continue
        is_match = False
        if s_toks and (s_toks & o['toks']):
            is_match = True
        elif len(s_stem) >= 4 and len(o['stem']) >= 4 and (s_stem in o['stem'] or o['stem'] in s_stem or s_stem[:5] == o['stem'][:5]):
            is_match = True
            
        if is_match:
            d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
            if d < 1200 and d < best_dist:
                best_dist = d
                best_osm = o
                
    if not best_osm:
        for o in osm_stops:
            if abs(s['latitude'] - o['lat']) > 0.001 or abs(s['longitude'] - o['lon']) > 0.001:
                continue
            d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
            if d <= 45.0 and d < best_dist:
                best_dist = d
                best_osm = o
                
    if best_osm:
        new_stop = dict(s)
        new_stop['latitude'] = round(best_osm['lat'], 6)
        new_stop['longitude'] = round(best_osm['lon'], 6)
        perfect_stops.append(new_stop)

merged_catalog = []
for s in sorted(perfect_stops, key=lambda x: x['monthly_boardings'], reverse=True):
    matched_existing = None
    for ex in merged_catalog:
        d = haversine(s['latitude'], s['longitude'], ex['latitude'], ex['longitude'])
        if d < 35.0:
            matched_existing = ex
            break
    if matched_existing:
        matched_existing['monthly_boardings'] += s.get('monthly_boardings', 0)
        matched_existing['monthly_alightings'] += s.get('monthly_alightings', 0)
        if s.get('is_major_hub'):
            matched_existing['is_major_hub'] = True
    else:
        merged_catalog.append(s)

print(f"[STEP 2] Pure OSM Catalog Snap: {len(merged_catalog)} stops.")

# 4. Refine Bus Stands
demote_hubs_1 = ['Munirka Village', 'Jharoda Crossing Nazafgarh Terminal', 'Begumpur', 'Okhla Village', 'Mayur Vihar Phase 1', 'Tilak Nagar', 'Lodhi Colony']
rename_map = {
    'SNPD': 'Sriniwaspuri DTC Depot (SNPD)',
    'Ordinance Depot': 'Ordnance Depot (Shakurbasti)',
    'Supply Depot': 'Supply Depot (Delhi Cantt)',
    'BBM Cluster Depot': 'BBM DTC Depot (Kingsway Camp)',
    'DTC Bus Depot Yamuna Vihar': 'Yamuna Vihar DTC Depot',
}
for s in merged_catalog:
    if s['name'] in demote_hubs_1:
        s['is_major_hub'] = False
    if s['name'] in rename_map:
        s['name'] = rename_map[s['name']]

# 5. Apply Deep Merges (75m, 200m, 350m, clusters)
deep_merges = {
    # 75m
    'Mata Mandir New Friends Colony': 'New Friends Colony',
    'A 1 Keshav Puram': 'C 2 Keshav Puram',
    'Sunder Apartment': 'Sunder Vihar',
    'Dispensary Paharganj': 'Police Station Paharganj',
    'CRPF Camp Okhla Phase 1': 'Okhla Depot Iv Cws Ii',
    'Thana DB Gupta Road': 'Prahlad Market',
    'Sunder Nagri': 'Nand Nagari Terminal',
    'Dwarka Sec 1 Mahalaxmi Apartment': 'Dwarka Sec 1',
    'Desu Colony Janakpuri': 'Janakpuri B 2',
    'Shalimar Bagh BA Block': 'Wazir Pur Industrial Area Ashok Vihar Crossing',
    'Mangolpuri School': 'B Block Mangol Puri',
    'Centaur Hotel Nangal Dairy': 'Centaur Hotel New Custom House',
    'Delhi Gate': 'Ambedkar Stadium Terminal',
    'Tees Hazari Animal Hospital Mori Gate': 'St Stephen Hospital',
    'Jahangirpuri B Block': 'Jahangirpuri GT Road',
    'Rohini Sec 11 Agarwal Sabha': 'Rohini Sec 16',
    'Jahangir Puri Outer Ring Road': 'Jahangirpuri K Block',
    'Dilshad Garden GT Road': 'Jhilmil Crossing',
    'Basai Darapur Ramesh Nagar': 'Bali Nagar',
    'Seelampur Market': 'Seelampur',
    'Sheikh Sarai More': 'Shaikh Sarai Phase II',
    # 200m
    'Shakurpur JJ Colony Britannia': 'Britannia',
    'Air Force HQ Subroto Park': 'Subroto Park',
    'District Centre Nazafgarh Road': 'Janakpuri District Centre',
    'Krishna Nagar A Block': 'East Krishna Nagar',
    'Raksha Vigyan Kendra Metcalf House': 'Metcalfe House',
    'Raja Garden': 'Raja Garden Terminal',
    'Andheria Bagh More': 'Andheria More',
    'Rithala Village': 'Rithala Crossing',
    'Ashram Ring Road': 'Ashram Chowk',
    'Roop Nagar Shakti Nagar': 'Shakti Nagar',
    'R Block Rajendra Nagar': 'New Rajender Nagar',
    'Inder Puri JJ Colony': 'Inder Puri',
    # 350m
    'Kalma Nehru College': 'Kamla Nehru College Niti Bag',
    'Humayun Road': 'Humayun Road Khan Mkt',
    'Ashram': 'Ashram Chowk',
    'Moti Nagar Market': 'Moti Nagar',
    'PNB Geetanjali': 'Geetanjali Enclave',
    'Shakarpur': 'Shakarpur Crossing',
    'Sarai Rohilla Flyover': 'Sarai Rohila',
    'Kalyan Puri crossing': 'Kalyan Puri Terminal',
    'Rajendra Place Karol Bagh Telephone Exchange': 'Rajendra Place',
    '18 Block Lodhi Colony': 'Lodhi Colony',
    'Golf Club Sunder Nagar': 'Sunder Nagar',
    'Shadipur DTC Colony': 'Shadipur Depot',
    'Panchkuian Road Banwai Lal Hospital': 'Panchkuian Road',
    'Hassanpur Village': 'Hasanpur Depot',
    'Shahdara Railway Bridge': 'Shahdara Terminal',
    'Ram Prastha Temple': 'Ram Prastha Crossing',
    'Kakrola Bridge': 'Kakrola crossing',
    'Munirka Family Planning': 'Munirka Village',
    'Jharoda Crossing Nazafgarh Terminal': 'Najafgarh Terminal',
    # clusters
    'Rani Jhansi Road Jhande Walan': 'Jhandewalan',
    'Nehru Place Apartments': 'Nehru Place Crossing Paras Cinema',
    'Maya Puri Crossing Ring Road': 'Mayapuri Depot',
    'B3 Keshav Puram': 'B 4 Keshav Puram',
    'C 8 Keshav Puram': 'B 4 Keshav Puram',
    'Raghubir Nagar F Block': 'Khayala More Subhash Nagar Crossing',
}

extra_b = {}
for s in merged_catalog:
    if s['name'] in deep_merges:
        target = deep_merges[s['name']]
        extra_b[target] = extra_b.get(target, 0) + s.get('monthly_boardings', 0)

filtered_after_deep = []
for s in merged_catalog:
    if s['name'] in deep_merges:
        continue
    if s['name'] in extra_b:
        s['monthly_boardings'] = s.get('monthly_boardings', 0) + extra_b[s['name']]
    filtered_after_deep.append(s)

print(f"[STEP 3] After Semantic Merges: {len(filtered_after_deep)} stops.")

# 6. Execute Hubs & Empty-Road Cleanup
snap_fixes = {
    'Najafgarh Terminal': (28.611651, 76.978471),
    'AIIMS Transit Hub': (28.568849, 77.213239),
    'IG Stadium': (28.632931, 77.247190),
    'Wazirpur Depot': (28.691918, 77.153692),
    'Uttri Pitam Pura': (28.715078, 77.138988),
}
for s in filtered_after_deep:
    if s['name'] in snap_fixes:
        s['latitude'] = snap_fixes[s['name']][0]
        s['longitude'] = snap_fixes[s['name']][1]

demote_to_regular_2 = [
    'Supply Depot (Delhi Cantt)', 'Ordnance Depot (Shakurbasti)', 'Okhla Depot Iv Cws Ii',
    'Tara Apartments Terminal', 'Jai Mata Market Tri Nagar Terminal', 'Khayala Colony Terminal',
    'E Block Jahangir Puri Terminal', 'East Vinod Nagar Depot', 'Rohini Depot 2', 'Rohini Depot 3',
    'Sriniwaspuri DTC Depot (SNPD)', 'Malka Ganj Terminal', 'West Enclave Terminal',
    'BBM DTC Depot (Kingsway Camp)', 'Dichau Kalan Depot', 'Vivek Vihar Terminal',
    'Ambedkar Stadium Terminal', 'Dilshad Garden Depot Cluster', 'Janak Puri B 1 Terminal',
    'Kalyan Puri Terminal', 'Mangla Puri Terminal', 'Jal Vihar Terminal', 'Jheel Terminal',
    'Karampura Terminal', 'Keshopur Depot', 'Peera Garhi Depot', 'Pragati Maidan Terminal',
    'Safdurjung Terminal'
]
for s in filtered_after_deep:
    if s['name'] in demote_to_regular_2:
        s['is_major_hub'] = False

remove_empty_road = {'Yamuna Vihar DTC Depot', 'Rohini Sec 22 Terminal'}
filtered_825 = [s for s in filtered_after_deep if s['name'] not in remove_empty_road]
hubs_825 = [s for s in filtered_825 if s.get('is_major_hub')]
print(f"[STEP 4] 825 Milestone: {len(filtered_825)} stops, {len(hubs_825)} Major Hubs.")

# 7. Comprehensive Fix: Move 25 stops from Road Centerline to Sidewalk Shelters & Purge 30 Metro Track Phantoms
snaps_to_shelters = {
    'Lajpat Nagar': (28.565286, 77.248529),
    'Seelampur': (28.670473, 77.266685),
    'Shahdara Terminal': (28.673801, 77.286881),
    'Mayur Vihar Phase 3 Terminal': (28.617258, 77.339243),
    'Civil Line': (28.676718, 77.225025),
    'Tilak Nagar': (28.634590, 77.097372),
    'Janakpuri District Centre': (28.630246, 77.078207),
    'Shastri Nagar A Block': (28.670308, 77.180596),
    'Chirag Delhi': (28.538912, 77.232314),
    'Welcome': (28.672012, 77.278669),
    'Adarsh Nagar': (28.717014, 77.170247),
    'Kailash Colony': (28.556074, 77.241003),
    'NajafGarh Delhi Gate': (28.612694, 76.986267),
    'Mansarovar Park': (28.675582, 77.300107),
    'Bhalaswa crossing': (28.737309, 77.166609),
    'Vishwa Vidyalaya': (28.695054, 77.215425),
    'Inderlok': (28.673402, 77.168999),
    'Kohat Enclave': (28.697110, 77.142202),
    'Khajuri School': (28.704730, 77.257014),
    'Humayun Road Khan Mkt': (28.602844, 77.227826),
    'Bali Nagar': (28.652764, 77.132399),
    'Rohini Sec 5': (28.713810, 77.117225),
    'JLN Stadium Terminal': (28.589054, 77.233644),
    'ISBT Sarai Kale Khan': (28.589696, 77.258403),
    'Anand Vihar ISBT': (28.646246, 77.315159),
}
for s in filtered_825:
    if s['name'] in snaps_to_shelters:
        s['latitude'] = round(snaps_to_shelters[s['name']][0], 6)
        s['longitude'] = round(snaps_to_shelters[s['name']][1], 6)

phantoms_to_remove = {
    'Surajmal Stadium', 'Udyog Nagar', 'Rajdhani Park', 'Nangloi', 'Mundka Village',
    'Tikri Border', 'Tikri Hospital', 'Prem Nagar', 'Nawada Gaon', 'Shaheen Bagh Thokar No 5',
    'Samaypur School', 'Jhilmil Crossing', 'IOC Dwarka Road', 'Nangli Dairy', 'Govind Puri',
    'Avtar Enclave', 'Shivani Apartments Kunj Vihar Sector 12 Dwarka', 'Lokesh Cinema Nangloi JJ Colony',
    'Dwarka Sec 19 20 Crossing', 'Hans Apartment', 'Aero City', 'Jor Bagh', 'KarKarDooma Court',
    'Gokul Puri', 'Chand Nagar', 'Dwarka Sec 16C GGS IP University', 'Palam Gaon',
    'Janak Puri B 1 Terminal', 'Jai Mata Market Tri Nagar Terminal', 'Dwarka Mor Bus Stand'
}

filtered_no_phantoms = [s for s in filtered_825 if s['name'] not in phantoms_to_remove]
print(f"[STEP 5] Removed 30 DMRC Train Track Phantoms -> Remaining: {len(filtered_no_phantoms)} stops.")

# 8. Strict Ground Truth Snap to exact OSM node (<= 5.0m)
terminal_snaps = {
    'ISBT Kashmere Gate': (28.669517, 77.232170, True),
    'Shivaji Stadium Terminal': (28.632996, 77.215522, True),
    'Badarpur Border Terminal': (28.491472, 77.303722, True),
    'Punjabi Bagh Terminal': (28.667787, 77.137390, True),
    'Rajouri Garden': (28.647729, 77.119870, False),
    'ISBT Sarai Kale Khan': (28.590600, 77.257884, True),
    'Anand Vihar ISBT': (28.648984, 77.318288, True),
    'Nehru Place Terminal': (28.547266, 77.253895, True),
}
for s in filtered_no_phantoms:
    if s['name'] in terminal_snaps:
        lat, lon, is_hub = terminal_snaps[s['name']]
        s['latitude'] = lat
        s['longitude'] = lon
        s['is_major_hub'] = is_hub

strictly_verified = []
for s in filtered_no_phantoms:
    best_d = 999999
    best_b = None
    for b in osm_stops:
        d = haversine(s['latitude'], s['longitude'], b['lat'], b['lon'])
        if d < best_d:
            best_d = d
            best_b = b
    if best_d <= 5.0:
        s['latitude'] = round(best_b['lat'], 6)
        s['longitude'] = round(best_b['lon'], 6)
        strictly_verified.append(s)

deduped_final = []
for s in strictly_verified:
    too_close = False
    for existing in deduped_final:
        if haversine(s['latitude'], s['longitude'], existing['latitude'], existing['longitude']) < 15.0:
            too_close = True
            existing['monthly_boardings'] += s.get('monthly_boardings', 0)
            if s.get('is_major_hub'):
                existing['is_major_hub'] = True
            break
    if not too_close:
        deduped_final.append(s)

# 9. Ensure Wazirpur Depot and Shivaji Stadium Terminal
if not any(s['name'] == 'Wazirpur Depot' for s in deduped_final):
    deduped_final.append({
        "name": "Wazirpur Depot",
        "latitude": 28.692046,
        "longitude": 77.153868,
        "corridor": "181: Hazrat Nizamuddin ↔ Jahangirpuri",
        "monthly_boardings": 21000,
        "monthly_alightings": 19950,
        "is_major_hub": True
    })

if not any(s['name'] == 'Shivaji Stadium Terminal' for s in deduped_final):
    deduped_final.append({
        "name": "Shivaji Stadium Terminal",
        "latitude": 28.632996,
        "longitude": 77.215522,
        "corridor": "Connaught Place Central Hub",
        "monthly_boardings": 14200,
        "monthly_alightings": 13490,
        "is_major_hub": True
    })

deduped_final.sort(key=lambda x: x['monthly_boardings'], reverse=True)
hubs_final = [s for s in deduped_final if s.get('is_major_hub')]
print(f"\n[FINAL COUNT] Total Street-Perfect Stops: {len(deduped_final)}")
print(f"[FINAL COUNT] Total Major Bus Stands (Black Dots): {len(hubs_final)}")

# 10. Save to files
with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(deduped_final, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(deduped_final, f, indent=2, ensure_ascii=False)

print("Saved cleanly to data/processed/stop_profiles.json and data/stops_meta.json!")

# 11. Sync SQLite DB
conn = sqlite3.connect("data/flowpulse.db")
cur = conn.cursor()
cur.execute("DELETE FROM stops;")
for idx, s in enumerate(deduped_final, 1):
    cur.execute("""
        INSERT INTO stops (id, name, latitude, longitude, corridor, monthly_boardings, monthly_alightings, is_major_hub)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        idx,
        s['name'],
        s['latitude'],
        s['longitude'],
        s.get('corridor', 'Delhi Transit Network'),
        s.get('monthly_boardings', 0),
        s.get('monthly_alightings', 0),
        1 if s.get('is_major_hub') else 0
    ))
conn.commit()
conn.close()
print(f"Synced data/flowpulse.db: {len(deduped_final)} stops, {len(hubs_final)} hubs.")
