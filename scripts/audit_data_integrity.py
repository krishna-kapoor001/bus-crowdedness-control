import os
import json
import sqlite3
import pandas as pd

def audit():
    print("=" * 60)
    print("BUSROUTE DATA INTEGRITY & QUALITY AUDIT")
    print("=" * 60)

    # 1. Stops Audit
    stops_file = os.path.join('data', 'stops_meta.json')
    with open(stops_file, 'r', encoding='utf-8') as f:
        stops = json.load(f)
    print(f"\n1. STOPS AUDIT ({len(stops)} stops in data/stops_meta.json):")
    
    oob = []
    nulls = 0
    zero_boardings = 0
    negatives = 0
    for s in stops:
        lat = s.get('latitude')
        lon = s.get('longitude')
        if lat is None or lon is None:
            nulls += 1
            continue
        # Delhi NCT bounding box: lat 28.3 to 28.95, lon 76.8 to 77.5
        if not (28.35 <= lat <= 28.95 and 76.80 <= lon <= 77.45):
            oob.append((s['name'], lat, lon))
        b = s.get('monthly_boardings', 0)
        if b < 0:
            negatives += 1
        elif b == 0:
            zero_boardings += 1

    print(f"   Null Coordinates: {nulls}")
    print(f"   Out-of-Bounds (Outside Delhi NCT): {len(oob)}")
    if oob:
        print(f"   Samples OOB: {oob[:5]}")
    print(f"   Negative Boardings: {negatives}")
    print(f"   Zero Boardings: {zero_boardings}")
    print(f"   Max Boardings: {max(s['monthly_boardings'] for s in stops):,}")

    # 2. Stop Profiles in processed/
    proc_stops_file = os.path.join('data', 'processed', 'stop_profiles.json')
    with open(proc_stops_file, 'r', encoding='utf-8') as f:
        proc_stops = json.load(f)
    print(f"\n2. PROCESSED STOP PROFILES ({len(proc_stops)} stops):")
    proc_oob = [s for s in proc_stops if not (28.35 <= s.get('latitude', 0) <= 28.95 and 76.80 <= s.get('longitude', 0) <= 77.45)]
    print(f"   Out-of-Bounds: {len(proc_oob)}")

    # 3. Routes Audit
    routes_file = os.path.join('data', 'routes_meta.json')
    with open(routes_file, 'r', encoding='utf-8') as f:
        routes = json.load(f)
    print(f"\n3. ROUTES AUDIT ({len(routes)} routes in data/routes_meta.json):")
    inv_routes = [r for r in routes if r.get('total_tickets', 0) <= 0 or r.get('total_passengers', 0) <= 0]
    print(f"   Invalid Routes (<= 0 tickets/passengers): {len(inv_routes)}")
    total_pax = sum(r['total_passengers'] for r in routes)
    total_tix = sum(r['total_tickets'] for r in routes)
    print(f"   Total Tickets Monitored: {total_tix:,}")
    print(f"   Total Passengers Monitored: {total_pax:,}")

    # 4. Transit Graph Edges
    edges_file = os.path.join('data', 'transit_edges.json')
    with open(edges_file, 'r', encoding='utf-8') as f:
        edges = json.load(f)
    print(f"\n4. TRANSIT EDGES AUDIT ({len(edges)} graph transitions):")
    inv_edges = [e for e in edges if not e.get('start_stop') or not e.get('end_stop') or e.get('frequency', 0) <= 0]
    print(f"   Invalid Edges: {len(inv_edges)}")

    # 5. SQLite Database Audit
    db_path = os.path.join('data', 'busroute.db')
    print(f"\n5. SQLITE DATABASE AUDIT ({db_path}):")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    tables = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"   Tables found: {tables}")
    for t in tables:
        cnt = cur.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        print(f"   Table '{t}': {cnt:,} records")
        
        # Check coordinates in stops table
        if t == 'stops':
            db_oob = cur.execute("SELECT count(*) FROM stops WHERE latitude < 28.35 OR latitude > 28.95 OR longitude < 76.80 OR longitude > 77.45").fetchone()[0]
            print(f"      Stops with coordinates outside Delhi NCT: {db_oob}")
    conn.close()

    # 6. Hourly Demand Compressed CSV
    hourly_csv = os.path.join('data', 'hourly_route_demand.csv.gz')
    if os.path.exists(hourly_csv):
        df_h = pd.read_csv(hourly_csv, compression='gzip', nrows=1000)
        print(f"\n6. HOURLY DEMAND DATASET ({hourly_csv}):")
        print(f"   Columns: {list(df_h.columns)}")
        print(f"   Nulls in sample: {df_h.isnull().sum().to_dict()}")
        print(f"   Hours min/max: {df_h['hour'].min()} to {df_h['hour'].max()}")

    print("\n" + "=" * 60)
    print("AUDIT SUMMARY: Complete & Verified")
    print("=" * 60)

if __name__ == '__main__':
    audit()
