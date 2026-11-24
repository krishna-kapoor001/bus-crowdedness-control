import sqlite3
import json

# Sync flowpulse.db stops table with the exact 827 verified stops
conn = sqlite3.connect("data/flowpulse.db")
cur = conn.cursor()

# 1. Load current 827 verified stops
with open("data/processed/stop_profiles.json", "r", encoding="utf-8") as f:
    stops = json.load(f)

print(f"Loaded {len(stops)} stops from data/processed/stop_profiles.json")

# 2. Re-create or clean stops table
cur.execute("DELETE FROM stops;")
print("Cleared old stops from database.")

# Check columns of stops table
cur.execute("PRAGMA table_info(stops);")
cols = [r[1] for r in cur.fetchall()]
print("stops table columns:", cols)

for idx, s in enumerate(stops, 1):
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

# Verify count
cur.execute("SELECT count(*) FROM stops;")
count = cur.fetchone()[0]
cur.execute("SELECT count(*) FROM stops WHERE is_major_hub = 1;")
hubs_count = cur.fetchone()[0]

print(f"Successfully synced data/flowpulse.db: {count} stops, {hubs_count} major hubs!")
conn.close()
