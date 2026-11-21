import sqlite3

conn = sqlite3.connect("data/flowpulse.db")
c = conn.cursor()
c.execute("SELECT name, sql FROM sqlite_master WHERE type='index'")
print("Indexes:", c.fetchall())
conn.close()
