import sqlite3

conn = sqlite3.connect('data/flowpulse.db')
c = conn.cursor()
c.execute("SELECT id, name, latitude, longitude, is_major_hub FROM stops WHERE name LIKE '%village%' OR name LIKE '%gaon%' OR name LIKE '%kalan%' OR name LIKE '%khurd%' OR name LIKE '%khera%' LIMIT 30")
rural = c.fetchall()
conn.close()

print(f"Sample rural / village stops in DB:")
for r in rural:
    print(f"  • {r[1]} -> ({r[2]}, {r[3]}) [Hub: {r[4]}]")
