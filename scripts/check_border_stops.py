import json

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

# Extreme coordinates check
# Delhi NCT latitude: ~28.404 to 28.883
# Delhi NCT longitude: ~76.838 to 77.348
suspects = []
for s in stops:
    lat = s['latitude']
    lon = s['longitude']
    name = s['name']
    
    # Check east of Yamuna / UP border (longitude > 77.335 often enters Noida or Ghaziabad)
    if lon > 77.330:
        suspects.append((name, lat, lon, 'East of 77.330 (potential Noida/Ghaziabad)'))
    # Check south of Badarpur / Aya Nagar (latitude < 28.47 often enters Faridabad or Gurgaon)
    elif lat < 28.470:
        suspects.append((name, lat, lon, 'South of 28.470 (potential Faridabad/Gurgaon)'))
    # Check west of Najafgarh / Dhansa (longitude < 76.84)
    elif lon < 76.850:
        suspects.append((name, lat, lon, 'West of 76.850 (potential Haryana)'))
    # Check north of Singhu (latitude > 28.88)
    elif lat > 28.880:
        suspects.append((name, lat, lon, 'North of 28.880 (potential Sonipat)'))

print(f"Total suspect border/outside stops: {len(suspects)}")
for s in suspects:
    print(f"  '{s[0]}': ({s[1]}, {s[2]}) -> {s[3]}")
