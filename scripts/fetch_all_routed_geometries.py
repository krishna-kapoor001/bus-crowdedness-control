import json
import urllib.request
import concurrent.futures
import time
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
OUT_FILE = os.path.join(PROCESSED_DIR, 'corridors_routed.json')

CORRIDOR_WAYPOINTS = [
    {
        "id": "corridor-ring",
        "type": "corridor",
        "name": "Ring Road Arterial (Kashmere Gate ↔ AIIMS ↔ Sarai Kale Khan)",
        "crowd_level": "VERY HIGH",
        "avg_speed_kmh": 16.4,
        "routes_count": "48 routes",
        "stops": [
            "Kashmere Gate", "Rajghat", "ITO Ring Road",
            "Sarai Kale Khan", "Ashram", "Lajpat Nagar",
            "AIIMS", "Safdarjung Hospital", "Moti Bagh", "Dhaula Kuan"
        ],
        "waypoints": [
            [28.6685, 77.2295],
            [28.6450, 77.2470],
            [28.6290, 77.2490],
            [28.5886, 77.2530],
            [28.5700, 77.2550],
            [28.5700, 77.2400],
            [28.5672, 77.2100],
            [28.5700, 77.2080],
            [28.5860, 77.1680],
            [28.5921, 77.1614]
        ]
    },
    {
        "id": "corridor-mb",
        "type": "corridor",
        "name": "Mehrauli-Badarpur Corridor (Mehrauli ↔ Saket ↔ Badarpur Border)",
        "crowd_level": "VERY HIGH",
        "avg_speed_kmh": 14.8,
        "routes_count": "32 routes",
        "stops": [
            "Mehrauli Terminal", "Lado Sarai", "Saket Metro Station",
            "Khanpur Village", "Hamdard Nagar / Sangam Vihar", "Lal Kuan", "Badarpur Border"
        ],
        "waypoints": [
            [28.5195, 77.1818],
            [28.5220, 77.1980],
            [28.5204, 77.2015],
            [28.5180, 77.2320],
            [28.5126, 77.2485],
            [28.5030, 77.2880],
            [28.4984, 77.3045]
        ]
    },
    {
        "id": "corridor-outer-ring",
        "type": "corridor",
        "name": "Outer Ring Road Arterial (Munirka ↔ IIT Gate ↔ Nehru Place ↔ Okhla)",
        "crowd_level": "VERY HIGH",
        "avg_speed_kmh": 18.2,
        "routes_count": "35 routes",
        "stops": [
            "Munirka Village", "IIT Gate", "Hauz Khas", "Chirag Delhi", "Nehru Place", "Okhla"
        ],
        "waypoints": [
            [28.5580, 77.1720],
            [28.5440, 77.1930],
            [28.5435, 77.2060],
            [28.5470, 77.2250],
            [28.5494, 77.2528],
            [28.5350, 77.2750]
        ]
    },
    {
        "id": "corridor-airport",
        "type": "corridor",
        "name": "Airport Expressway Corridor (Dhaula Kuan ↔ Mahipalpur ↔ Kapashera)",
        "crowd_level": "HIGH",
        "avg_speed_kmh": 22.5,
        "routes_count": "24 routes",
        "stops": [
            "Dhaula Kuan", "Satya Niketan", "Mahipal Pur", "Shiv Murti", "Kapashera Border"
        ],
        "waypoints": [
            [28.5921, 77.1614],
            [28.5860, 77.1680],
            [28.5444, 77.1278],
            [28.5330, 77.1120],
            [28.5255, 77.0865]
        ]
    },
    {
        "id": "corridor-transyamuna",
        "type": "corridor",
        "name": "Trans-Yamuna East Corridor (Shahdara ↔ Anand Vihar ISBT ↔ Mayur Vihar)",
        "crowd_level": "HIGH",
        "avg_speed_kmh": 17.5,
        "routes_count": "28 routes",
        "stops": [
            "Shahdara", "Seelampur", "Laxmi Nagar", "Anand Vihar ISBT", "Mayur Vihar Phase 1"
        ],
        "waypoints": [
            [28.6730, 77.2880],
            [28.6650, 77.2750],
            [28.6310, 77.2770],
            [28.6469, 77.3160],
            [28.6040, 77.2940]
        ]
    },
    {
        "id": "corridor-gtk",
        "type": "corridor",
        "name": "GT Karnal Highway Corridor (Azadpur ↔ Jahangirpuri ↔ Singhu Border)",
        "crowd_level": "VERY HIGH",
        "avg_speed_kmh": 24.0,
        "routes_count": "30 routes",
        "stops": [
            "Azadpur Terminal", "Model Town", "Jahangirpuri", "Mukarba Chowk", "Alipur", "Singhu Border"
        ],
        "waypoints": [
            [28.7070, 77.1790],
            [28.7180, 77.1750],
            [28.7260, 77.1680],
            [28.7520, 77.1550],
            [28.7990, 77.1330],
            [28.8250, 77.1200]
        ]
    },
    {
        "id": "corridor-aurobindo",
        "type": "corridor",
        "name": "Aurobindo Marg Corridor (Safdarjung Tomb ↔ AIIMS ↔ Mehrauli)",
        "crowd_level": "HIGH",
        "avg_speed_kmh": 17.1,
        "routes_count": "29 routes",
        "stops": [
            "Safdarjung Tomb", "AIIMS", "Green Park", "IIT Gate", "Qutub Minar", "Mehrauli Terminal"
        ],
        "waypoints": [
            [28.5880, 77.2100],
            [28.5672, 77.2100],
            [28.5560, 77.2060],
            [28.5440, 77.1930],
            [28.5245, 77.1855],
            [28.5195, 77.1818]
        ]
    },
    {
        "id": "corridor-mathura",
        "type": "corridor",
        "name": "Mathura Road Corridor (Delhi Gate ↔ Nizamuddin ↔ Badarpur Border)",
        "crowd_level": "VERY HIGH",
        "avg_speed_kmh": 15.9,
        "routes_count": "34 routes",
        "stops": [
            "Delhi Gate", "Hazrat Nizamuddin", "Ashram", "Apollo Hospital", "Badarpur Border"
        ],
        "waypoints": [
            [28.6360, 77.2430],
            [28.6200, 77.2440],
            [28.5886, 77.2530],
            [28.5700, 77.2550],
            [28.5350, 77.2800],
            [28.4984, 77.3045]
        ]
    },
    # 20 High-Ridership Bus Routes
    {
        "id": "route-717a",
        "type": "route",
        "name": "717A: Badarpur Border ↔ Kapashera Border",
        "crowd_level": "VERY HIGH",
        "avg_speed_kmh": 15.2,
        "stops": [
            "Badarpur Border", "Lal Kuan", "Hamdard Nagar / Sangam Vihar",
            "Khanpur Village", "Saket Metro Station", "Mehrauli Terminal",
            "Mahipal Pur", "Kapashera Border"
        ],
        "waypoints": [
            [28.4984, 77.3045], [28.5030, 77.2880], [28.5126, 77.2485],
            [28.5180, 77.2320], [28.5204, 77.2015], [28.5195, 77.1818],
            [28.5444, 77.1278], [28.5255, 77.0865]
        ]
    },
    {
        "id": "route-511a",
        "type": "route",
        "name": "511A: Badarpur Border ↔ Dhaula Kuan",
        "crowd_level": "VERY HIGH",
        "avg_speed_kmh": 16.8,
        "stops": [
            "Badarpur Border", "Lal Kuan", "Hamdard Nagar / Sangam Vihar",
            "Nehru Place", "AIIMS", "Safdarjung Hospital", "Dhaula Kuan"
        ],
        "waypoints": [
            [28.4984, 77.3045], [28.5030, 77.2880], [28.5126, 77.2485],
            [28.5494, 77.2528], [28.5672, 77.2100], [28.5700, 77.2080],
            [28.5921, 77.1614]
        ]
    },
    {
        "id": "route-546",
        "type": "route",
        "name": "546: Saket Metro Station ↔ Dhaula Kuan",
        "crowd_level": "HIGH",
        "avg_speed_kmh": 19.0,
        "stops": [
            "Saket Metro Station", "IIT Gate", "Munirka Village", "Satya Niketan", "Dhaula Kuan"
        ],
        "waypoints": [
            [28.5204, 77.2015], [28.5440, 77.1930], [28.5580, 77.1720],
            [28.5860, 77.1680], [28.5921, 77.1614]
        ]
    },
    {
        "id": "route-522",
        "type": "route",
        "name": "522: Ambedkar Nagar ↔ Shivaji Stadium",
        "crowd_level": "VERY HIGH",
        "avg_speed_kmh": 14.5,
        "stops": [
            "Ambedkar Nagar Depot", "Andrews Ganj", "AIIMS", "Safdarjung Tomb", "Shivaji Stadium"
        ],
        "waypoints": [
            [28.5262, 77.2346], [28.5684, 77.2248], [28.5672, 77.2100],
            [28.5880, 77.2100], [28.6304, 77.2177]
        ]
    },
    {
        "id": "route-623",
        "type": "route",
        "name": "623: Vasant Kunj ↔ Central Secretariat",
        "crowd_level": "MODERATE",
        "avg_speed_kmh": 20.1,
        "stops": [
            "Vasant Kunj C-9", "Munirka Village", "AIIMS", "Defence Colony", "Central Secretariat"
        ],
        "waypoints": [
            [28.5320, 77.1510], [28.5580, 77.1720], [28.5672, 77.2100],
            [28.5700, 77.2350], [28.6180, 77.2120]
        ]
    },
    {
        "id": "route-729",
        "type": "route",
        "name": "729: Kapashera Border ↔ Mori Gate Terminal",
        "crowd_level": "VERY HIGH",
        "avg_speed_kmh": 15.6,
        "stops": [
            "Kapashera Border", "Mahipal Pur", "Dhaula Kuan", "Karol Bagh", "Mori Gate Terminal"
        ],
        "waypoints": [
            [28.5255, 77.0865], [28.5444, 77.1278], [28.5921, 77.1614],
            [28.6440, 77.1890], [28.6610, 77.2240]
        ]
    },
    {
        "id": "route-534",
        "type": "route",
        "name": "534: Anand Vihar ISBT ↔ Mehrauli Terminal",
        "crowd_level": "VERY HIGH",
        "avg_speed_kmh": 16.2,
        "stops": [
            "Anand Vihar ISBT", "Mayur Vihar Phase 1", "Sarai Kale Khan", "Ashram",
            "Nehru Place", "Chirag Delhi", "Saket Metro Station", "Mehrauli Terminal"
        ],
        "waypoints": [
            [28.6469, 77.3160], [28.6040, 77.2940], [28.5886, 77.2530],
            [28.5700, 77.2550], [28.5494, 77.2528], [28.5470, 77.2250],
            [28.5204, 77.2015], [28.5195, 77.1818]
        ]
    },
    {
        "id": "route-764",
        "type": "route",
        "name": "764: Nehru Place ↔ Najafgarh Terminal",
        "crowd_level": "HIGH",
        "avg_speed_kmh": 18.4,
        "stops": [
            "Nehru Place", "IIT Gate", "Munirka Village", "Dhaula Kuan",
            "Delhi Cantt", "Janakpuri", "Najafgarh Terminal"
        ],
        "waypoints": [
            [28.5494, 77.2528], [28.5440, 77.1930], [28.5580, 77.1720],
            [28.5921, 77.1614], [28.6000, 77.1250], [28.6220, 77.0850],
            [28.6120, 76.9850]
        ]
    },
    {
        "id": "route-578",
        "type": "route",
        "name": "578: Najafgarh Terminal ↔ Safdarjung Terminal",
        "crowd_level": "HIGH",
        "avg_speed_kmh": 17.6,
        "stops": [
            "Najafgarh Terminal", "Uttam Nagar", "Janakpuri", "Dhaula Kuan",
            "AIIMS", "Safdarjung Hospital"
        ],
        "waypoints": [
            [28.6120, 76.9850], [28.6220, 77.0560], [28.6220, 77.0850],
            [28.5921, 77.1614], [28.5672, 77.2100], [28.5700, 77.2080]
        ]
    },
    {
        "id": "route-525stl",
        "type": "route",
        "name": "525STL: Badarpur Border ↔ Mehrauli Terminal",
        "crowd_level": "VERY HIGH",
        "avg_speed_kmh": 15.0,
        "stops": [
            "Badarpur Border", "Lal Kuan", "Hamdard Nagar / Sangam Vihar",
            "Khanpur Village", "Saket Metro Station", "Mehrauli Terminal"
        ],
        "waypoints": [
            [28.4984, 77.3045], [28.5030, 77.2880], [28.5126, 77.2485],
            [28.5180, 77.2320], [28.5204, 77.2015], [28.5195, 77.1818]
        ]
    },
    {
        "id": "route-502",
        "type": "route",
        "name": "502: Mehrauli Terminal ↔ Old Delhi Railway Station",
        "crowd_level": "VERY HIGH",
        "avg_speed_kmh": 14.8,
        "stops": [
            "Mehrauli Terminal", "Adhchini", "IIT Gate", "AIIMS",
            "Safdarjung Tomb", "Shivaji Stadium", "Delhi Gate", "Old Delhi Railway Station"
        ],
        "waypoints": [
            [28.5195, 77.1818], [28.5360, 77.1950], [28.5440, 77.1930],
            [28.5672, 77.2100], [28.5880, 77.2100], [28.6304, 77.2177],
            [28.6360, 77.2430], [28.6570, 77.2280]
        ]
    },
    {
        "id": "route-505",
        "type": "route",
        "name": "505: Mehrauli Terminal ↔ Shivaji Stadium",
        "crowd_level": "HIGH",
        "avg_speed_kmh": 16.5,
        "stops": [
            "Mehrauli Terminal", "Saket Metro Station", "Hauz Khas", "Green Park",
            "AIIMS", "Central Secretariat", "Shivaji Stadium"
        ],
        "waypoints": [
            [28.5195, 77.1818], [28.5204, 77.2015], [28.5435, 77.2060],
            [28.5560, 77.2060], [28.5672, 77.2100], [28.6180, 77.2120],
            [28.6304, 77.2177]
        ]
    },
    {
        "id": "route-419",
        "type": "route",
        "name": "419: Ambedkar Nagar ↔ Old Delhi Railway Station",
        "crowd_level": "VERY HIGH",
        "avg_speed_kmh": 15.3,
        "stops": [
            "Ambedkar Nagar Depot", "Andrews Ganj", "Lajpat Nagar",
            "Nizamuddin Railway Station", "Delhi Gate", "Old Delhi Railway Station"
        ],
        "waypoints": [
            [28.5262, 77.2346], [28.5684, 77.2248], [28.5700, 77.2400],
            [28.5886, 77.2530], [28.6360, 77.2430], [28.6570, 77.2280]
        ]
    },
    {
        "id": "route-427",
        "type": "route",
        "name": "427: Mehrauli Terminal ↔ Hazrat Nizamuddin",
        "crowd_level": "MODERATE",
        "avg_speed_kmh": 17.2,
        "stops": [
            "Mehrauli Terminal", "Saket Metro Station", "Chirag Delhi",
            "Nehru Place", "Ashram", "Nizamuddin Railway Station"
        ],
        "waypoints": [
            [28.5195, 77.1818], [28.5204, 77.2015], [28.5470, 77.2250],
            [28.5494, 77.2528], [28.5700, 77.2550], [28.5886, 77.2530]
        ]
    },
    {
        "id": "route-433",
        "type": "route",
        "name": "433: Badarpur Border ↔ New Delhi Railway Station",
        "crowd_level": "HIGH",
        "avg_speed_kmh": 17.0,
        "stops": [
            "Badarpur Border", "Apollo Hospital", "Ashram", "Nizamuddin Railway Station",
            "Pragati Maidan", "New Delhi Railway Station"
        ],
        "waypoints": [
            [28.4984, 77.3045], [28.5350, 77.2800], [28.5700, 77.2550],
            [28.5886, 77.2530], [28.6200, 77.2440], [28.6420, 77.2210]
        ]
    },
    {
        "id": "route-261",
        "type": "route",
        "name": "261: Sarai Kale Khan ↔ Nand Nagri Terminal",
        "crowd_level": "HIGH",
        "avg_speed_kmh": 18.1,
        "stops": [
            "Sarai Kale Khan", "ITO Ring Road", "Delhi Gate", "Kashmere Gate",
            "Seelampur", "Shahdara", "Nand Nagri"
        ],
        "waypoints": [
            [28.5886, 77.2530], [28.6290, 77.2490], [28.6360, 77.2430],
            [28.6675, 77.2285], [28.6650, 77.2750], [28.6730, 77.2880],
            [28.7050, 77.3050]
        ]
    },
    {
        "id": "route-181",
        "type": "route",
        "name": "181: Hazrat Nizamuddin ↔ Jahangirpuri",
        "crowd_level": "HIGH",
        "avg_speed_kmh": 19.2,
        "stops": [
            "Nizamuddin Railway Station", "ITO Ring Road", "Kashmere Gate",
            "Model Town", "Azadpur Terminal", "Jahangirpuri"
        ],
        "waypoints": [
            [28.5886, 77.2530], [28.6290, 77.2490], [28.6675, 77.2285],
            [28.7180, 77.1750], [28.7070, 77.1790], [28.7300, 77.1650]
        ]
    },
    {
        "id": "route-781",
        "type": "route",
        "name": "781: New Delhi Railway Station ↔ Kapashera Border",
        "crowd_level": "HIGH",
        "avg_speed_kmh": 21.0,
        "stops": [
            "New Delhi Railway Station", "Shivaji Stadium", "Dhaula Kuan",
            "Mahipal Pur", "Kapashera Border"
        ],
        "waypoints": [
            [28.6420, 77.2210], [28.6304, 77.2177], [28.5921, 77.1614],
            [28.5444, 77.1278], [28.5255, 77.0865]
        ]
    },
    {
        "id": "route-894",
        "type": "route",
        "name": "894: Okhla Depot ↔ Karampura Terminal",
        "crowd_level": "HIGH",
        "avg_speed_kmh": 18.5,
        "stops": [
            "Okhla Industrial Area", "Nehru Place", "AIIMS", "Dhaula Kuan",
            "Naraina", "Raja Garden", "Karampura Terminal"
        ],
        "waypoints": [
            [28.5350, 77.2750], [28.5494, 77.2528], [28.5672, 77.2100],
            [28.5921, 77.1614], [28.6250, 77.1350], [28.6500, 77.1250],
            [28.6600, 77.1350]
        ]
    },
    {
        "id": "route-548",
        "type": "route",
        "name": "548: Tuglakabad Extension ↔ Moti Nagar",
        "crowd_level": "MODERATE",
        "avg_speed_kmh": 17.8,
        "stops": [
            "Tuglakabad Extension", "Hamdard Nagar / Sangam Vihar",
            "Chirag Delhi", "AIIMS", "Dhaula Kuan", "Moti Nagar"
        ],
        "waypoints": [
            [28.5080, 77.2600], [28.5126, 77.2485], [28.5470, 77.2250],
            [28.5672, 77.2100], [28.5921, 77.1614], [28.6550, 77.1400]
        ]
    }
]

def downsample_coordinates(coords, max_points=220):
    if len(coords) <= max_points:
        return coords
    step = len(coords) / (max_points - 1)
    res = [coords[0]]
    for i in range(1, max_points - 1):
        idx = int(i * step)
        res.append(coords[idx])
    res.append(coords[-1])
    return res

def fetch_single_route(item):
    cid = item['id']
    wps = item['waypoints']
    locs = ';'.join(f'{pt[1]:.5f},{pt[0]:.5f}' for pt in wps)
    url = f'http://router.project-osrm.org/route/v1/driving/{locs}?overview=full&geometries=geojson'
    
    routed_coords = None
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'DelhiTransitApp/1.0'})
        res = urllib.request.urlopen(req, timeout=10)
        resp_data = json.loads(res.read().decode())
        if resp_data.get('code') == 'Ok':
            raw_pts = resp_data['routes'][0]['geometry']['coordinates']
            lat_lon_pts = [[round(p[1], 5), round(p[0], 5)] for p in raw_pts]
            routed_coords = downsample_coordinates(lat_lon_pts, max_points=220)
            print(f"[{cid}] Snapped: {len(raw_pts)} -> {len(routed_coords)} pts", flush=True)
    except Exception as e:
        print(f"[{cid}] Failed ({e}), using default waypoints", flush=True)

    if not routed_coords:
        routed_coords = wps

    return {
        "id": item["id"],
        "type": item["type"],
        "name": item["name"],
        "crowd_level": item["crowd_level"],
        "avg_speed_kmh": item["avg_speed_kmh"],
        "routes_count": item.get("routes_count", f"{len(item['stops'])} stops"),
        "stops": item["stops"],
        "coordinates": routed_coords
    }

print(f"Routing {len(CORRIDOR_WAYPOINTS)} corridors and bus routes in parallel...", flush=True)
t0 = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    results = list(executor.map(fetch_single_route, CORRIDOR_WAYPOINTS))

print(f"Finished routing in {time.time()-t0:.2f}s", flush=True)

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Saved {len(results)} street-accurate routes to: {OUT_FILE}", flush=True)
