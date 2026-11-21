import sqlite3

conn = sqlite3.connect("data/flowpulse.db")
c = conn.cursor()
c.execute("SELECT name, latitude, longitude FROM stops WHERE name LIKE '%Shahdara%'")
rows = c.fetchall()
print("SQLite stops for Shahdara:", rows)
conn.close()
