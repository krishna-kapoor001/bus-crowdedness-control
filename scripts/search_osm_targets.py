import json

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm = json.load(f)

def search_osm(query):
    print(f"\n--- OSM search for '{query}' ---")
    matches = []
    for o in osm:
        name = o.get('name') or ''
        if query.lower() in name.lower():
            lat = o.get('latitude') or o.get('lat')
            lon = o.get('longitude') or o.get('lon')
            matches.append((name, lat, lon, o.get('tags', {})))
    for m in matches[:5]:
        print(f"  '{m[0]}' at ({m[1]}, {m[2]}) tags: {m[3]}")
    if not matches:
        print("  NO MATCHES IN OSM!")

search_osm('najafgarh')
search_osm('yamuna vihar')
search_osm('rohini sec 22')
search_osm('pitampura')
search_osm('pitam pura')
search_osm('ig stadium')
search_osm('indira gandhi stadium')
search_osm('balmiki')
search_osm('aiims')
search_osm('wazirpur depot')
