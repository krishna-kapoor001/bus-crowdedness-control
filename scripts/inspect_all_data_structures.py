import sqlite3
import os
import csv
import gzip

# 1. SQLite schema
print("=== SQLite Schema ===")
conn = sqlite3.connect('data/flowpulse.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
for t in tables:
    t_name = t[0]
    c.execute(f"PRAGMA table_info({t_name});")
    cols = [col[1] for col in c.fetchall()]
    c.execute(f"SELECT count(*) FROM {t_name};")
    cnt = c.fetchone()[0]
    print(f"Table {t_name} ({cnt} rows): {cols}")
    c.execute(f"SELECT * FROM {t_name} LIMIT 2;")
    print("  Sample:", c.fetchall())
conn.close()

# 2. Raw ETM CSV Header
print("\n=== Raw ETM CSV Columns ===")
with open('data/raw/October-Delhi.csv', 'r', encoding='utf-8', errors='ignore') as f:
    header = f.readline().strip()
    sample_line = f.readline().strip()
    print("Header:", header)
    print("Sample:", sample_line)

# 3. Processed files in data/ and data/processed/
print("\n=== Processed files ===")
for p in ['data', 'data/processed']:
    for f in os.listdir(p):
        if f.endswith(('.json', '.csv', '.gz')):
            fpath = os.path.join(p, f)
            size_mb = os.path.getsize(fpath) / (1024 * 1024)
            print(f"  {fpath} ({size_mb:.2f} MB)")
