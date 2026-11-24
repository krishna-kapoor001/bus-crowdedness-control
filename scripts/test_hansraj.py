import urllib.request
import urllib.parse
import json

query = """
[out:json];
node(around:200,28.679099,77.20837)["highway"="bus_stop"];
out;
"""
url = "https://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(query)
req = urllib.request.Request(url, headers={"User-Agent": "TransportDelhiAudit/1.0"})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        print("Elements found in Overpass:", len(data.get("elements", [])))
        for el in data.get("elements", []):
            print(el.get("id"), el.get("lat"), el.get("lon"), el.get("tags", {}).get("name"))
except Exception as e:
    print("Error:", e)
