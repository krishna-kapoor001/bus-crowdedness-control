import sqlite3

conn = sqlite3.connect("data/flowpulse.db")
c = conn.cursor()
c.execute("SELECT count(*) FROM stops")
print("Total stops in flowpulse.db:", c.fetchone()[0])

# Check how many stops in flowpulse.db have 3 decimal places or less:
c.execute("SELECT id, name, latitude, longitude FROM stops")
rows = c.fetchall()
coarse = []
for r in rows:
    lat_s = str(r[2])
    lon_s = str(r[3])
    lat_dec = len(lat_s.split('.')[1]) if '.' in lat_s else 0
    lon_dec = len(lon_s.split('.')[1]) if '.' in lon_s else 0
    if lat_dec <= 3 or lon_dec <= 3:
        coarse.append(r)

print(f"Total coarse stops in flowpulse.db: {len(coarse)}")
for cr in coarse[:15]:
    print("  Coarse:", cr)

conn.close()
