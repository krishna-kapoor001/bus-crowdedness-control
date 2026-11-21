import sqlite3

conn = sqlite3.connect("data/flowpulse.db")
c = conn.cursor()
c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='stops'")
print("Table DDL:", c.fetchone()[0])
conn.close()
