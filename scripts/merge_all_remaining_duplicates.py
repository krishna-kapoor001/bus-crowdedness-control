import json
import math
import re

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# Explicit duplicate mappings: (target_canonical_name, [duplicate_aliases_to_merge_into_it])
DUPLICATE_CLUSTERS = [
    ("Shahdara Border", ["Shahdra Border", "Shahadara Border"]),
    ("Qutub Minar", ["Qutab Minar", "Qutub Minar Bus StopSation"]),
    ("Rajiv Nagar", ["Rajeev Nagar"]),
    ("Prem Bari Pul", ["Prem Bari Pull"]),
    ("Samalkha More", ["Samalka Crossing"]),
    ("Don Bosco School", ["Don Basco School"]),
    ("Najafgarh Terminal", ["Nazafgarh Terminal"]),
    ("Mayur Vihar Phase 3 Crossing", ["Mayur vihar Phase III Crossing"]),
    ("Max Mueller Bhawan", ["Max Muller Bhawan"]),
    ("Shahjahan Road UPSC", ["Shajahan Road UPSC"]),
    ("Burari Transport Authority", ["Burari Transport Authourity"]),
    ("Shadipur DTC Colony", ["Shadipur Colony"]),
    ("Anand Gram", ["Anand Gram Ashram"]),
    ("Dhakka Village", ["Daka Village"]),
    ("Madhuban Chowk", ["Madhuvan Chowk"]),
    ("IA Block Ashok Vihar", ["JA Block Ashok Vihar"]),
    ("Tagore Garden", ["Tagore Garden Tatarpur"]),
    ("Peera Garhi Chowk", ["Peera Garhi"]),
    ("Prithviraj Road Crossing", ["Prithvi Raj Road"]),
    ("Police Station Nizamuddin", ["DPS Police Station Nizamuddin", "P S Nizamuddin"]),
    ("Kasturba Gandhi Crossing", ["Kasturba Gandhi Road Crossing", "Kasturba Gandhi crossing"]),
    ("RK Puram Sec 9", ["R K Puram Sec 8 9"]),
    ("RK Puram Sec 1", ["RK Puram Sec 1 4"]),
    ("Government Model School", ["Govt Model School Ambedkar Park"]),
    ("Lodhi Road Crossing", ["Lodhi Estate crossing"]),
    ("Seelampur", ["Seelam Pur", "Seelam Pur Bus StopMall"]),
    ("Shastri Park Depot", ["Shastri Park Bus Depot"]),
    ("Karol Bagh", ["Karol Bagh Terminal"]),
    ("New Delhi Railway Station", ["New Delhi Railway Station Gate 2"]),
]

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Initial stops count: {len(stops)}")

stop_dict = {s['name']: s for s in stops}
merged_out_names = set()

for target_name, dupes in DUPLICATE_CLUSTERS:
    # Find or establish target
    target_stop = stop_dict.get(target_name)
    if not target_stop:
        # maybe one of the dupes exists
        for d in dupes:
            if d in stop_dict:
                target_stop = stop_dict[d]
                target_stop['name'] = target_name
                stop_dict[target_name] = target_stop
                break

    if not target_stop:
        continue

    for d in dupes:
        if d in stop_dict and d != target_name and d not in merged_out_names:
            dupe_stop = stop_dict[d]
            # Merge ridership
            target_stop['monthly_boardings'] += dupe_stop.get('monthly_boardings', 0)
            target_stop['monthly_alightings'] += dupe_stop.get('monthly_alightings', 0)
            target_stop['is_major_hub'] = target_stop.get('is_major_hub', False) or dupe_stop.get('is_major_hub', False)
            merged_out_names.add(d)
            print(f"  Merged duplicate '{d}' -> '{target_name}' (added {dupe_stop.get('monthly_boardings', 0)} pax)")

# Filter out merged duplicates
clean_stops = [s for s in stops if s['name'] not in merged_out_names]

# Also ensure target stops have their updated data in clean_stops
final_stops = []
seen = set()
for s in clean_stops:
    name = s['name']
    if name in seen:
        continue
    seen.add(name)
    if name in stop_dict:
        final_stops.append(stop_dict[name])
    else:
        final_stops.append(s)

final_stops.sort(key=lambda x: x['monthly_boardings'], reverse=True)

print(f"\nTotal removed duplicate stops: {len(merged_out_names)}")
print(f"Final clean unique stops: {len(final_stops)}")

# Save to data/processed/stop_profiles.json and data/stops_meta.json
with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(final_stops, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(final_stops, f, indent=2, ensure_ascii=False)

print("Saved cleanly merged master stops to data files!")
