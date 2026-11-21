import os
import sys
import json
import gzip
import pandas as pd
import numpy as np
from datetime import datetime

RAW_CSV = os.path.join('data', 'raw', 'October-Delhi.csv')
PROCESSED_DIR = os.path.join('data', 'processed')
os.makedirs(PROCESSED_DIR, exist_ok=True)

print(f"Executing Preprocessing Pipeline...")
print(f"Source: {RAW_CSV}")
print(f"Target Directory: {PROCESSED_DIR}")

# Data structures for streaming aggregation
route_stats = {}
stop_boardings = {}
stop_alightings = {}
hourly_chunks = []
route_pair_edges = {}

chunk_size = 250000
total_processed = 0

for chunk in pd.read_csv(RAW_CSV, chunksize=chunk_size, low_memory=False):
    # 1. Clean and normalize string fields
    chunk['route'] = chunk['route'].fillna('UNKNOWN').astype(str).str.strip()
    chunk['start_stop_name'] = chunk['start_stop_name'].fillna('UNKNOWN').astype(str).str.strip()
    chunk['end_stop_name'] = chunk['end_stop_name'].fillna('UNKNOWN').astype(str).str.strip()
    
    # 2. Parse and normalize passenger counts and fares
    chunk['passenger_count'] = pd.to_numeric(chunk['passenger_count'], errors='coerce').fillna(1).astype(int)
    chunk['amount'] = pd.to_numeric(chunk['amount'], errors='coerce').fillna(0.0).astype(float)
    chunk['is_ac_clean'] = chunk['is_ac'].astype(str).str.lower().isin(['true', '1', 't'])

    # 3. Timestamps & Temporal Feature Engineering
    chunk['created_at_dt'] = pd.to_datetime(chunk['created_at'], errors='coerce')
    chunk = chunk.dropna(subset=['created_at_dt'])
    
    chunk['date'] = chunk['created_at_dt'].dt.date.astype(str)
    chunk['hour'] = chunk['created_at_dt'].dt.hour
    chunk['day_of_week'] = chunk['created_at_dt'].dt.dayofweek
    chunk['is_weekend'] = chunk['day_of_week'].isin([5, 6]).astype(int)

    # 4. Route-level aggregations
    for route, grp in chunk.groupby('route'):
        if route not in route_stats:
            route_stats[route] = {
                'tickets': 0,
                'passengers': 0,
                'revenue': 0.0,
                'ac_count': 0,
                'start_stops': {},
                'end_stops': {}
            }
        route_stats[route]['tickets'] += len(grp)
        route_stats[route]['passengers'] += int(grp['passenger_count'].sum())
        route_stats[route]['revenue'] += float(grp['amount'].sum())
        route_stats[route]['ac_count'] += int(grp['is_ac_clean'].sum())
        
        for s, c in grp['start_stop_name'].value_counts().head(3).items():
            route_stats[route]['start_stops'][s] = route_stats[route]['start_stops'].get(s, 0) + int(c)
        for s, c in grp['end_stop_name'].value_counts().head(3).items():
            route_stats[route]['end_stops'][s] = route_stats[route]['end_stops'].get(s, 0) + int(c)

    # 5. Stop boardings and alightings
    for s, c in chunk['start_stop_name'].value_counts().items():
        stop_boardings[s] = stop_boardings.get(s, 0) + int(c)
    for s, c in chunk['end_stop_name'].value_counts().items():
        stop_alightings[s] = stop_alightings.get(s, 0) + int(c)

    # 6. Graph edges between consecutive stops
    for (rt, start, end), count in chunk.groupby(['route', 'start_stop_name', 'end_stop_name']).size().items():
        key = (rt, start, end)
        route_pair_edges[key] = route_pair_edges.get(key, 0) + int(count)

    # 7. Hourly route-level demand grouping
    hourly_grp = chunk.groupby(['route', 'date', 'day_of_week', 'hour', 'is_weekend']).agg(
        passengers=('passenger_count', 'sum'),
        tickets=('passenger_count', 'count'),
        revenue=('amount', 'sum'),
        ac_trips=('is_ac_clean', 'sum')
    ).reset_index()

    hourly_chunks.append(hourly_grp)
    total_processed += len(chunk)
    print(f"Processed {total_processed:,} records...")

print("Consolidating hourly demand across all chunks...")
df_hourly = pd.concat(hourly_chunks, ignore_index=True)
df_hourly = df_hourly.groupby(['route', 'date', 'day_of_week', 'hour', 'is_weekend'], as_index=False).agg({
    'passengers': 'sum',
    'tickets': 'sum',
    'revenue': 'sum',
    'ac_trips': 'sum'
})

print(f"Total aggregated hourly records: {len(df_hourly):,}")
hourly_output = os.path.join(PROCESSED_DIR, 'hourly_route_demand.csv.gz')
df_hourly.to_csv(hourly_output, index=False, compression='gzip')
print(f"Saved: {hourly_output}")

# Save route profiles
route_profiles = []
for r, d in sorted(route_stats.items(), key=lambda x: x[1]['passengers'], reverse=True):
    p_orig = max(d['start_stops'].items(), key=lambda x: x[1])[0] if d['start_stops'] else "Origin Hub"
    p_dest = max(d['end_stops'].items(), key=lambda x: x[1])[0] if d['end_stops'] else "Destination Hub"
    direction = "UP" if "UP" in r.upper() else ("DOWN" if "DOWN" in r.upper() else "CIRCULAR")
    is_ac = (d['ac_count'] / max(1, d['tickets'])) > 0.5
    
    route_profiles.append({
        'route_id': r,
        'direction': direction,
        'origin': p_orig,
        'destination': p_dest,
        'total_tickets': d['tickets'],
        'total_passengers': d['passengers'],
        'total_revenue': round(d['revenue'], 2),
        'is_predominantly_ac': is_ac,
        'avg_daily_passengers': round(d['passengers'] / 31.0, 1)
    })

routes_json = os.path.join(PROCESSED_DIR, 'route_profiles.json')
with open(routes_json, 'w') as f:
    json.dump(route_profiles, f, indent=2)
print(f"Saved {len(route_profiles)} route profiles to {routes_json}")

# Save stop profiles with geo coordinates
try:
    from fix_all_stop_coordinates import resolve_stop_geo
except ImportError:
    try:
        from scripts.fix_all_stop_coordinates import resolve_stop_geo
    except ImportError:
        def resolve_stop_geo(name):
            return 28.6139, 77.2090, "Delhi NCT Central"

stop_profiles = []
for s, b_cnt in sorted(stop_boardings.items(), key=lambda x: x[1], reverse=True)[:500]:
    lat, lon, corr = resolve_stop_geo(s)
    stop_profiles.append({
        'name': s,
        'latitude': round(lat, 5),
        'longitude': round(lon, 5),
        'corridor': corr,
        'monthly_boardings': b_cnt,
        'monthly_alightings': stop_alightings.get(s, 0),
        'is_major_hub': b_cnt >= 2000
    })

stops_json = os.path.join(PROCESSED_DIR, 'stop_profiles.json')
with open(stops_json, 'w') as f:
    json.dump(stop_profiles, f, indent=2)
print(f"Saved {len(stop_profiles)} top stop profiles to {stops_json}")

# Save transit edges
transit_edges = []
for (rt, start, end), count in route_pair_edges.items():
    if count >= 20:
        transit_edges.append({
            'route': rt,
            'start_stop': start,
            'end_stop': end,
            'frequency': count
        })

edges_json = os.path.join(PROCESSED_DIR, 'transit_graph_edges.json')
with open(edges_json, 'w') as f:
    json.dump(transit_edges, f, indent=2)
print(f"Saved {len(transit_edges)} transit graph edges to {edges_json}")

print("\nData Preprocessing Pipeline Complete!")
