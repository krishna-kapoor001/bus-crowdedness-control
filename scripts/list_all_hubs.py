import sqlite3

conn = sqlite3.connect('data/flowpulse.db')
c = conn.cursor()
c.execute('SELECT id, name, latitude, longitude FROM stops WHERE is_major_hub = 1 ORDER BY name')
hubs = c.fetchall()
conn.close()

for i, h in enumerate(hubs):
    print(f"{i+1:3d}. {h[1]} -> ({h[2]}, {h[3]})")
