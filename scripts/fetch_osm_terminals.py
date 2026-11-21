import urllib.request
import urllib.parse
import json
import time

key_terminals = [
    ('Shahdara Terminal', 'Shahdara'),
    ('Shahdara Terminal', 'Shahdara Terminal'),
    ('Kashmere Gate ISBT', 'ISBT Kashmiri Gate'),
    ('Anand Vihar ISBT', 'Anand Vihar Isbt'),
    ('Sarai Kale Khan ISBT', 'Sarai Kale Khan Isbt'),
    ('Mehrauli Bus Terminal', 'Mehrauli'),
    ('Najafgarh Bus Terminal', 'Najafgarh'),
    ('Uttam Nagar Bus Terminal', 'Uttam Nagar'),
    ('Azadpur Bus Terminal', 'Azadpur'),
    ('Mori Gate Bus Terminal', 'Mori Gate'),
    ('Shivaji Stadium Bus Terminal', 'Shivaji Stadium'),
    ('Kendriya Terminal New Delhi', 'Kendriya'),
    ('Nehru Place Bus Terminal', 'Nehru Place'),
    ('Ambedkar Nagar Bus Terminal', 'Ambedkar Nagar'),
    ('Badarpur Border Bus Terminal', 'Badarpur Border'),
    ('Nand Nagri Bus Depot', 'Nand Nagri Depot'),
    ('Mayapuri Bus Depot', 'Maya Puri Depot'),
    ('Kalkaji Bus Depot', 'Kalkaji Depot'),
    ('Hasanpur Bus Depot', 'Hasan Pur Depot'),
    ('Shadipur Bus Depot', 'Shadipur Depot'),
    ('Wazirpur Bus Depot', 'Wazirpur Depot'),
    ('GTK Bus Depot', 'GTK Depot'),
    ('Peeragarhi Bus Depot', 'Peera Garhi Depot'),
    ('Vasant Vihar Bus Depot', 'Vasant Vihar Depot'),
    ('DTC Bus Depot Yamuna Vihar', 'DTC Bus Depot Yamuna Vihar'),
    ('Rohini Bus Depot 1', 'Rohini Depot 1 Sec 6'),
    ('Rohini Bus Depot 2', 'Rohini Depot Ii'),
    ('Rohini Bus Depot 3', 'Rohini Depot - 3'),
    ('Dichau Kalan Bus Depot', 'Dichau Kalan Depot'),
    ('Kanjhawala Bus Depot', 'Kanjhawala Depot'),
    ('Naraina Bus Depot', 'Naraina Depot'),
    ('Ghazipur Bus Depot', 'Gazipur Depot'),
    ('Hari Nagar Bus Depot', 'Hari Nagar Depot'),
    ('Rajghat DTC Depot', 'Dtc Rajghat Depot'),
    ('IP Bus Depot Delhi', 'Ip Depot Metro Station'),
    ('Kapashera Border', 'Kapashera Border'),
    ('Narela Bus Terminal', 'Narela'),
    ('Bawana Bus Stand', 'Bawana'),
    ('Karampura Bus Terminal', 'Karampura'),
    ('Punjabi Bagh Bus Terminal', 'Punjabi Bagh Terminal'),
    ('Jal Vihar Terminal', 'Jal Vihar'),
    ('Malka Ganj Terminal', 'Malka Ganj'),
    ('New Seema Puri Bus Stand', 'New Seema Puri'),
    ('Vivek Vihar Bus Terminal', 'Vivek Vihar'),
    ('Chauhan Patti Terminal', 'Chauhan Patti'),
    ('Qamruddin Nagar Terminal', 'Qamruddin Nagar')
]

results = {}
headers = {'User-Agent': 'TransportDelhiOsmAudit/1.0'}

for q, target_name in key_terminals:
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(q + ', Delhi')}&format=json&limit=1"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            if data:
                item = data[0]
                lat = float(item['lat'])
                lon = float(item['lon'])
                results[target_name] = (lat, lon, item['display_name'])
                print(f"FOUND: '{target_name}' -> ({lat}, {lon}) | {item['display_name'][:60]}")
            else:
                print(f"NOT FOUND for query: '{q}'")
    except Exception as e:
        print(f"ERROR for '{q}': {e}")
    time.sleep(0.6)

with open('data/osm_terminal_pins.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"\nSaved {len(results)} exact OSM terminal pins!")
