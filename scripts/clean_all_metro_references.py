import json
import csv
import os
import sqlite3
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
DB_PATH = os.path.join(DATA_DIR, 'flowpulse.db')

METRO_REPLACEMENTS = {
    'Chhatarpur Metro Station': 'Chhatarpur Bus Stop',
    'Vishwa Vidyalaya Metro Station': 'Vishwa Vidyalaya Bus Stop',
    'Saket Metro Station': 'Saket Bus Stop',
    'Karol Bagh Metro Station': 'Karol Bagh Bus Stop',
    'Laxmi Nagar (Vikas Marg) / Laxmi Nagar Metro Station': 'Laxmi Nagar (Vikas Marg) Bus Stop',
    'Rajindera Place Metro Station': 'Rajendra Place Bus Stop',
    'Shadipur Dtc Colony Metro Station': 'Shadipur DTC Colony Bus Stop',
    'Saket A Block (Malviya Nagar Metro Station)': 'Saket A Block (Malviya Nagar Bus Stop)',
    'Karol Bagh Metro': 'Karol Bagh Bus Stand',
    'Saket Metro Sation / Said-Ul-Ajaib': 'Saket Said-Ul-Ajaib Bus Stop',
    'Jahangir Puri Metro Station': 'Jahangirpuri Bus Stop',
    'Rithala Metro Station': 'Rithala Bus Stop',
    'Shadi Pur Metro Station': 'Shadipur Bus Stop',
    'Dwarka More Metro Station': 'Dwarka Mor Bus Stand',
    'Lajpat Nagar Metro': 'Lajpat Nagar Bus Stand',
    'Chhatarpur Metro': 'Chhatarpur Bus Stand',
    'Punj Sons / Govind Puri Metro Station': 'Punj Sons / Govindpuri Bus Stop',
    'Andheria More / Chhatarpur Metro Station': 'Andheria Mor / Chhatarpur Bus Stop',
    'Jahangirpuri Metro Station Gt Road': 'Jahangirpuri GT Road Bus Stop',
    'Qutub Minar Metro Sation': 'Qutub Minar Bus Stop',
    'Metro Train Depot': 'Shastri Park Transit Depot',
    'Ip Depot Metro Station': 'IP Depot Bus Stand',
    'Shastri Park Metro Depot': 'Shastri Park Bus Depot'
}

# 1. Update stop_profiles.json & stops_meta.json
for p in [os.path.join(PROCESSED_DIR, 'stop_profiles.json'), os.path.join(DATA_DIR, 'stops_meta.json')]:
    with open(p, 'r', encoding='utf-8') as f:
        stops = json.load(f)
    for s in stops:
        if s['name'] in METRO_REPLACEMENTS:
            s['name'] = METRO_REPLACEMENTS[s['name']]
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(stops, f, indent=2, ensure_ascii=False)
    print(f"Updated {p}")

# 2. Update corridors_routed.json
for cp in [os.path.join(PROCESSED_DIR, 'corridors_routed.json'), os.path.join(DATA_DIR, 'corridors_routed.json')]:
    with open(cp, 'r', encoding='utf-8') as f:
        corridors = json.load(f)
    for c in corridors:
        # update name if it contains Saket Metro Station
        if 'Saket Metro Station' in c['name']:
            c['name'] = c['name'].replace('Saket Metro Station', 'Saket Bus Stop')
        new_stops = []
        for s in c.get('stops', []):
            new_stops.append(METRO_REPLACEMENTS.get(s, s))
        c['stops'] = new_stops
    with open(cp, 'w', encoding='utf-8') as f:
        json.dump(corridors, f, indent=2, ensure_ascii=False)
    print(f"Updated {cp}")

# 3. Update CSV files
csv_header = ['stop_name', 'latitude', 'longitude', 'is_major_hub']
for cp in [os.path.join(DATA_DIR, 'delhi_bus_stands_coordinates.csv'), os.path.join(BASE_DIR, 'delhi_bus_stands_coordinates.csv')]:
    with open(os.path.join(PROCESSED_DIR, 'stop_profiles.json'), 'r', encoding='utf-8') as f:
        stops = json.load(f)
    with open(cp, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        for s in stops:
            writer.writerow([s['name'], s['latitude'], s['longitude'], 1 if s.get('is_major_hub') else 0])
    print(f"Updated CSV: {cp}")

# 4. Update SQLite Database
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for old_name, new_name in METRO_REPLACEMENTS.items():
        cur.execute("UPDATE stops SET name = ? WHERE name = ?", (new_name, old_name))
    conn.commit()
    conn.close()
    print("Updated SQLite database with cleaned bus stop names!")

print("\nSuccessfully cleaned all Metro keywords into Bus Stop / Bus Stand systemwide!")
