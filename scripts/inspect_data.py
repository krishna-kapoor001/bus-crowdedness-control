import zipfile
import pandas as pd
import numpy as np

zip_path = r'C:\Users\Hp\Downloads\October-Delhi.csv.zip'
print("Reading dataset sample...")

with zipfile.ZipFile(zip_path) as z:
    with z.open('October-Delhi.csv') as f:
        df = pd.read_csv(f, nrows=500000)

df['created_at'] = pd.to_datetime(df['created_at'])
df['hour'] = df['created_at'].dt.hour
df['day_name'] = df['created_at'].dt.day_name()
df['date'] = df['created_at'].dt.date

print(f"Sample size: {len(df):,} records")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print("\nHourly trip distribution (%):")
hour_counts = df['hour'].value_counts(normalize=True).sort_index() * 100
for h, pct in hour_counts.items():
    bar = '#' * int(pct * 2)
    print(f"Hour {h:02d}: {pct:5.2f}% {bar}")

print("\nDay of week trip distribution (%):")
dow_counts = df['day_name'].value_counts(normalize=True) * 100
for d, pct in dow_counts.items():
    print(f"{d:10s}: {pct:5.2f}%")

print(f"\nTotal unique routes in 500k sample: {df['route'].nunique()}")
top_15_routes = df['route'].value_counts().head(15)
print("\nTop 15 routes by ticket count:")
for r, c in top_15_routes.items():
    print(f"Route {r:10s}: {c:,} tickets")

top_15_stops = df['start_stop_name'].value_counts().head(15)
print("\nTop 15 start stops:")
for s, c in top_15_stops.items():
    print(f"{s:30s}: {c:,} boardings")
