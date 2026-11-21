import json, sqlite3, csv, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'flowpulse.db')

EXPRESSWAY_CORRECTIONS = {
    'Khichdipur': (28.624456, 77.309587, 'Khichdipur Village Road Curb'),
    'Sanjay Lake Trilokpuri': (28.620562, 77.296032, 'West Vinod Nagar / Kalyanvas Road Curb'),
    'Shiv Murti': (28.535640, 77.112550, 'NH-48 Service Road Bus Bay Curb'),
    'Lalita Park': (28.632161, 77.271016, 'Pushta Road Service Lane Curb'),
    'Pusta Crossing Akhardham Temple': (28.612200, 77.282495, 'Akshardham Pushta Road Curb'),
    'Samaspur Jagir Village': (28.615485, 77.284352, 'Samaspur Village Local Road Curb')
}

# 1. Update stops_meta.json
stops_meta_path = os.path.join(DATA_DIR, 'stops_meta.json')
with open(stops_meta_path, 'r', encoding='utf-8') as f:
    stops_meta = json.load(f)

for s in stops_meta:
    name = s.get('name', '')
    if name in EXPRESSWAY_CORRECTIONS:
        new_lat, new_lon, note = EXPRESSWAY_CORRECTIONS[name]
        s['latitude'] = new_lat
        s['longitude'] = new_lon

with open(stops_meta_path, 'w', encoding='utf-8') as f:
    json.dump(stops_meta, f, indent=2)

# 2. Update stop_profiles.json
stop_profiles_path = os.path.join(DATA_DIR, 'processed', 'stop_profiles.json')
with open(stop_profiles_path, 'r', encoding='utf-8') as f:
    profiles = json.load(f)

updated_prof = 0
for p in profiles:
    name = p.get('name', '')
    if name in EXPRESSWAY_CORRECTIONS:
        new_lat, new_lon, note = EXPRESSWAY_CORRECTIONS[name]
        p['latitude'] = new_lat
        p['longitude'] = new_lon
        updated_prof += 1

with open(stop_profiles_path, 'w', encoding='utf-8') as f:
    json.dump(profiles, f, indent=2)
print(f"Updated {updated_prof} stops in {stop_profiles_path}")

# 3. Update CSV files
csv_files = [
    os.path.join(DATA_DIR, 'delhi_bus_stands_coordinates.csv'),
    os.path.join(BASE_DIR, 'delhi_bus_stands_coordinates.csv')
]

for cp in csv_files:
    if os.path.exists(cp):
        rows = []
        with open(cp, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                name = row.get('bus_stand_name', '')
                if name in EXPRESSWAY_CORRECTIONS:
                    new_lat, new_lon, note = EXPRESSWAY_CORRECTIONS[name]
                    row['latitude'] = str(new_lat)
                    row['longitude'] = str(new_lon)
                rows.append(row)
        with open(cp, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Updated CSV: {cp}")

# 4. Update SQLite flowpulse.db
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
for name, (new_lat, new_lon, note) in EXPRESSWAY_CORRECTIONS.items():
    cursor.execute("""
        UPDATE stops
        SET latitude = ?, longitude = ?
        WHERE LOWER(name) = LOWER(?)
    """, (new_lat, new_lon, name))
conn.commit()
conn.close()
print("Updated SQLite flowpulse.db stops table successfully.")
