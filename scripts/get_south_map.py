import urllib.request

url = "https://api.openstreetmap.org/api/0.6/map?bbox=77.2855,28.6715,77.2895,28.6735"
headers = {'User-Agent': 'TransportDelhiResearch/1.0'}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    data = resp.read().decode('utf-8')
    with open("scripts/shahdara_south_map.xml", "w", encoding="utf-8") as f:
        f.write(data)
    print("South map downloaded, size:", len(data))
