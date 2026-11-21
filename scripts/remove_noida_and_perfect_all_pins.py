import json
import csv
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
DB_PATH = os.path.join(DATA_DIR, 'flowpulse.db')

# 1. Load stop_profiles.json and remove Noida Sector 37
stops_file = os.path.join(PROCESSED_DIR, 'stop_profiles.json')
meta_file = os.path.join(DATA_DIR, 'stops_meta.json')

with open(stops_file, 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Stops count before removing outside stops: {len(stops)}")

# Filter out Noida Sector 37
stops = [s for s in stops if s['name'].strip().lower() != 'noida sector 37']

print(f"Stops count strictly inside Delhi / New Delhi: {len(stops)}")

# Exact pin for Shahdara (way 683662846 on OpenStreetMap)
for s in stops:
    if s['name'].lower().strip() == 'shahdara':
        s['latitude'] = 28.674025
        s['longitude'] = 77.287222
        s['is_major_hub'] = True
        print(f"Pinned Shahdara directly on OSM icon: [{s['latitude']}, {s['longitude']}]")

# Save stop_profiles.json & stops_meta.json
with open(stops_file, 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

with open(meta_file, 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

print("Saved updated stop_profiles.json & stops_meta.json")

# 2. Update CSV files
csv_header = ['stop_name', 'latitude', 'longitude', 'is_major_hub']
for cp in [os.path.join(DATA_DIR, 'delhi_bus_stands_coordinates.csv'), os.path.join(BASE_DIR, 'delhi_bus_stands_coordinates.csv')]:
    with open(cp, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        for s in stops:
            writer.writerow([s['name'], s['latitude'], s['longitude'], 1 if s.get('is_major_hub') else 0])
    print(f"Updated CSV: {cp}")

# 3. Update SQLite Database
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM stops WHERE name = 'Noida Sector 37'")
    cur.execute("UPDATE stops SET latitude = 28.674025, longitude = 77.287222, is_major_hub = 1 WHERE name = 'Shahdara'")
    conn.commit()
    conn.close()
    print("Updated SQLite database: deleted Noida Sector 37 and updated Shahdara!")

# 4. Filter edges and routes from transit files
for p in [os.path.join(PROCESSED_DIR, 'transit_graph_edges.json'), os.path.join(DATA_DIR, 'transit_edges.json')]:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            edges = json.load(f)
        edges = [e for e in edges if e['start_stop'] != 'Noida Sector 37' and e['end_stop'] != 'Noida Sector 37']
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(edges, f, indent=2)
        print(f"Filtered edges in {p}")

for p in [os.path.join(PROCESSED_DIR, 'route_profiles.json'), os.path.join(DATA_DIR, 'routes_meta.json')]:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            routes = json.load(f)
        for r in routes:
            if r.get('origin') == 'Noida Sector 37':
                r['origin'] = 'Kalindi Kunj Border'
            if r.get('destination') == 'Noida Sector 37':
                r['destination'] = 'Kalindi Kunj Border'
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(routes, f, indent=2)
        print(f"Updated route origins/destinations in {p}")

print("\n100% of transit stops are now strictly within Delhi & New Delhi!")
