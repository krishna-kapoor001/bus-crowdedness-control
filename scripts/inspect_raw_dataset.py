import os
import sys
import json
import pandas as pd
import numpy as np

CSV_PATH = os.path.join('data', 'raw', 'October-Delhi.csv')
print(f"Auditing Raw Dataset: {CSV_PATH}")

if not os.path.exists(CSV_PATH):
    print(f"Error: File not found at {CSV_PATH}")
    sys.exit(1)

file_size_bytes = os.path.getsize(CSV_PATH)
file_size_mb = file_size_bytes / (1024 * 1024)
print(f"File Size: {file_size_mb:.2f} MB ({file_size_bytes:,} bytes)")

# 1. Inspect first few lines and columns
with open(CSV_PATH, 'r', encoding='utf-8', errors='ignore') as f:
    header = f.readline().strip()
    sample_rows = [f.readline().strip() for _ in range(5)]

print(f"\nHeader columns: {header}")
columns = [col.strip().strip('"') for col in header.split(',')]
print(f"Parsed {len(columns)} columns: {columns}")

# 2. Process data in chunks to inspect missing values, duplicates, and ranges
print("\nScanning dataset in chunks for missing values, timestamps, and row counts...")

total_rows = 0
missing_counts = {col: 0 for col in columns}
dtypes_set = {col: set() for col in columns}
sample_records = []
min_dt = None
max_dt = None
invalid_dt_count = 0
route_counter = {}
start_stop_counter = {}
end_stop_counter = {}
ac_counter = {True: 0, False: 0}
passenger_count_dist = {}
fare_amount_dist = {}
vehicle_null_count = 0

chunk_size = 300000

for chunk in pd.read_csv(CSV_PATH, chunksize=chunk_size, low_memory=False):
    total_rows += len(chunk)
    
    # Missing values
    for col in columns:
        missing_counts[col] += int(chunk[col].isnull().sum())
    
    # Datetime validation
    dt_series = pd.to_datetime(chunk['created_at'], errors='coerce')
    invalid_dt_count += int(dt_series.isnull().sum())
    valid_dts = dt_series.dropna()
    if not valid_dts.empty:
        c_min = valid_dts.min()
        c_max = valid_dts.max()
        min_dt = c_min if min_dt is None else min(min_dt, c_min)
        max_dt = c_max if max_dt is None else max(max_dt, c_max)

    # Routes
    for r, count in chunk['route'].value_counts().items():
        r_str = str(r).strip()
        route_counter[r_str] = route_counter.get(r_str, 0) + int(count)

    # Stops
    for s, count in chunk['start_stop_name'].value_counts().items():
        s_str = str(s).strip()
        start_stop_counter[s_str] = start_stop_counter.get(s_str, 0) + int(count)
    for s, count in chunk['end_stop_name'].value_counts().items():
        s_str = str(s).strip()
        end_stop_counter[s_str] = end_stop_counter.get(s_str, 0) + int(count)

    # AC vs Non-AC
    chunk['is_ac_clean'] = chunk['is_ac'].astype(str).str.lower().isin(['true', '1', 't'])
    ac_counter[True] += int(chunk['is_ac_clean'].sum())
    ac_counter[False] += int((~chunk['is_ac_clean']).sum())

    # Passenger count distribution
    for pc, count in chunk['passenger_count'].value_counts().items():
        passenger_count_dist[pc] = passenger_count_dist.get(pc, 0) + int(count)

    # Amount sample
    for amt, count in chunk['amount'].value_counts().head(5).items():
        amt_str = str(amt)
        fare_amount_dist[amt_str] = fare_amount_dist.get(amt_str, 0) + int(count)

    print(f"Scanned {total_rows:,} rows...")

print("\n--- DATASET INSPECTION REPORT ---")
print(f"Total Rows: {total_rows:,}")
print(f"Date Range: {min_dt} to {max_dt}")
print(f"Invalid Datetimes: {invalid_dt_count}")
print("\nMissing Values by Column:")
for col, cnt in missing_counts.items():
    pct = (cnt / total_rows) * 100
    print(f"  {col:20s}: {cnt:,} missing ({pct:.2f}%)")

print("\nAC vs Non-AC Bus Fleet Share:")
for is_ac, cnt in ac_counter.items():
    pct = (cnt / total_rows) * 100
    label = "Electric / AC Bus" if is_ac else "Standard / Non-AC Bus"
    print(f"  {label:25s}: {cnt:,} tickets ({pct:.2f}%)")

print("\nPassenger Count Distribution:")
for pc, cnt in sorted(passenger_count_dist.items(), key=lambda x: str(x[0]))[:5]:
    pct = (cnt / total_rows) * 100
    print(f"  {pc} passenger(s): {cnt:,} ({pct:.2f}%)")

print(f"\nUnique Routes: {len(route_counter):,}")
top_routes = sorted(route_counter.items(), key=lambda x: x[1], reverse=True)[:10]
print("Top 10 Routes by Ticket Count:")
for r, c in top_routes:
    print(f"  Route {r:12s}: {c:,} tickets")

print(f"\nUnique Start Stops: {len(start_stop_counter):,}")
print(f"Unique End Stops:   {len(end_stop_counter):,}")
top_start_stops = sorted(start_stop_counter.items(), key=lambda x: x[1], reverse=True)[:10]
print("Top 10 Start Stops (Boardings):")
for s, c in top_start_stops:
    print(f"  {s:35s}: {c:,} boardings")

# Save inspection summary to json
summary = {
    "file_path": CSV_PATH,
    "file_size_bytes": file_size_bytes,
    "file_size_mb": round(file_size_mb, 2),
    "total_rows": total_rows,
    "columns": columns,
    "missing_values": missing_counts,
    "timestamp_min": str(min_dt),
    "timestamp_max": str(max_dt),
    "invalid_timestamps": invalid_dt_count,
    "unique_routes": len(route_counter),
    "unique_start_stops": len(start_stop_counter),
    "unique_end_stops": len(end_stop_counter),
    "ac_share_pct": round((ac_counter[True] / total_rows) * 100, 2),
    "top_routes": [{"route": r, "tickets": c} for r, c in top_routes],
    "top_stops": [{"stop": s, "boardings": c} for s, c in top_start_stops]
}

os.makedirs('data/processed', exist_ok=True)
with open('data/processed/dataset_inspection_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("\nSaved inspection summary to data/processed/dataset_inspection_summary.json")
