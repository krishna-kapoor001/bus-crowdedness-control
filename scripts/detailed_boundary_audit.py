import json

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

# Delhi NCT exact geographical polygon approximation:
# Lat min: 28.404, Lat max: 28.883
# Lon min: 76.838, Lon max: 77.348
# Let's check stops near the boundary:
for s in stops:
    lat = s['latitude']
    lon = s['longitude']
    name = s['name']
    
    # Noida check: lon > 77.325 and lat < 28.60 (Noida / Greater Noida)
    if lon > 77.325 and lat < 28.58:
        print(f"OUTSIDE (Noida area): '{name}' ({lat}, {lon})")
    # Gurgaon check: lat < 28.50 and lon < 77.10 (Gurgaon)
    elif lat < 28.48 and lon < 77.10:
        print(f"OUTSIDE (Gurgaon area): '{name}' ({lat}, {lon})")
    # Faridabad check: lat < 28.48 and lon > 77.28 (Faridabad)
    elif lat < 28.48 and lon > 77.28:
        print(f"OUTSIDE (Faridabad area): '{name}' ({lat}, {lon})")
    # Ghaziabad check: lon > 77.34 and lat > 28.62 (Ghaziabad)
    elif lon > 77.34 and lat > 28.62:
        print(f"OUTSIDE (Ghaziabad area): '{name}' ({lat}, {lon})")
    # Bahadurgarh check: lon < 76.88 and lat > 28.65 (Bahadurgarh)
    elif lon < 76.88 and lat > 28.65:
        print(f"OUTSIDE (Bahadurgarh area): '{name}' ({lat}, {lon})")
    # Sonipat / Kundli check: lat > 28.87 (Kundli)
    elif lat > 28.87:
        print(f"OUTSIDE (Sonipat area): '{name}' ({lat}, {lon})")

print("Boundary check complete.")
