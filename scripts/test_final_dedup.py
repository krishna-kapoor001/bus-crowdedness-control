import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from scripts.build_clean_unified_stops import unified_list, haversine

# Perform a secondary spatial pass: if any two stops are within 35m, merge them into 1!
merged_final = []
used_indices = set()

# Sort by is_major_hub first so hubs take precedence
sorted_stops = sorted(unified_list, key=lambda s: (not s['is_major_hub'], s['name']))

for i, s1 in enumerate(sorted_stops):
    if i in used_indices:
        continue
    cluster = [s1]
    used_indices.add(i)
    
    for j in range(i + 1, len(sorted_stops)):
        if j in used_indices:
            continue
        s2 = sorted_stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d <= 35: # Within 35 meters
            cluster.append(s2)
            used_indices.add(j)
    
    # Choose best name and coordinates
    # If any stop in cluster is major hub, the cluster becomes a major hub
    is_hub = any(c['is_major_hub'] for c in cluster)
    
    # Priority for name: hub name > shorter cleaner name
    hub_stops = [c for c in cluster if c['is_major_hub']]
    if hub_stops:
        best_name = hub_stops[0]['name']
        best_lat = hub_stops[0]['latitude']
        best_lon = hub_stops[0]['longitude']
    else:
        # Cleanest name (without Area or numbers if possible)
        clean_names = sorted([c['name'] for c in cluster], key=lambda x: (len(x), x))
        best_name = clean_names[0]
        best_lat = round(sum(c['latitude'] for c in cluster) / len(cluster), 6)
        best_lon = round(sum(c['longitude'] for c in cluster) / len(cluster), 6)
        
    merged_final.append({
        'name': best_name,
        'latitude': best_lat,
        'longitude': best_lon,
        'is_major_hub': is_hub,
        'merged_count': len(cluster)
    })

print(f"Final Count after 35m spatial merging: {len(merged_final)}")
hubs = [s for s in merged_final if s['is_major_hub']]
stops = [s for s in merged_final if not s['is_major_hub']]
print(f"  Major Bus Stands / Terminals / Depots (Black Dots): {len(hubs)}")
print(f"  Regular Bus Stops (Blue Dots): {len(stops)}")

# Now verify: Are there ANY stops within 25m?
close_count = 0
for i in range(len(merged_final)):
    s1 = merged_final[i]
    for j in range(i+1, len(merged_final)):
        s2 = merged_final[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d < 25:
            close_count += 1
            if close_count <= 5:
                print(f"  Still close: {s1['name']} <-> {s2['name']} ({d:.1f}m)")

print(f"Remaining pairs within 25m: {close_count}")

# Check Yamuna Vihar specifically
print("\n--- Yamuna Vihar Stops in Final Set ---")
for s in merged_final:
    if 'yamuna vihar' in s['name'].lower():
        print(f"  {s['name']}: [{s['latitude']}, {s['longitude']}] (Hub: {s['is_major_hub']}, Merged: {s['merged_count']})")
