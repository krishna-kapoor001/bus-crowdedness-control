import urllib.request
import urllib.parse
import json
import time
import math

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

# Priority hubs
priority_hubs = [
    # ISBTs & Intermodal
    ('DTC Bus Depot Yamuna Vihar', 'DTC Bus Depot Yamuna Vihar, Subash Marg, Delhi'),
    ('Kashmere Gate', 'Maharana Pratap Inter State Bus Terminus, Kashmere Gate, Delhi'),
    ('Anand Vihar ISBT', 'Swami Vivekanand ISBT, Anand Vihar, Delhi'),
    ('Sarai Kale Khan', 'Sarai Kale Khan ISBT, Ring Road, Delhi'),
    ('Dhaula Kuan', 'Dhaula Kuan Bus Stop, Ring Road, Delhi'),
    
    # Key Bus Terminals
    ('Mehrauli', 'Mehrauli Bus Terminal, Delhi'),
    ('Shivaji Stadium', 'Shivaji Stadium Bus Terminal, Connaught Place, Delhi'),
    ('Nehru Place', 'Nehru Place Bus Terminal, Delhi'),
    ('Azadpur', 'Azadpur Bus Terminal, GT Karnal Road, Delhi'),
    ('Najafgarh', 'Najafgarh Bus Terminal, Delhi'),
    ('Uttam Nagar', 'Uttam Nagar Bus Terminal, Delhi'),
    ('Shahdara', 'Shahdara Bus Terminal, Delhi'),
    ('Karampura', 'Karampura Bus Terminal, Delhi'),
    ('Punjabi Bagh', 'Punjabi Bagh Bus Terminal, Delhi'),
    ('Narela', 'Narela Bus Terminal, Delhi'),
    ('Chauhan Patti', 'Chauhan Patti, Burari, Delhi'),
    ('Badarpur Border', 'Badarpur Border Bus Terminal, Mathura Road, Delhi'),
    ('Ambedkar Nagar', 'Ambedkar Nagar Bus Depot, Delhi'),
    ('Mori Gate', 'Mori Gate Bus Terminal, Delhi'),
    ('Kendriya Terminal', 'Kendriya Terminal, Gurudwara Rakab Ganj, Delhi'),

    # Key DTC Bus Depots
    ('Nand Nagri Depot', 'Nand Nagri Bus Depot, Delhi'),
    ('Wazirpur Depot', 'Wazirpur DTC Depot, Netaji Subhash Place, Delhi'),
    ('Mayapuri Depot', 'Mayapuri DTC Depot, Delhi'),
    ('Kalkaji Depot', 'Kalkaji Bus Depot, Govindpuri, Delhi'),
    ('Peera Garhi Depot', 'Peeragarhi Bus Depot, Rohtak Road, Delhi'),
    ('Hasanpur Depot', 'Hasanpur Bus Depot, IP Extension, Delhi'),
    ('Shadipur Depot', 'Shadipur DTC Depot, Patel Road, Delhi'),
    ('GTK Depot', 'GTK Bus Depot, GT Karnal Road, Delhi'),
    ('Vasant Vihar Depot', 'Vasant Vihar Bus Depot, Delhi'),
    ('Okhla Depot', 'Okhla Bus Depot, Phase 1, Delhi'),
    ('Dichau Kalan Depot', 'Dichau Kalan Depot, Najafgarh, Delhi'),
    ('Kanjhawala Depot', 'Kanjhawala Bus Depot, Delhi'),
    ('Rohini Depot 1', 'Rohini Bus Depot, Sector 1, Delhi'),
    ('Bawana Depot', 'Bawana Bus Depot, Delhi'),
    ('Seemapuri Depot', 'Seemapuri Bus Depot, Delhi'),
    ('Yamuna Depot', 'Yamuna Bus Depot, Delhi')
]

results = {}
for stop_name, search_query in priority_hubs:
    q = urllib.parse.quote(search_query)
    url = f"https://nominatim.openstreetmap.org/search?q={q}&format=json&limit=1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'DelhiTransitAlign/2.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data:
                lat = round(float(data[0]['lat']), 6)
                lon = round(float(data[0]['lon']), 6)
                results[stop_name] = (lat, lon, data[0].get('display_name', ''))
                print(f"✓ {stop_name:<25} -> {lat}, {lon}")
            else:
                print(f"! {stop_name:<25} -> No OSM match")
        time.sleep(0.8)
    except Exception as e:
        print(f"x {stop_name:<25} -> Error: {e}")

with open('data/osm_aligned_hubs.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"\nSaved {len(results)} exact OSM-aligned hubs to data/osm_aligned_hubs.json")
