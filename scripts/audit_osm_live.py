import urllib.request
import urllib.parse
import json
import time

targets = [
    "DTC Bus Depot Yamuna Vihar, Delhi",
    "Shahdara Bus Terminal, Delhi",
    "ISBT Kashmere Gate, Delhi",
    "Anand Vihar ISBT, Delhi",
    "Sarai Kale Khan ISBT, Delhi",
    "Nehru Place Bus Terminal, Delhi",
    "Mehrauli Bus Terminal, Delhi",
    "Azadpur Bus Terminal, Delhi",
    "Mori Gate Bus Terminal, Delhi",
    "Najafgarh Bus Terminal, Delhi",
    "Uttam Nagar Bus Terminal, Delhi",
    "Karampura Bus Terminal, Delhi",
    "Punjabi Bagh Bus Terminal, Delhi",
    "Badarpur Bus Terminal, Delhi",
    "Ambedkar Nagar Bus Depot, Delhi",
    "Kendriya Terminal, Delhi",
    "Shivaji Stadium Bus Terminal, Delhi",
    "Dhaula Kuan Bus Stop, Delhi",
    "Nand Nagri Bus Depot, Delhi",
    "Wazirpur Bus Depot, Delhi",
    "Mayapuri Bus Depot, Delhi",
    "Hasanpur Bus Depot, Delhi",
    "Shadipur Bus Depot, Delhi",
    "Kalkaji Bus Depot, Delhi",
    "Bawana Bus Depot, Delhi",
    "Vasant Vihar Bus Depot, Delhi",
    "Rohini Bus Depot 1, Delhi",
    "East Vinod Nagar Bus Depot, Delhi",
    "BBM Bus Depot, Delhi",
    "Okhla Bus Depot, Delhi"
]

results = {}
for q in targets:
    try:
        url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
            'q': q,
            'format': 'json',
            'limit': 1
        })
        req = urllib.request.Request(url, headers={'User-Agent': 'DelhiTransitAudit/2.0 (contact@flowpulse.delhi.gov.in)'})
        with urllib.request.urlopen(req, timeout=5) as r:
            res = json.loads(r.read().decode('utf-8'))
            if res:
                results[q] = (float(res[0]['lat']), float(res[0]['lon']), res[0]['display_name'])
                print(f"✓ {q} -> ({res[0]['lat']}, {res[0]['lon']})")
            else:
                print(f"- No result for: {q}")
        time.sleep(1.0) # Respect OSM Nominatim 1 request/sec rate limit
    except Exception as e:
        print(f"! Error for {q}: {e}")

with open('data/osm_live_verified_hubs.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"\nSaved {len(results)} live 2026 OSM ground truth hubs to data/osm_live_verified_hubs.json!")
