import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

new_stops = [
    {
        'name': 'DTC Bus Depot Yamuna Vihar',
        'latitude': 28.697911,
        'longitude': 77.271642,
        'corridor': 'Trans-Yamuna North Hub',
        'monthly_boardings': 15800,
        'monthly_alightings': 14900,
        'is_major_hub': True
    },
    {
        'name': 'Yamuna Vihar',
        'latitude': 28.697911,
        'longitude': 77.271642,
        'corridor': 'Trans-Yamuna North Hub',
        'monthly_boardings': 14200,
        'monthly_alightings': 13500,
        'is_major_hub': True
    },
    {
        'name': 'C-4 Yamuna Vihar',
        'latitude': 28.698500,
        'longitude': 77.272500,
        'corridor': 'Trans-Yamuna North',
        'monthly_boardings': 9800,
        'monthly_alightings': 9200,
        'is_major_hub': False
    },
    {
        'name': 'C-Block Yamuna Vihar / C4 Yamuna Vihar',
        'latitude': 28.698500,
        'longitude': 77.272500,
        'corridor': 'Trans-Yamuna North',
        'monthly_boardings': 8600,
        'monthly_alightings': 8100,
        'is_major_hub': False
    },
    {
        'name': 'B Block Yamuna Vihar',
        'latitude': 28.699500,
        'longitude': 77.268500,
        'corridor': 'Trans-Yamuna North',
        'monthly_boardings': 7500,
        'monthly_alightings': 7100,
        'is_major_hub': False
    },
    {
        'name': 'Yamuna Vihar Ablock',
        'latitude': 28.701000,
        'longitude': 77.270500,
        'corridor': 'Trans-Yamuna North',
        'monthly_boardings': 6200,
        'monthly_alightings': 5900,
        'is_major_hub': False
    }
]

# 1. Update stop_profiles.json and stops_meta.json
for p in [os.path.join(PROCESSED_DIR, 'stop_profiles.json'), os.path.join(DATA_DIR, 'stops_meta.json')]:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            stops = json.load(f)
        existing_names = {s['name'].lower() for s in stops}
        added = 0
        for ns in new_stops:
            if ns['name'].lower() not in existing_names:
                stops.append(ns)
                existing_names.add(ns['name'].lower())
                added += 1
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(stops, f, indent=2)
        print(f"Updated {p}: added {added} stops (total {len(stops)})")

# 2. Update CSV files
csv_records = [
    {
        'bus_stand_name': 'DTC Bus Depot Yamuna Vihar',
        'latitude': 28.697911,
        'longitude': 77.271642,
        'category': 'Major Bus Depot',
        'corridor_locality': 'Trans-Yamuna North Hub',
        'region': 'Delhi NCT'
    },
    {
        'bus_stand_name': 'Yamuna Vihar',
        'latitude': 28.697911,
        'longitude': 77.271642,
        'category': 'Major Bus Depot',
        'corridor_locality': 'Trans-Yamuna North Hub',
        'region': 'Delhi NCT'
    },
    {
        'bus_stand_name': 'C-4 Yamuna Vihar',
        'latitude': 28.698500,
        'longitude': 77.272500,
        'category': 'Bus Stand',
        'corridor_locality': 'Trans-Yamuna North',
        'region': 'Delhi NCT'
    },
    {
        'bus_stand_name': 'C-Block Yamuna Vihar / C4 Yamuna Vihar',
        'latitude': 28.698500,
        'longitude': 77.272500,
        'category': 'Bus Stand',
        'corridor_locality': 'Trans-Yamuna North',
        'region': 'Delhi NCT'
    },
    {
        'bus_stand_name': 'B Block Yamuna Vihar',
        'latitude': 28.699500,
        'longitude': 77.268500,
        'category': 'Bus Stand',
        'corridor_locality': 'Trans-Yamuna North',
        'region': 'Delhi NCT'
    },
    {
        'bus_stand_name': 'Yamuna Vihar Ablock',
        'latitude': 28.701000,
        'longitude': 77.270500,
        'category': 'Bus Stand',
        'corridor_locality': 'Trans-Yamuna North',
        'region': 'Delhi NCT'
    }
]

for cp in [os.path.join(DATA_DIR, 'delhi_bus_stands_coordinates.csv'), os.path.join(BASE_DIR, 'delhi_bus_stands_coordinates.csv')]:
    if os.path.exists(cp):
        df = pd.read_csv(cp)
        existing = set(df['bus_stand_name'].str.lower())
        new_rows = []
        max_id = int(df['stand_id'].max()) if 'stand_id' in df.columns else 1230
        for rec in csv_records:
            if rec['bus_stand_name'].lower() not in existing:
                max_id += 1
                rec_copy = dict(rec)
                rec_copy['stand_id'] = max_id
                new_rows.append(rec_copy)
        if new_rows:
            df_new = pd.DataFrame(new_rows)
            df_combined = pd.concat([df, df_new], ignore_index=True)
            df_combined.to_csv(cp, index=False)
            print(f"Updated {cp}: added {len(new_rows)} rows (total {len(df_combined)})")

# 3. Add transit edges for DTC Bus Depot Yamuna Vihar
new_edges = [
    {"start_stop": "DTC Bus Depot Yamuna Vihar", "end_stop": "Bhajanpura", "route": "212UP", "frequency": 42},
    {"start_stop": "Bhajanpura", "end_stop": "DTC Bus Depot Yamuna Vihar", "route": "212DOWN", "frequency": 42},
    {"start_stop": "DTC Bus Depot Yamuna Vihar", "end_stop": "Nand Nagri Depot", "route": "212BSTLUP", "frequency": 38},
    {"start_stop": "Nand Nagri Depot", "end_stop": "DTC Bus Depot Yamuna Vihar", "route": "212BSTLDOWN", "frequency": 38},
    {"start_stop": "DTC Bus Depot Yamuna Vihar", "end_stop": "Seelampur Metro Station", "route": "D-5501DOWN", "frequency": 35},
    {"start_stop": "Seelampur Metro Station", "end_stop": "DTC Bus Depot Yamuna Vihar", "route": "D-5501UP", "frequency": 35},
    {"start_stop": "DTC Bus Depot Yamuna Vihar", "end_stop": "Mayur Vihar Ph-3", "route": "206AUP", "frequency": 30},
    {"start_stop": "Mayur Vihar Ph-3", "end_stop": "DTC Bus Depot Yamuna Vihar", "route": "206ADOWN", "frequency": 30},
    {"start_stop": "DTC Bus Depot Yamuna Vihar", "end_stop": "Anand Vihar Isbt Main Road", "route": "165DOWN", "frequency": 45},
    {"start_stop": "Anand Vihar Isbt Main Road", "end_stop": "DTC Bus Depot Yamuna Vihar", "route": "165UP", "frequency": 45},
    {"start_stop": "Yamuna Vihar", "end_stop": "Bhajanpura", "route": "212UP", "frequency": 42},
    {"start_stop": "Bhajanpura", "end_stop": "Yamuna Vihar", "route": "212DOWN", "frequency": 42},
    {"start_stop": "Yamuna Vihar", "end_stop": "DTC Bus Depot Yamuna Vihar", "route": "INTERNAL", "frequency": 100},
    {"start_stop": "DTC Bus Depot Yamuna Vihar", "end_stop": "Yamuna Vihar", "route": "INTERNAL", "frequency": 100}
]

for ep in [os.path.join(PROCESSED_DIR, 'transit_graph_edges.json'), os.path.join(DATA_DIR, 'transit_edges.json')]:
    if os.path.exists(ep):
        with open(ep, 'r', encoding='utf-8') as f:
            edges = json.load(f)
        existing_edge_keys = {(e.get('start_stop', '').lower(), e.get('end_stop', '').lower(), e.get('route', '').lower()) for e in edges}
        added_e = 0
        for ne in new_edges:
            k = (ne['start_stop'].lower(), ne['end_stop'].lower(), ne['route'].lower())
            if k not in existing_edge_keys:
                edges.append(ne)
                existing_edge_keys.add(k)
                added_e += 1
        with open(ep, 'w', encoding='utf-8') as f:
            json.dump(edges, f, indent=2)
        print(f"Updated {ep}: added {added_e} edges (total {len(edges)})")

print("\n✓ SUCCESS: DTC Bus Depot Yamuna Vihar added cleanly to stops, coordinates, and network graph!")
