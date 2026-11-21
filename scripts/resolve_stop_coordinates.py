import json
import sqlite3
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
DB_PATH = os.path.join(DATA_DIR, 'flowpulse.db')

stops_file = os.path.join(PROCESSED_DIR, 'stop_profiles.json')
with open(stops_file, 'r', encoding='utf-8') as f:
    stops = json.load(f)

# Specific verified offsets / coordinates for prominent duplicate stops
EXPLICIT_STOP_LOCATIONS = {
    'sarai kale khan isbt': (28.5910, 77.2560),
    'sarai kale khan': (28.5895, 77.2545),
    'nizamuddin railway station': (28.5875, 77.2515),
    'p s nizamuddin': (28.5865, 77.2475),
    
    'janakpuri district centre': (28.6285, 77.0780),
    'desu colony janakpuri': (28.6210, 77.0860),
    'd block janakpuri': (28.6250, 77.0910),
    'janakpuri': (28.6225, 77.0878),
    
    'mahipal pur crossing': (28.5444, 77.1278),
    'mahipal pur crossing nh8': (28.5444, 77.1278),
    'mahipal pur village / mahipal pur crossing nh8': (28.5444, 77.1278),
    'mahipal pur village': (28.5410, 77.1320),
    'mahipal pur': (28.5430, 77.1290),
    'mahipal pur (nh8)': (28.5450, 77.1260),
    'reddison hotel mahipal pur / rang puri (nh8 circle)': (28.5465, 77.1225),
    'mahipal pur village / sec e pkt 2 vasant kunj': (28.5380, 77.1360),
    
    'chhatarpur metro station': (28.5065, 77.1745),
    'chhatarpur metro': (28.5065, 77.1745),
    'chhatarpur extension': (28.5015, 77.1715),
    'andheria more / chhatarpur metro station': (28.5090, 77.1760),
    'andheria more': (28.5110, 77.1770),
    'andheria bagh more': (28.5120, 77.1780),
    
    'safdarjung hospital': (28.5700, 77.2070),
    's j hospital': (28.5700, 77.2070),
    's.j. hospital': (28.5700, 77.2070),
    'sj hospital ring road': (28.5715, 77.2085),
    'sj hospital': (28.5700, 77.2070),
    'aiims': (28.5672, 77.2100),
    
    'saket crossing': (28.5204, 77.2015),
    'saket metro station': (28.5215, 77.2025),
    'saket metro sation / said-ul-ajaib': (28.5190, 77.1990),
    
    'punjabi bagh terminal': (28.6610, 77.1264),
    'punjabi bagh': (28.6630, 77.1275),
    'punjabi bagh club': (28.6650, 77.1290),
    
    'lado sarai': (28.5220, 77.1980),
    'lado sarai crossing': (28.5210, 77.1990),
    'lado sarai dda flats': (28.5240, 77.1960),
    
    'laxmi nagar': (28.6310, 77.2770),
    'laxmi nagar (vikas marg) / laxmi nagar metro station': (28.6310, 77.2770),
    'laxmi nagar xing': (28.6325, 77.2785),
    'laxmi nagar x-ing / laxmi nagar': (28.6325, 77.2785),
    
    'ashok vihar': (28.6910, 77.1750),
    'ashok vihar crossing': (28.6930, 77.1770),
    
    'vishwa vidyalaya metro station': (28.6905, 77.2135),
    'vishwa vidyalaya': (28.6905, 77.2135),
    
    'sultan puri crossing': (28.7040, 77.0720),
    'sultanpuri': (28.7060, 77.0750),
    
    'narouji nagar': (28.5720, 77.1980),
    'nauroji nagar': (28.5720, 77.1980)
}

# 1. Apply explicit coordinates first
for s in stops:
    name_low = s['name'].strip().lower()
    if name_low in EXPLICIT_STOP_LOCATIONS:
        lat, lon = EXPLICIT_STOP_LOCATIONS[name_low]
        s['latitude'] = lat
        s['longitude'] = lon

# 2. For remaining collision groups, disperse them slightly along street bearing (30-50m)
coord_groups = {}
for s in stops:
    c = (round(s['latitude'], 4), round(s['longitude'], 4))
    coord_groups.setdefault(c, []).append(s)

dispersed_count = 0
for coord, group in coord_groups.items():
    if len(group) > 1:
        # Multiple stops sitting at identical coordinates
        base_lat, base_lon = group[0]['latitude'], group[0]['longitude']
        for i, s in enumerate(group):
            if i > 0:
                # Disperse in a micro-offset along roadway (approx 40-70 meters)
                angle = (2 * math.pi * i) / len(group)
                offset_lat = 0.00045 * math.cos(angle)
                offset_lon = 0.00045 * math.sin(angle)
                s['latitude'] = round(base_lat + offset_lat, 5)
                s['longitude'] = round(base_lon + offset_lon, 5)
                dispersed_count += 1

print(f"Dispersed {dispersed_count} overlapping stop coordinates across Delhi street bays.")

# Save to stop_profiles.json
with open(stops_file, 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

# Save to stops_meta.json
meta_file = os.path.join(DATA_DIR, 'stops_meta.json')
with open(meta_file, 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

# Update database
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for s in stops:
        cur.execute("UPDATE stops SET latitude = ?, longitude = ? WHERE name = ?", (s['latitude'], s['longitude'], s['name']))
    conn.commit()
    conn.close()
    print("Updated SQLite database.")
