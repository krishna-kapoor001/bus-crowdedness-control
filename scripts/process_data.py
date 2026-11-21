import zipfile
import os
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
RAW_CSV_PATH = os.path.join(DATA_DIR, 'Raw', 'October-Delhi.csv')
if not os.path.exists(RAW_CSV_PATH):
    RAW_CSV_PATH = os.path.join(DATA_DIR, 'October-Delhi.csv')

ZIP_PATH = os.getenv('DELHI_ETM_ZIP_PATH', os.path.join(DATA_DIR, 'Raw', 'October-Delhi.csv.zip'))
os.makedirs(DATA_DIR, exist_ok=True)

# Curated high-precision coordinates for Delhi Transit hubs & key stops
DELHI_STOP_COORDINATES = {
    "Kashmere Gate": (28.6675, 77.2285, "North Corridor"),
    "ISBT Kashmiri Gate": (28.6685, 77.2300, "North Corridor"),
    "Shivaji Stadium": (28.6304, 77.2177, "Central Delhi"),
    "Connaught Place": (28.6315, 77.2167, "Central Delhi"),
    "Mori Gate Terminal": (28.6610, 77.2240, "North Corridor"),
    "AIIMS": (28.5672, 77.2100, "Ring Road Corridor"),
    "Safdarjung Hospital": (28.5700, 77.2080, "Ring Road Corridor"),
    "Dhaula Kuan": (28.5921, 77.1614, "Ring Road / Airport Corridor"),
    "Mehrauli Terminal": (28.5195, 77.1818, "South Mehrauli Corridor"),
    "Saket Metro Station": (28.5204, 77.2015, "South Corridor"),
    "Badarpur Border": (28.4984, 77.3045, "Mathura Road Corridor"),
    "Badarpur Border(T)": (28.4990, 77.3050, "Mathura Road Corridor"),
    "Hamdard Nagar / Sangam Vihar": (28.5126, 77.2485, "Mehrauli-Badarpur Corridor"),
    "Kapashera Border": (28.5255, 77.0865, "South-West Corridor"),
    "Mahipal Pur": (28.5444, 77.1278, "Airport Corridor"),
    "Mahipal Pur Village": (28.5430, 77.1260, "Airport Corridor"),
    "Said Ul Zeb Village": (28.5165, 77.2023, "South Corridor"),
    "Ambedkar Nagar Depot": (28.5262, 77.2346, "BRT Corridor"),
    "Andrews Ganj": (28.5684, 77.2248, "Ring Road Corridor"),
    "West Patel Nagar": (28.6508, 77.1585, "West Corridor"),
    "Mother Dairy": (28.6290, 77.2910, "East Corridor"),
    "Nehru Place": (28.5494, 77.2528, "Outer Ring Road"),
    "Nehru Place Terminal": (28.5480, 77.2510, "Outer Ring Road"),
    "Anand Vihar ISBT": (28.6469, 77.3160, "Trans-Yamuna East"),
    "Anand Vihar": (28.6455, 77.3145, "Trans-Yamuna East"),
    "Sarai Kale Khan": (28.5886, 77.2530, "Ring Road East"),
    "Lajpat Nagar": (28.5700, 77.2400, "Ring Road South"),
    "Lajpat Nagar Metro": (28.5710, 77.2410, "Ring Road South"),
    "Punjabi Bagh": (28.6610, 77.1264, "West Ring Road"),
    "Janakpuri": (28.6219, 77.0878, "West Corridor"),
    "Janakpuri District Centre": (28.6280, 77.0820, "West Corridor"),
    "Dwarka Sector 10": (28.5810, 77.0580, "South-West Sub-city"),
    "Dwarka Mor": (28.6190, 77.0330, "West Sub-city"),
    "Uttam Nagar Terminal": (28.6220, 77.0560, "West Corridor"),
    "Rohini Sector 22": (28.7180, 77.0820, "North-West Corridor"),
    "Rohini West": (28.7140, 77.1140, "North-West Corridor"),
    "Pitampura": (28.6980, 77.1400, "North-West Corridor"),
    "Pitampura Nd Block": (28.6990, 77.1390, "North-West Corridor"),
    "GTB Nagar": (28.6978, 77.2064, "North University Corridor"),
    "Gtb Nagar": (28.6978, 77.2064, "North University Corridor"),
    "Vishwa Vidyalaya": (28.6900, 77.2100, "North Campus"),
    "Azadpur": (28.7070, 77.1790, "GT Karnal Corridor"),
    "Azadpur Terminal": (28.7060, 77.1780, "GT Karnal Corridor"),
    "Jahangirpuri": (28.7260, 77.1680, "North Outer Corridor"),
    "Kalkaji Temple": (28.5520, 77.2610, "South-East Corridor"),
    "Govindpuri": (28.5430, 77.2650, "South-East Corridor"),
    "Okhla Phase 3": (28.5350, 77.2720, "Industrial Corridor"),
    "Lal Kuan": (28.5030, 77.2880, "South-East Corridor"),
    "Khanpur Village": (28.5180, 77.2320, "Mehrauli-Badarpur Corridor"),
    "Chhatarpur Metro": (28.5060, 77.1740, "South Corridor"),
    "Chhatarpur Extension": (28.5020, 77.1700, "South Corridor"),
    "Vasant Kunj C-9": (28.5320, 77.1510, "South-West Corridor"),
    "Munirka Village": (28.5580, 77.1720, "Ring Road South"),
    "R.K. Puram Sector 1": (28.5640, 77.1790, "Central-South"),
    "Satya Niketan": (28.5860, 77.1680, "Ring Road South-West"),
    "Naraina Vihar": (28.6270, 77.1380, "Ring Road West"),
    "Raja Garden": (28.6530, 77.1310, "Ring Road West"),
    "Karol Bagh Metro": (28.6440, 77.1890, "Central-West"),
    "Jhandewalan": (28.6430, 77.2000, "Central Corridor"),
    "New Delhi Railway Station": (28.6420, 77.2210, "Central Transit Hub"),
    "Old Delhi Railway Station": (28.6570, 77.2280, "North Central Hub"),
    "Delhi Gate": (28.6410, 77.2410, "Old Delhi Corridor"),
    "ITO Ring Road": (28.6290, 77.2490, "Institutional East"),
    "Pragati Maidan": (28.6180, 77.2440, "Central East"),
    "Nizamuddin Railway Station": (28.5890, 77.2540, "South-East Hub"),
    "Ashok Vihar": (28.6910, 77.1750, "North-West"),
    "Wazirpur Depot": (28.6980, 77.1620, "North-West Industrial"),
    "Shahdara": (28.6730, 77.2880, "Trans-Yamuna North"),
    "Seelampur": (28.6690, 77.2680, "Trans-Yamuna"),
    "Kalyanpuri": (28.6170, 77.3100, "East Delhi Corridor"),
    "Mayur Vihar Phase 1": (28.6040, 77.2940, "East Delhi Corridor"),
    "Mayur Vihar Phase 3": (28.6080, 77.3320, "East Outer Border"),
    "Nangloi": (28.6820, 77.0650, "Rohtak Road West"),
    "Peeragarhi": (28.6780, 77.0930, "West Outer Ring Road"),
    "Mangolpuri": (28.6940, 77.0850, "North-West Corridor"),
    "Sultanpuri": (28.7040, 77.0720, "North-West Outer"),
    "Alipur Village": (28.7990, 77.1330, "GT Karnal North"),
    "Narela Terminal": (28.8530, 77.0920, "North Border Corridor"),
    "Najafgarh Terminal": (28.6120, 76.9850, "Rural-Urban South-West"),
}

print("Starting ETM Data Preprocessing & Aggregation...")
print("Reading CSV chunks from zip file...")

# Aggregation data structures
route_stats = {}
stop_boardings = {}
stop_alightings = {}
hourly_records = []
route_pair_edges = {}

chunk_size = 250000
total_processed = 0

def get_csv_chunks():
    if os.path.exists(RAW_CSV_PATH):
        print(f"Reading directly from CSV: {RAW_CSV_PATH}")
        return pd.read_csv(RAW_CSV_PATH, chunksize=chunk_size, low_memory=False)
    elif os.path.exists(ZIP_PATH):
        print(f"Reading from zip: {ZIP_PATH}")
        z = zipfile.ZipFile(ZIP_PATH)
        f = z.open('October-Delhi.csv')
        return pd.read_csv(f, chunksize=chunk_size, low_memory=False)
    else:
        raise FileNotFoundError(f"Neither {RAW_CSV_PATH} nor {ZIP_PATH} found.")

for chunk in get_csv_chunks():
            # Fill NAs
            chunk['route'] = chunk['route'].fillna('UNKNOWN').astype(str).str.strip()
            chunk['start_stop_name'] = chunk['start_stop_name'].fillna('UNKNOWN').astype(str).str.strip()
            chunk['end_stop_name'] = chunk['end_stop_name'].fillna('UNKNOWN').astype(str).str.strip()
            chunk['passenger_count'] = pd.to_numeric(chunk['passenger_count'], errors='coerce').fillna(1).astype(int)
            chunk['amount'] = pd.to_numeric(chunk['amount'], errors='coerce').fillna(0.0).astype(float)
            chunk['is_ac'] = chunk['is_ac'].astype(str).str.lower().isin(['true', '1', 't'])

            # Datetime processing
            chunk['created_at'] = pd.to_datetime(chunk['created_at'], errors='coerce')
            chunk = chunk.dropna(subset=['created_at'])
            chunk['hour'] = chunk['created_at'].dt.hour
            chunk['date'] = chunk['created_at'].dt.date
            chunk['day_of_week'] = chunk['created_at'].dt.dayofweek
            chunk['is_weekend'] = chunk['day_of_week'].isin([5, 6]).astype(int)

            # Route aggregations
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
                route_stats[route]['ac_count'] += int(grp['is_ac'].sum())
                
                # Frequent origins/destinations
                top_starts = grp['start_stop_name'].value_counts().head(3)
                for s, c in top_starts.items():
                    route_stats[route]['start_stops'][s] = route_stats[route]['start_stops'].get(s, 0) + int(c)
                top_ends = grp['end_stop_name'].value_counts().head(3)
                for s, c in top_ends.items():
                    route_stats[route]['end_stops'][s] = route_stats[route]['end_stops'].get(s, 0) + int(c)

            # Stop aggregations
            for stop, c in chunk['start_stop_name'].value_counts().items():
                stop_boardings[stop] = stop_boardings.get(stop, 0) + int(c)
            for stop, c in chunk['end_stop_name'].value_counts().items():
                stop_alightings[stop] = stop_alightings.get(stop, 0) + int(c)

            # Route pairs (graph edges)
            for (rt, start, end), count in chunk.groupby(['route', 'start_stop_name', 'end_stop_name']).size().items():
                key = (rt, start, end)
                route_pair_edges[key] = route_pair_edges.get(key, 0) + int(count)

            # Hourly aggregated demand per route
            grouped_hourly = chunk.groupby(['route', 'date', 'day_of_week', 'hour', 'is_weekend']).agg(
                passengers=('passenger_count', 'sum'),
                tickets=('passenger_count', 'count'),
                revenue=('amount', 'sum'),
                ac_trips=('is_ac', 'sum')
            ).reset_index()

            hourly_records.append(grouped_hourly)
            total_processed += len(chunk)
            print(f"Processed {total_processed:,} records...")

print("Concatenating hourly demand records...")
df_hourly = pd.concat(hourly_records, ignore_index=True)
# Re-aggregate in case of chunk overlap
df_hourly = df_hourly.groupby(['route', 'date', 'day_of_week', 'hour', 'is_weekend'], as_index=False).agg({
    'passengers': 'sum',
    'tickets': 'sum',
    'revenue': 'sum',
    'ac_trips': 'sum'
})

print(f"Aggregated hourly dataset shape: {df_hourly.shape}")
hourly_csv_gz = os.path.join(DATA_DIR, 'hourly_route_demand.csv.gz')
df_hourly.to_csv(hourly_csv_gz, index=False, compression='gzip')
print(f"Saved hourly demand to {hourly_csv_gz}")

# Select top routes (e.g. routes with >= 500 tickets in the month)
top_routes = {r: data for r, data in route_stats.items() if data['tickets'] >= 500}
print(f"Found {len(top_routes)} prominent routes with >= 500 tickets (out of {len(route_stats)} total)")

# Save route and stop profiles to JSON for fast database seeding and API loading
routes_meta = []
for r, data in top_routes.items():
    primary_origin = max(data['start_stops'].items(), key=lambda x: x[1])[0] if data['start_stops'] else "Origin Hub"
    primary_dest = max(data['end_stops'].items(), key=lambda x: x[1])[0] if data['end_stops'] else "Bus Stand"
    direction = "UP" if "UP" in r.upper() else ("DOWN" if "DOWN" in r.upper() else "CIRCULAR")
    is_ac = (data['ac_count'] / max(1, data['tickets'])) > 0.5
    routes_meta.append({
        'route_id': r,
        'direction': direction,
        'origin': primary_origin,
        'destination': primary_dest,
        'total_tickets': data['tickets'],
        'total_passengers': data['passengers'],
        'total_revenue': round(data['revenue'], 2),
        'is_predominantly_ac': is_ac,
        'avg_daily_passengers': round(data['passengers'] / 30.0, 1)
    })

routes_json = os.path.join(DATA_DIR, 'routes_meta.json')
with open(routes_json, 'w') as f:
    json.dump(routes_meta, f, indent=2)

# Collect top stops
top_stops_list = []
# Ensure all curated stops with coordinates are included
all_notable_stops = set(DELHI_STOP_COORDINATES.keys())
for s, c in sorted(stop_boardings.items(), key=lambda x: x[1], reverse=True)[:300]:
    all_notable_stops.add(s)

# Fallback Delhi high-precision locality resolver for stops
try:
    from fix_all_stop_coordinates import LOCALITY_GEO, resolve_stop_geo
except ImportError:
    try:
        from scripts.fix_all_stop_coordinates import LOCALITY_GEO, resolve_stop_geo
    except ImportError:
        LOCALITY_GEO = {}
        def resolve_stop_geo(name):
            return 28.6139, 77.2090, "Delhi NCT Central"

for s in all_notable_stops:
    if s in DELHI_STOP_COORDINATES:
        lat, lon, corridor = DELHI_STOP_COORDINATES[s]
    else:
        lat, lon, corridor = resolve_stop_geo(s)
    
    boardings = stop_boardings.get(s, 0)
    alightings = stop_alightings.get(s, 0)
    
    top_stops_list.append({
        'name': s,
        'latitude': round(lat, 5),
        'longitude': round(lon, 5),
        'corridor': corridor,
        'monthly_boardings': boardings,
        'monthly_alightings': alightings,
        'is_major_hub': s in DELHI_STOP_COORDINATES or boardings > 1500
    })

stops_json = os.path.join(DATA_DIR, 'stops_meta.json')
with open(stops_json, 'w') as f:
    json.dump(top_stops_list, f, indent=2)

# Save frequent route pair edges for the transit graph
frequent_edges = []
for (rt, start, end), count in route_pair_edges.items():
    if count >= 30 and rt in top_routes:
        frequent_edges.append({
            'route': rt,
            'start_stop': start,
            'end_stop': end,
            'frequency': count
        })

edges_json = os.path.join(DATA_DIR, 'transit_edges.json')
with open(edges_json, 'w') as f:
    json.dump(frequent_edges, f, indent=2)

print(f"Data preprocessing finished successfully!")
print(f"Routes: {len(routes_meta)}, Stops: {len(top_stops_list)}, Transit Edges: {len(frequent_edges)}")
