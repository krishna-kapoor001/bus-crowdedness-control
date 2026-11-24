import json
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Stops count before cleanup: {len(stops)}")

# 1. Coordinate alignments to exact OSM bus stop nodes
snap_fixes = {
    'Najafgarh Terminal': (28.611651, 76.978471),       # Najafgarh Dhansa Bus Stand
    'AIIMS Transit Hub': (28.568849, 77.213239),        # AIIMS main bus platform
    'IG Stadium': (28.632931, 77.247190),               # Indira Gandhi Stadium
    'Wazirpur Depot': (28.691918, 77.153692),           # Wazirpur Depot bus platform
    'Uttri Pitam Pura': (28.715078, 77.138988),         # Uttari Pitampura OSM platform
}

for s in stops:
    if s['name'] in snap_fixes:
        s['latitude'] = snap_fixes[s['name']][0]
        s['longitude'] = snap_fixes[s['name']][1]
        print(f"Snapped '{s['name']}' to exact OSM coordinates: {snap_fixes[s['name']]}")

# 2. Demote non-hub roadside stops and minor colony turnarounds (removing unwanted black dots)
demote_to_regular = [
    'Supply Depot (Delhi Cantt)',
    'Ordnance Depot (Shakurbasti)',
    'Okhla Depot Iv Cws Ii',
    'Tara Apartments Terminal',
    'Jai Mata Market Tri Nagar Terminal',
    'Khayala Colony Terminal',
    'E Block Jahangir Puri Terminal',
    'East Vinod Nagar Depot',
    'Rohini Depot 2',
    'Rohini Depot 3',
    'Sriniwaspuri DTC Depot (SNPD)',
    'Malka Ganj Terminal',
    'West Enclave Terminal',
    'BBM DTC Depot (Kingsway Camp)',
    'Dichau Kalan Depot',
    'Vivek Vihar Terminal',
    'Ambedkar Stadium Terminal',
    'Dilshad Garden Depot Cluster',
    'Janak Puri B 1 Terminal',
    'Kalyan Puri Terminal',
    'Mangla Puri Terminal',
    'Jal Vihar Terminal',
    'Jheel Terminal',
    'Karampura Terminal',
    'Keshopur Depot',
    'Peera Garhi Depot',
    'Pragati Maidan Terminal',
    'Safdurjung Terminal',
]

demoted_count = 0
for s in stops:
    if s['name'] in demote_to_regular and s.get('is_major_hub'):
        s['is_major_hub'] = False
        demoted_count += 1

print(f"Demoted {demoted_count} non-hub/colony stops to regular stops (is_major_hub=False).")

# 3. Remove fake/empty-road dots that have no OSM bus stop:
# Yamuna Vihar DTC Depot (516m from any stop on empty residential road)
# Rohini Sec 22 Terminal (401m from any stop on empty road)
remove_empty_road = {'Yamuna Vihar DTC Depot', 'Rohini Sec 22 Terminal'}
filtered = [s for s in stops if s['name'] not in remove_empty_road]

print(f"Removed {len(stops) - len(filtered)} empty-road orphan dots. Final stop count: {len(filtered)}")

# Check remaining major hubs (official Bus Stands & Terminals)
remaining_hubs = [s for s in filtered if s.get('is_major_hub')]
print(f"Remaining clean, official Major Bus Stands & Terminals: {len(remaining_hubs)}")

for idx, h in enumerate(remaining_hubs, 1):
    print(f"  {idx:2d}. {h['name']} ({h['latitude']}, {h['longitude']})")

# Save datasets cleanly
filtered.sort(key=lambda x: x['monthly_boardings'], reverse=True)

with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

print("Saved cleanly to stop_profiles.json and stops_meta.json!")
