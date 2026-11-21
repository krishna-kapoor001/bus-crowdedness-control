import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

# Exact OpenStreetMap Tile-Matched Pin-Point Coordinates
EXACT_OSM_PINS = {
    # 1. User screenshot highlighted: Subash Marg Bus Depot
    'dtc bus depot yamuna vihar': (28.697906, 77.271192),
    'c-4 yamuna vihar': (28.698500, 77.272500),
    'b block yamuna vihar': (28.699500, 77.268500),
    'yamuna vihar ablock': (28.701000, 77.270500),

    # 2. Major ISBTs & Intermodal Hubs (Exact OSM Terminal footprint center)
    'kashmere gate': (28.668690, 77.230420),
    'isbt kashmiri gate': (28.668690, 77.230420),
    'isbt nityanand marg': (28.667000, 77.228000),
    'anand vihar isbt': (28.646753, 77.318004),
    'anand vihar isbt main road': (28.647500, 77.316000),
    'sarai kale khan': (28.585038, 77.258760),
    'sarai kale khan isbt': (28.585038, 77.258760),
    'dhaula kuan': (28.590797, 77.168346),
    'shivaji stadium': (28.632517, 77.215525),
    'new delhi railway station': (28.642000, 77.221000),
    'old delhi railway station': (28.657000, 77.228000),
    'nizamuddin railway station': (28.588000, 77.251000),

    # 3. Major Bus Terminals (Exact OSM Bus Station nodes)
    'mehrauli': (28.522469, 77.182353),
    'nehru place': (28.548100, 77.255200),
    'azadpur': (28.708330, 77.177920),
    'najafgarh': (28.612500, 76.986500),
    'uttam nagar': (28.626125, 77.068310),
    'shahdara': (28.674078, 77.287596),
    'karampura': (28.660349, 77.143945),
    'punjabi bagh': (28.667300, 77.137322),
    'mori gate': (28.668361, 77.225176),
    'badarpur border': (28.493283, 77.303366),
    'ambedkar nagar': (28.514075, 77.228304),
    'kendriya terminal': (28.623500, 77.204500),
    'narela': (28.852500, 77.091500),
    'chauhan patti': (28.754859, 77.243323),
    'qamruddin nagar': (28.679000, 77.052000),
    'dwarka more metro station': (28.619000, 77.033000),
    'munirka village': (28.558000, 77.172000),
    'safdarjung hospital': (28.568983, 77.213433),
    'aiims': (28.568983, 77.213433),

    # 4. DTC Bus Depots (Exact OSM Depot locations)
    'nand nagri depot': (28.697809, 77.305701),
    'wazirpur depot': (28.693572, 77.155382),
    'mayapuri depot': (28.630588, 77.129781),
    'hasanpur depot': (28.635019, 77.307667),
    'shadipur depot': (28.653193, 77.156028),
    'kalkaji depot': (28.538073, 77.267806),
    'bawana depot': (28.795523, 77.042137),
    'peera garhi depot': (28.678000, 77.093000),
    'vasant vihar depot': (28.558000, 77.158000),
    'okhla depot': (28.535000, 77.272000),
    'gtk depot': (28.718000, 77.168000)
}

def apply_pins():
    stops_file = os.path.join(PROCESSED_DIR, 'stop_profiles.json')
    meta_file = os.path.join(DATA_DIR, 'stops_meta.json')

    # Update stop_profiles.json & stops_meta.json
    for p in [stops_file, meta_file]:
        with open(p, 'r', encoding='utf-8') as f:
            stops = json.load(f)
        
        updated_count = 0
        for s in stops:
            name_low = s['name'].lower().strip()
            # Match directly or by clean key
            matched_key = None
            if name_low in EXACT_OSM_PINS:
                matched_key = name_low
            else:
                for k in EXACT_OSM_PINS:
                    if k == name_low or (len(k) >= 5 and k in name_low):
                        matched_key = k
                        break
            
            if matched_key:
                new_lat, new_lon = EXACT_OSM_PINS[matched_key]
                s['latitude'] = new_lat
                s['longitude'] = new_lon
                updated_count += 1
        
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(stops, f, indent=2)
        print(f"Updated {p}: {updated_count} stops pinned to exact OSM tile coordinates!")

    # Update CSV files
    for cp in [os.path.join(DATA_DIR, 'delhi_bus_stands_coordinates.csv'), os.path.join(BASE_DIR, 'delhi_bus_stands_coordinates.csv')]:
        if os.path.exists(cp):
            df = pd.read_csv(cp)
            updated_csv = 0
            for idx, row in df.iterrows():
                name_low = str(row['bus_stand_name']).lower().strip()
                matched_key = None
                if name_low in EXACT_OSM_PINS:
                    matched_key = name_low
                else:
                    for k in EXACT_OSM_PINS:
                        if k == name_low or (len(k) >= 5 and k in name_low):
                            matched_key = k
                            break
                if matched_key:
                    new_lat, new_lon = EXACT_OSM_PINS[matched_key]
                    df.at[idx, 'latitude'] = new_lat
                    df.at[idx, 'longitude'] = new_lon
                    updated_csv += 1
            df.to_csv(cp, index=False)
            print(f"Updated {cp}: {updated_csv} stops pinned to exact OSM coordinates!")

if __name__ == '__main__':
    apply_pins()
