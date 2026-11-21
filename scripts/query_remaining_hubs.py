import urllib.request
import urllib.parse
import json
import time

queries = [
    ('Kashmere Gate ISBT', 'Maharana Pratap Inter State Bus Terminus'),
    ('Anand Vihar ISBT', 'Anand Vihar ISBT'),
    ('Sarai Kale Khan ISBT', 'Sarai Kale Khan ISBT'),
    ('Nehru Place', 'Nehru Place Terminal'),
    ('Azadpur', 'Azadpur Terminal'),
    ('Najafgarh', 'Najafgarh Terminal'),
    ('Uttam Nagar', 'Uttam Nagar Terminal'),
    ('Badarpur Border', 'Badarpur Border'),
    ('Ambedkar Nagar', 'Ambedkar Nagar Terminal'),
    ('Wazirpur Depot', 'Wazirpur Depot'),
    ('Mayapuri Depot', 'Mayapuri Depot'),
    ('Hasanpur Depot', 'Hasanpur Depot'),
    ('Shadipur Depot', 'Shadipur Depot'),
    ('GTK Depot', 'GTK Depot'),
    ('Karampura', 'Karampura Terminal'),
    ('Punjabi Bagh', 'Punjabi Bagh Terminal'),
    ('Narela', 'Narela Terminal')
]

for name, q_str in queries:
    q = urllib.parse.quote(f"{q_str}, Delhi")
    url = f"https://nominatim.openstreetmap.org/search?q={q}&format=json&limit=1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'DelhiTransitAlign/3.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data:
                lat = round(float(data[0]['lat']), 6)
                lon = round(float(data[0]['lon']), 6)
                print(f"'{name}': ({lat}, {lon}),")
            else:
                print(f"# No match: {name}")
        time.sleep(0.8)
    except Exception as e:
        print(f"# Error: {name} - {e}")
