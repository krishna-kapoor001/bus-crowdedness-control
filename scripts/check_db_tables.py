import sqlite3
import os

for db_path in ['flowpulse.db', 'data/flowpulse.db']:
    if not os.path.exists(db_path):
        continue
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cur.fetchall()]
        print(f"{db_path} tables:", tables)
        for t in tables:
            cur.execute(f"SELECT count(*) FROM {t}")
            cnt = cur.fetchone()[0]
            print(f"   {t}: {cnt} rows")
        conn.close()
    except Exception as e:
        print(f"{db_path}: {e}")
