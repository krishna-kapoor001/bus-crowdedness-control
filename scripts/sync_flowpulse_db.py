import sqlite3
import json

conn = sqlite3.connect("data/flowpulse.db")
c = conn.cursor()

# 1. Delete duplicate or obsolete Shahdara Terminal if any
c.execute("DELETE FROM stops WHERE name = 'Shahdara Terminal'")
c.execute("DELETE FROM stops WHERE name LIKE '%Noida%'")

# 2. Load all 428 stops from stop_profiles.json
with open("data/processed/stop_profiles.json", "r", encoding="utf-8") as f:
    stops = json.load(f)

print(f"Loaded {len(stops)} stops from stop_profiles.json")

# 3. Upsert or update each stop in flowpulse.db
for s in stops:
    name = s['name']
    lat = s['latitude']
    lon = s['longitude']
    corridor = s.get('corridor', 'Delhi Transit Region')
    boardings = s.get('monthly_boardings', 500)
    alightings = s.get('monthly_alightings', 500)
    
    c.execute("SELECT id FROM stops WHERE name = ?", (name,))
    row = c.fetchone()
    if row:
        c.execute("""
            UPDATE stops 
            SET latitude = ?, longitude = ?, corridor = ?, monthly_boardings = ?, monthly_alightings = ?
            WHERE name = ?
        """, (lat, lon, corridor, boardings, alightings, name))
    else:
        c.execute("""
            INSERT INTO stops (name, latitude, longitude, corridor, monthly_boardings, monthly_alightings)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, lat, lon, corridor, boardings, alightings))

conn.commit()

# Verify Shahdara in SQLite:
c.execute("SELECT id, name, latitude, longitude FROM stops WHERE name LIKE '%Shahdara%'")
print("Verified SQLite Shahdara entries:", c.fetchall())

# Check total count in SQLite
c.execute("SELECT count(*) FROM stops")
print("Total stops in flowpulse.db:", c.fetchone()[0])

conn.close()
