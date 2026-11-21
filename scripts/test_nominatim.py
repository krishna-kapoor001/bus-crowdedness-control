import urllib.request
import urllib.parse
import json

url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
    'q': 'DTC Bus Depot Yamuna Vihar, Delhi',
    'format': 'json',
    'limit': 1
})

req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhiBot/1.0 (contact@transportdelhi.org)'})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode('utf-8'))
        print(f"Nominatim status: {r.status}, results: {len(res)}")
        if res:
            print(f"  Result: {res[0]['display_name']} -> ({res[0]['lat']}, {res[0]['lon']})")
except Exception as e:
    print("Nominatim error:", e)
