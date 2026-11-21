import urllib.request, json

with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/network/geojson') as r:
    data = json.loads(r.read().decode('utf-8'))

features = data['features']
hubs = [f for f in features if f['properties']['is_hub']]
print(f"Total major bus stands (Black Dots): {len(hubs)}")

targets = ['kashmere gate', 'anand vihar', 'yamuna vihar', 'wazirpur', 'hasanpur', 'kalkaji', 'shahdara', 'mori gate', 'nehru place', 'dhaula kuan']
for q in targets:
    m = [h for h in hubs if q in h['properties']['name'].lower()]
    if m:
        props = m[0]['properties']
        coords = m[0]['geometry']['coordinates']
        print(f"  • {q.title()}: Exactly {len(m)} Black Dot -> '{props['name']}' at [lat={coords[1]}, lon={coords[0]}]")
