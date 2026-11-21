import sqlite3
import json

conn = sqlite3.connect("data/flowpulse.db")
c = conn.cursor()
c.execute("SELECT id, name, latitude, longitude, corridor FROM stops WHERE name LIKE '%Shahdara%'")
print("flowpulse.db stops:", c.fetchall())

# Check stop_profiles.json
with open("data/processed/stop_profiles.json", "r", encoding="utf-8") as f:
    sp = json.load(f)
print("stop_profiles keys with Shahdara:", [k for k in sp.keys() if 'Shahdara' in k])
for k in sp.keys():
    if 'Shahdara' in k:
        print(f"  {k}: lat={sp[k].get('latitude')}, lon={sp[k].get('longitude')}")

# Check stops_meta.json
with open("data/stops_meta.json", "r", encoding="utf-8") as f:
    sm = json.load(f)
print("stops_meta items with Shahdara:", [(s.get('name'), s.get('latitude'), s.get('longitude')) for s in sm if 'Shahdara' in s.get('name', '')])

# Check delhi_bus_stands_coordinates.csv
with open("data/delhi_bus_stands_coordinates.csv", "r", encoding="utf-8") as f:
    for line in f:
        if 'Shahdara' in line:
            print("csv:", line.strip())

conn.close()
