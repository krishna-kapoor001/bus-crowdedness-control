import json
import os
import sqlite3

print("--- Data Sources Inspection ---")

stops_profile_file = 'data/processed/stop_profiles.json'
if os.path.exists(stops_profile_file):
    with open(stops_profile_file, 'r', encoding='utf-8') as f:
        st = json.load(f)
        print(f"stop_profiles.json: {len(st)} stops")
        print("Sample stop:", st[0])

stops_meta_file = 'data/stops_meta.json'
if os.path.exists(stops_meta_file):
    with open(stops_meta_file, 'r', encoding='utf-8') as f:
        sm = json.load(f)
        print(f"stops_meta.json: {len(sm)} stops")

all_stops_file = 'data/all_stop_names.txt'
if os.path.exists(all_stops_file):
    with open(all_stops_file, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]
        print(f"all_stop_names.txt: {len(lines)} names")

db_file = 'data/flowpulse.db'
if os.path.exists(db_file):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("DB Tables:", [t[0] for t in cur.fetchall()])
    cur.execute("SELECT count(*) FROM stops")
    print("DB Stops count:", cur.fetchone()[0])
    cur.execute("SELECT * FROM stops LIMIT 3")
    print("Sample DB rows:", cur.fetchall())
    conn.close()
