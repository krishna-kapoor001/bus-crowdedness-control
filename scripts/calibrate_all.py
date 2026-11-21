import csv
import json
import re

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

with open('data/all_stop_names.txt', 'r', encoding='utf-8') as f:
    stops = [s.strip() for s in f if s.strip()]

# Build a lookup table from GTFS
# Direct exact match, direct lower match, cleaned match
gtfs_by_name = {}
gtfs_by_lower = {}
for g in gtfs:
    try:
        lat = float(g['stop_lat'])
        lon = float(g['stop_lon'])
        if 28.35 <= lat <= 28.95 and 76.80 <= lon <= 77.40:
            name = g['stop_name'].strip()
            gtfs_by_name[name] = (lat, lon)
            gtfs_by_lower[name.lower()] = (lat, lon)
    except:
        pass

print(f"Loaded {len(gtfs_by_lower)} unique GTFS stop names.")

# Curated alias / alias mappings for known Delhi transit stops to GTFS names or exact OSM bus bays:
aliases = {
    "adhchini village": (28.5395, 77.1966), # Sri Aurobindo Marg, Adhchini
    "air traffic control office": (28.5620, 77.1180), # IGI Airport / ATC
    "alipur gt road": (28.7980, 77.1352), # Alipur GT Karnal Road
    "alipur village": (28.8005, 77.1340), # Alipur Village
    "ambedkar nagar terminal / dipsar": (28.5159, 77.2255), # Ambedkar Nagar Terminal
    "badarpur m b road / rajiv gandhi stadium": (28.4975, 77.3005), # Badarpur MB Road
    "badli crossing": (28.7286, 77.1463), # Badli Xing
    "begam pur": (28.7225, 77.0540), # Begumpur Barwala Road
    "chhatarpur extension": (28.5020, 77.1780),
    "chhatarpur metro": (28.5065, 77.1745),
    "clal chowk": (28.6500, 77.2300), # Lal Chowk / Chandni Chowk
    "connaught place": (28.6327, 77.2156), # Shivaji Stadium Terminal / CP
    "dabri crossing dwarka road": (28.6137, 77.0857), # Dabri Crossing
    "dabri village": (28.6120, 77.0860), # Dabri
    "dada dev mandir": (28.5835, 77.0805), # Palam / Dada Dev Mandir
    "desu colony janakpuri": (28.6190, 77.0850),
    "devoli road crossing": (28.5085, 77.2340), # Devli Road / Khanpur
    "district centre janak puri": (28.6285, 77.0780), # Janakpuri District Centre
    "g.t.k depot": (28.7312, 77.1586), # GTK Depot
    "government model school": (28.6217, 77.2945), # Govt Model School
    "isbt kashmiri gate": (28.6669, 77.2275), # ISBT Kashmere Gate
    "ito agcr / ito": (28.6300, 77.2450), # ITO AGCR
    "ito-agcr": (28.6300, 77.2450),
    "jahangir puri crossing": (28.7265, 77.1650), # Jahangirpuri Metro/Crossing
    "janakpuri district centre": (28.6285, 77.0780),
    "kalindi kunj border": (28.5445, 77.3115), # Kalindi Kunj Border
    "kalkaji temple": (28.5502, 77.2588), # Kalkaji Mandir Metro / Terminal
    "khanpur extension / devali road xing": (28.5120, 77.2360),
    "khanpur extension / devli road xing / dakshin puri g-block": (28.5120, 77.2360),
    "lado sarai dda flats": (28.5200, 77.1950), # Lado Sarai
    "laxmi nagar (vikas marg) / laxmi nagar metro station": (28.6310, 77.2778),
    "laxmi nagar x-ing / laxmi nagar": (28.6292, 77.2774),
    "laxmi nagar xing": (28.6292, 77.2774),
    "madangir": (28.5255, 77.2310), # Madangir BRT / MB Road
    "madangir dda flats": (28.5240, 77.2290),
    "madangir village": (28.5265, 77.2320),
    "madanpur xing": (28.5270, 77.3060), # Madanpur Khadar Xing
    "mahipal pur village / sec e pkt 2 vasant kunj": (28.5457, 77.1268),
    "mahvir enclave part ii,iii": (28.5980, 77.0780), # Mahavir Enclave
    "mangol pur school (outer ring road)": (28.6940, 77.1050),
    "mayapuri depot crossing": (28.6320, 77.1280),
    "nand nagri depot": (28.6965, 77.3120), # Nand Nagri Depot
    "nangloi (najafgarh road)": (28.6815, 77.0673),
    "narouji nagar": (28.5720, 77.1980), # Nauroji Nagar Ring Road
    "noida sector 37": (28.5630, 77.3340), # Noida Sec 37 Bus Stand (NCT edge)
    "p.s. pahar gunj": (28.6430, 77.2140), # Pahar Ganj Police Station
    "pul prehladpur ( badarpur)": (28.5030, 77.2890), # Pul Prahladpur MB Road
    "punj sons": (28.5330, 77.2660), # Okhla Phase 1 Punj Sons
    "punj sons / govind puri metro station": (28.5340, 77.2650),
    "qutab hotel": (28.5370, 77.1870), # Qutab Hotel Shaheed Jeet Singh Marg
    "r.k. puram sector 1": (28.5642, 77.1785), # RK Puram Sec 1
    "rajindera place metro station": (28.6425, 77.1780),
    "reddison hotel mahipal pur / rang puri (nh8 circle)": (28.5459, 77.1232),
    "rohini sector 22": (28.7230, 77.0750),
    "s.j. hospital": (28.5700, 77.2070), # Safdarjung Hospital Ring Road
    "safdarjung hospital": (28.5700, 77.2070), # Safdarjung Hospital Ring Road
    "sagar pur vashishth park": (28.6010, 77.0940),
    "saket metro sation / said-ul-ajaib": (28.5205, 77.2027),
    "samalkha crossing": (28.5290, 77.0940),
    "samalkha xing": (28.5290, 77.0940),
    "sarai rohella": (28.6626, 77.1823),
    "seikh sarai ph-ii": (28.5360, 77.2280),
    "shakarpur (vikas marg)": (28.6338, 77.2822),
    "shakkar pur school block": (28.6274, 77.2793),
    "sheikh sarai phase ii / shaheed bhagat singh college": (28.5365, 77.2285),
    "sj hospital ring road": (28.5700, 77.2070),
    "south extension petrol pump": (28.5720, 77.2220),
    "uttam nagar (najafgarh road)": (28.6255, 77.0661),
    "vayusena bad": (28.5080, 77.2420), # Vayu Sena Bad / Tigri MB Road
    "vayusenabad (tigri)": (28.5080, 77.2420),
    "zakir hussain college": (28.6412, 77.2296)
}

final_matched = 0
results = {}

for s in stops:
    s_low = s.lower().strip()
    if s_low in aliases:
        results[s] = aliases[s_low]
        final_matched += 1
        continue
    
    # Try exact match in GTFS
    if s_low in gtfs_by_lower:
        results[s] = gtfs_by_lower[s_low]
        final_matched += 1
        continue

    # Try token matching
    words = [w for w in re.split(r'[\s/()\-]+', s_low) if len(w) > 3 and w not in ['road', 'village', 'metro', 'station', 'stand', 'stop', 'terminal', 'gate', 'nagar', 'vihar', 'enclave']]
    best = None
    for g_name, coords in gtfs_by_lower.items():
        if all(w in g_name for w in words):
            best = coords
            break
    if best:
        results[s] = best
        final_matched += 1
    else:
        print(f"STILL UNMATCHED: '{s}'")

print(f"\nTOTAL MATCHED: {final_matched} / {len(stops)} ({final_matched/len(stops)*100:.1f}%)")
