import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

def clean_stops():
    stops_file = os.path.join(PROCESSED_DIR, 'stop_profiles.json')
    meta_file = os.path.join(DATA_DIR, 'stops_meta.json')
    
    with open(stops_file, 'r', encoding='utf-8') as f:
        stops = json.load(f)

    # 1. Deduplicate by clean name lowercase
    unique_stops = {}
    for s in stops:
        name_clean = s['name'].strip()
        name_lower = name_clean.lower()
        
        # Remove phantom / alias duplicates
        if name_lower in ['yamuna vihar', 'c-block yamuna vihar / c4 yamuna vihar']:
            continue
            
        if name_lower not in unique_stops:
            unique_stops[name_lower] = s
        else:
            existing = unique_stops[name_lower]
            existing['monthly_boardings'] = max(existing.get('monthly_boardings', 0), s.get('monthly_boardings', 0))
            existing['monthly_alightings'] = max(existing.get('monthly_alightings', 0), s.get('monthly_alightings', 0))
            if s.get('is_major_hub'):
                existing['is_major_hub'] = True

    cleaned_stops = list(unique_stops.values())
    
    # Save to both locations
    for p in [stops_file, meta_file]:
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(cleaned_stops, f, indent=2)
        print(f"Saved {len(cleaned_stops)} verified unique stops to {p}")

    # 2. Clean CSV files
    for cp in [os.path.join(DATA_DIR, 'delhi_bus_stands_coordinates.csv'), os.path.join(BASE_DIR, 'delhi_bus_stands_coordinates.csv')]:
        if os.path.exists(cp):
            df = pd.read_csv(cp)
            # Remove any phantom rows
            df_filtered = df[~df['bus_stand_name'].str.lower().isin(['yamuna vihar', 'c-block yamuna vihar / c4 yamuna vihar'])].copy()
            df_dedup = df_filtered.drop_duplicates(subset=['bus_stand_name'], keep='first').copy()
            df_dedup.to_csv(cp, index=False)
            print(f"Cleaned {cp}: {len(df_dedup)} unique verified rows")

if __name__ == '__main__':
    clean_stops()
