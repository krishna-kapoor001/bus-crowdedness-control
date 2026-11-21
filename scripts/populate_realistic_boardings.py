import json
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
DB_PATH = os.path.join(DATA_DIR, 'flowpulse.db')

BENCHMARK_BOARDINGS = {
    'safdarjung hospital': 4200,
    'ashok vihar': 2800,
    'janakpuri': 3900,
    'mayur vihar phase 1': 3600,
    'janakpuri district centre': 3100,
    'govindpuri': 3400,
    'connaught place': 8600,
    'rohini sector 22': 2100,
    'kalkaji temple': 4500,
    'okhla phase 3': 2600,
    'new delhi railway station': 13500,
    'r.k. puram sector 1': 1927,
    'pitampura': 3300,
    'ito ring road': 5800,
    'isbt kashmiri gate': 16800,
    'karol bagh metro': 4800,
    'sultanpuri': 2400,
    'gtb nagar': 5200,
    'vishwa vidyalaya': 4900,
    'dwarka mor': 4100,
    'jahangirpuri': 4600,
    'lajpat nagar metro': 6500,
    'mangolpuri': 2800,
    'chhatarpur metro': 5900,
    'dwarka sector 10': 2300,
    'anand vihar isbt': 16200,
    'kashmere gate': 15400,
    'rohini west': 3600,
    'aiims': 11800,
}

stops_file = os.path.join(PROCESSED_DIR, 'stop_profiles.json')
with open(stops_file, 'r', encoding='utf-8') as f:
    stops = json.load(f)

fixed_count = 0
for s in stops:
    name_low = s['name'].strip().lower()
    if s.get('monthly_boardings', 0) == 0:
        val = BENCHMARK_BOARDINGS.get(name_low, 1500)
        s['monthly_boardings'] = val
        fixed_count += 1

print(f"Fixed zero boardings for {fixed_count} stops.")

with open(stops_file, 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

meta_file = os.path.join(DATA_DIR, 'stops_meta.json')
with open(meta_file, 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for s in stops:
        cur.execute("UPDATE stops SET monthly_boardings = ? WHERE name = ?", (s['monthly_boardings'], s['name']))
    conn.commit()
    conn.close()
    print("Database updated successfully.")
