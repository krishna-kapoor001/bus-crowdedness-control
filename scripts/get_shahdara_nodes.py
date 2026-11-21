import urllib.request
import json

url = "https://api.openstreetmap.org/api/0.6/way/683662846/full.json"
headers = {'User-Agent': 'TransportDelhiResearch/1.0'}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))

print("=== All nodes in way 683662846 ===")
for el in data.get('elements', []):
    if el.get('type') == 'node':
        print(f"Node {el['id']}: lat={el['lat']}, lon={el['lon']}")

# Also let's query bounding box 28.6735, 77.2855 to 28.6755, 77.2885 using OSM map API!
map_url = "https://api.openstreetmap.org/api/0.6/map?bbox=77.2855,28.6735,77.2885,28.6755"
req2 = urllib.request.Request(map_url, headers=headers)
with urllib.request.urlopen(req2, timeout=10) as resp2:
    xml_data = resp2.read().decode('utf-8')
    with open("scripts/shahdara_osm_map.xml", "w", encoding="utf-8") as f:
        f.write(xml_data)
    print("Saved shahdara_osm_map.xml, size:", len(xml_data))
