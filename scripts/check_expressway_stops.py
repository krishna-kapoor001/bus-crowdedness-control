import sqlite3

conn = sqlite3.connect('data/flowpulse.db')
c = conn.cursor()

# 1. DND Flyway: lat 28.56 to 28.59, lon 77.27 to 77.31
c.execute("""
SELECT id, name, latitude, longitude FROM stops 
WHERE latitude BETWEEN 28.56 AND 28.59 AND longitude BETWEEN 77.27 AND 77.31
""")
dnd_stops = c.fetchall()
print(f"Stops on/near DND Flyway: {len(dnd_stops)}")
for s in dnd_stops:
    print(f"  • {s[1]} -> ({s[2]}, {s[3]})")

# 2. Delhi-Meerut Expressway Corridor (Sarai Kale Khan to Ghazipur: lat 28.58 to 28.64, lon 77.26 to 77.33)
c.execute("""
SELECT id, name, latitude, longitude FROM stops 
WHERE latitude BETWEEN 28.60 AND 28.64 AND longitude BETWEEN 77.28 AND 77.33
""")
dme_stops = c.fetchall()
print(f"\nStops in Delhi-Meerut / NH-9 corridor: {len(dme_stops)}")
for s in dme_stops[:10]:
    print(f"  • {s[1]} -> ({s[2]}, {s[3]})")

# 3. NH-48 / Airport Corridor (Dhaula Kuan to Rajokri: lat 28.50 to 28.59, lon 77.10 to 77.17)
c.execute("""
SELECT id, name, latitude, longitude FROM stops 
WHERE latitude BETWEEN 28.50 AND 28.59 AND longitude BETWEEN 77.10 AND 77.17
""")
nh48_stops = c.fetchall()
print(f"\nStops along NH-48 corridor: {len(nh48_stops)}")
for s in nh48_stops[:10]:
    print(f"  • {s[1]} -> ({s[2]}, {s[3]})")

conn.close()
