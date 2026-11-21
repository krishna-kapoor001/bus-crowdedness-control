import os
import json
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from backend.app.config import settings

router = APIRouter()

# Pre-warmed in-memory GeoJSON and Corridors for high-concurrency zero-DB serving
CACHED_GEOJSON = None
CACHED_CORRIDORS = None

def _load_cached_geojson():
    global CACHED_GEOJSON
    stops_file = os.path.join(settings.PROCESSED_DATA_DIR, 'stop_profiles.json')
    if not os.path.exists(stops_file):
        stops_file = os.path.join(settings.DATA_DIR, 'stops_meta.json')

    features = []
    if os.path.exists(stops_file):
        with open(stops_file, 'r', encoding='utf-8') as f:
            stops = json.load(f)
            for idx, s in enumerate(stops):
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [s.get('longitude', 77.2090), s.get('latitude', 28.6139)]
                    },
                    "properties": {
                        "id": idx + 1,
                        "name": s.get('name'),
                        "corridor": s.get('corridor', 'Delhi Transit Corridor'),
                        "boardings": s.get('monthly_boardings', 500),
                        "is_hub": s.get('is_major_hub', False)
                    }
                })
    CACHED_GEOJSON = {
        "type": "FeatureCollection",
        "features": features
    }

def _load_cached_corridors():
    global CACHED_CORRIDORS
    routed_file = os.path.join(settings.PROCESSED_DATA_DIR, 'corridors_routed.json')
    if not os.path.exists(routed_file):
        routed_file = os.path.join(settings.DATA_DIR, 'corridors_routed.json')
    if os.path.exists(routed_file):
        with open(routed_file, 'r', encoding='utf-8') as f:
            CACHED_CORRIDORS = json.load(f)
            return

    # 1. Curated Major Arterial Transit Corridors (Sequential & Symmetrical Coordinates)
    corridors_list = [
        {
            "id": "corridor-ring",
            "type": "corridor",
            "name": "Ring Road Arterial (Kashmere Gate ↔ AIIMS ↔ Sarai Kale Khan)",
            "crowd_level": "VERY HIGH",
            "avg_speed_kmh": 16.4,
            "routes_count": "48 routes",
            "coordinates": [
                [28.6675, 77.2285],
                [28.6304, 77.2177],
                [28.5672, 77.2100],
                [28.5700, 77.2400],
                [28.5886, 77.2530],
                [28.6290, 77.2490],
                [28.6675, 77.2285]
            ],
            "stops": [
                "Kashmere Gate", "ISBT Kashmiri Gate", "Shivaji Stadium",
                "AIIMS", "Safdarjung Hospital", "Lajpat Nagar",
                "Sarai Kale Khan", "ITO Ring Road"
            ]
        },
        {
            "id": "corridor-mb",
            "type": "corridor",
            "name": "Mehrauli-Badarpur Corridor (Mehrauli ↔ Saket ↔ Badarpur Border)",
            "crowd_level": "VERY HIGH",
            "avg_speed_kmh": 14.8,
            "routes_count": "32 routes",
            "coordinates": [
                [28.5195, 77.1818],
                [28.5204, 77.2015],
                [28.5180, 77.2320],
                [28.5126, 77.2485],
                [28.5030, 77.2880],
                [28.4984, 77.3045]
            ],
            "stops": [
                "Mehrauli", "Said Ul Zeb Village", "Saket Bus Stop",
                "Khanpur Village", "Hamdard Nagar / Sangam Vihar", "Lal Kuan", "Badarpur Border"
            ]
        },
        {
            "id": "corridor-outer-ring",
            "type": "corridor",
            "name": "Outer Ring Road Arterial (Munirka ↔ IIT Gate ↔ Nehru Place ↔ Okhla)",
            "crowd_level": "VERY HIGH",
            "avg_speed_kmh": 18.2,
            "routes_count": "35 routes",
            "coordinates": [
                [28.5580, 77.1720],
                [28.5440, 77.2060],
                [28.5435, 77.2150],
                [28.5470, 77.2250],
                [28.5494, 77.2528],
                [28.5350, 77.2750]
            ],
            "stops": [
                "Munirka Village", "IIT Gate", "Hauz Khas", "Chirag Delhi", "Nehru Place", "Okhla"
            ]
        },
        {
            "id": "corridor-airport",
            "type": "corridor",
            "name": "Airport Expressway Corridor (Dhaula Kuan ↔ Mahipalpur ↔ Kapashera)",
            "crowd_level": "HIGH",
            "avg_speed_kmh": 22.1,
            "routes_count": "26 routes",
            "coordinates": [
                [28.60005, 77.162017],
                [28.587833, 77.170333],
                [28.546733, 77.125000],
                [28.546800, 77.123700],
                [28.545867, 77.126733],
                [28.535800, 77.112200],
                [28.514000, 77.095000],
                [28.521700, 77.082117]
            ],
            "stops": [
                "Dhaula Kuan", "Satya Niketan", "Mahipal Pur Crossing", "Mahipal Pur", "Mahipal Pur Village", "Shiv Murti", "Kapashera Border"
            ]
        },
        {
            "id": "corridor-transyamuna",
            "type": "corridor",
            "name": "Trans-Yamuna East Corridor (Shahdara ↔ Anand Vihar ISBT ↔ Mayur Vihar)",
            "crowd_level": "HIGH",
            "avg_speed_kmh": 18.5,
            "routes_count": "38 routes",
            "coordinates": [
                [28.6730, 77.2880],
                [28.6650, 77.2750],
                [28.6469, 77.3160],
                [28.6290, 77.2910],
                [28.6040, 77.2940]
            ],
            "stops": [
                "Shahdara", "Seelampur", "Anand Vihar ISBT", "Mother Dairy", "Mayur Vihar Phase 1", "Mayur Vihar Phase 3"
            ]
        },
        {
            "id": "corridor-gtk",
            "type": "corridor",
            "name": "GT Karnal Highway Corridor (Azadpur ↔ Jahangirpuri ↔ Singhu Border)",
            "crowd_level": "HIGH",
            "avg_speed_kmh": 20.4,
            "routes_count": "22 routes",
            "coordinates": [
                [28.7070, 77.1790],
                [28.7180, 77.1750],
                [28.7300, 77.1650],
                [28.7520, 77.1550],
                [28.7950, 77.1350],
                [28.8250, 77.1200]
            ],
            "stops": [
                "Azadpur", "Model Town", "Jahangirpuri", "Mukarba Chowk", "Alipur", "Singhu Border"
            ]
        },
        {
            "id": "corridor-aurobindo",
            "type": "corridor",
            "name": "Aurobindo Marg Corridor (Safdarjung Tomb ↔ AIIMS ↔ Mehrauli)",
            "crowd_level": "HIGH",
            "avg_speed_kmh": 17.1,
            "routes_count": "29 routes",
            "coordinates": [
                [28.5880, 77.2100],
                [28.5672, 77.2100],
                [28.5560, 77.2060],
                [28.5440, 77.2060],
                [28.5240, 77.1950],
                [28.5195, 77.1818]
            ],
            "stops": [
                "Safdarjung Tomb", "AIIMS", "Green Park", "IIT Gate", "Qutub Minar", "Mehrauli"
            ]
        },
        {
            "id": "corridor-mathura",
            "type": "corridor",
            "name": "Mathura Road Corridor (Delhi Gate ↔ Nizamuddin ↔ Badarpur Border)",
            "crowd_level": "VERY HIGH",
            "avg_speed_kmh": 15.9,
            "routes_count": "34 routes",
            "coordinates": [
                [28.6360, 77.2430],
                [28.5886, 77.2530],
                [28.5700, 77.2550],
                [28.5350, 77.2800],
                [28.4984, 77.3045]
            ],
            "stops": [
                "Delhi Gate", "Hazrat Nizamuddin", "Ashram", "Apollo Hospital", "Badarpur Border"
            ]
        }
    ]

    # 2. Curated High-Ridership Delhi Trunk Bus Routes (Sequential, Symmetrical Geometries)
    routes_list = [
        {
            "id": "route-717a",
            "type": "route",
            "name": "717A: Badarpur Border ↔ Kapashera Border",
            "crowd_level": "VERY HIGH",
            "avg_speed_kmh": 15.2,
            "routes_count": "8 stops",
            "stops": [
                "Badarpur Border", "Lal Kuan", "Hamdard Nagar / Sangam Vihar",
                "Khanpur Village", "Saket Bus Stop", "Mehrauli",
                "Mahipal Pur", "Kapashera Border"
            ],
            "coordinates": [
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
            "routes_count": "7 stops",
            "stops": [
                "Badarpur Border", "Lal Kuan", "Hamdard Nagar / Sangam Vihar",
                "Nehru Place", "AIIMS", "Safdarjung Hospital", "Dhaula Kuan"
            ],
            "coordinates": [
                [28.4984, 77.3045], [28.5030, 77.2880], [28.5126, 77.2485],
                [28.5494, 77.2528], [28.5672, 77.2100], [28.5700, 77.2080],
                [28.5921, 77.1614]
            ]
        },
        {
            "id": "route-546",
            "type": "route",
            "name": "546: Saket Bus Stop ↔ Dhaula Kuan",
            "crowd_level": "HIGH",
            "avg_speed_kmh": 19.0,
            "routes_count": "5 stops",
            "stops": [
                "Saket Bus Stop", "IIT Gate", "Munirka Village", "Satya Niketan", "Dhaula Kuan"
            ],
            "coordinates": [
                [28.5204, 77.2015], [28.5440, 77.2060], [28.5580, 77.1720],
                [28.5860, 77.1680], [28.5921, 77.1614]
            ]
        },
        {
            "id": "route-522",
            "type": "route",
            "name": "522: Ambedkar Nagar ↔ Shivaji Stadium",
            "crowd_level": "HIGH",
            "avg_speed_kmh": 17.5,
            "routes_count": "5 stops",
            "stops": [
                "Ambedkar Nagar Depot", "Andrews Ganj", "AIIMS", "Safdarjung Tomb", "Shivaji Stadium"
            ],
            "coordinates": [
                [28.5262, 77.2346], [28.5684, 77.2248], [28.5672, 77.2100],
                [28.5880, 77.2100], [28.6304, 77.2177]
            ]
        },
        {
            "id": "route-623",
            "type": "route",
            "name": "623: Vasant Kunj ↔ Central Secretariat",
            "crowd_level": "MODERATE",
            "avg_speed_kmh": 18.2,
            "routes_count": "5 stops",
            "stops": [
                "Vasant Kunj C-9", "Munirka Village", "AIIMS", "Defence Colony", "Central Secretariat"
            ],
            "coordinates": [
                [28.5320, 77.1510], [28.5580, 77.1720], [28.5672, 77.2100],
                [28.5700, 77.2350], [28.6180, 77.2120]
            ]
        },
        {
            "id": "route-729",
            "type": "route",
            "name": "729: Kapashera Border ↔ Mori Gate",
            "crowd_level": "VERY HIGH",
            "avg_speed_kmh": 16.5,
            "routes_count": "5 stops",
            "stops": [
                "Kapashera Border", "Mahipal Pur", "Dhaula Kuan", "Karol Bagh", "Mori Gate"
            ],
            "coordinates": [
                [28.5255, 77.0865], [28.5444, 77.1278], [28.5921, 77.1614],
                [28.6510, 77.1900], [28.6610, 77.2240]
            ]
        },
        {
            "id": "route-534",
            "type": "route",
            "name": "534: Anand Vihar ISBT ↔ Mehrauli",
            "crowd_level": "VERY HIGH",
            "avg_speed_kmh": 15.6,
            "routes_count": "8 stops",
            "stops": [
                "Anand Vihar ISBT", "Mayur Vihar Phase 1", "Sarai Kale Khan", "Ashram",
                "Nehru Place", "Chirag Delhi", "Saket Bus Stop", "Mehrauli"
            ],
            "coordinates": [
                [28.6469, 77.3160], [28.6040, 77.2940], [28.5886, 77.2530],
                [28.5700, 77.2550], [28.5494, 77.2528], [28.5470, 77.2250],
                [28.5204, 77.2015], [28.5195, 77.1818]
            ]
        },
        {
            "id": "route-764",
            "type": "route",
            "name": "764: Nehru Place ↔ Najafgarh",
            "crowd_level": "VERY HIGH",
            "avg_speed_kmh": 17.8,
            "routes_count": "7 stops",
            "stops": [
                "Nehru Place", "IIT Gate", "Munirka Village", "Dhaula Kuan",
                "Delhi Cantt", "Janakpuri", "Najafgarh"
            ],
            "coordinates": [
                [28.5494, 77.2528], [28.5440, 77.2060], [28.5580, 77.1720],
                [28.5921, 77.1614], [28.6000, 77.1250], [28.6220, 77.0850],
                [28.6120, 76.9850]
            ]
        },
        {
            "id": "route-578",
            "type": "route",
            "name": "578: Najafgarh ↔ Safdarjung",
            "crowd_level": "HIGH",
            "avg_speed_kmh": 18.0,
            "routes_count": "6 stops",
            "stops": [
                "Najafgarh", "Uttam Nagar", "Janakpuri", "Dhaula Kuan",
                "AIIMS", "Safdarjung Hospital"
            ],
            "coordinates": [
                [28.6120, 76.9850], [28.6220, 77.0560], [28.6220, 77.0850],
                [28.5921, 77.1614], [28.5672, 77.2100], [28.5700, 77.2080]
            ]
        },
        {
            "id": "route-525stl",
            "type": "route",
            "name": "525STL: Badarpur Border ↔ Mehrauli",
            "crowd_level": "VERY HIGH",
            "avg_speed_kmh": 14.9,
            "routes_count": "6 stops",
            "stops": [
                "Badarpur Border", "Lal Kuan", "Hamdard Nagar / Sangam Vihar",
                "Khanpur Village", "Saket Bus Stop", "Mehrauli"
            ],
            "coordinates": [
                [28.4984, 77.3045], [28.5030, 77.2880], [28.5126, 77.2485],
                [28.5180, 77.2320], [28.5204, 77.2015], [28.5195, 77.1818]
            ]
        },
        {
            "id": "route-502",
            "type": "route",
            "name": "502: Mehrauli ↔ Old Delhi Railway Station",
            "crowd_level": "HIGH",
            "avg_speed_kmh": 16.2,
            "routes_count": "8 stops",
            "stops": [
                "Mehrauli", "Adhchini", "IIT Gate", "AIIMS",
                "Safdarjung Tomb", "Shivaji Stadium", "Delhi Gate", "Old Delhi Railway Station"
            ],
            "coordinates": [
                [28.5195, 77.1818], [28.5350, 77.1950], [28.5440, 77.2060],
                [28.5672, 77.2100], [28.5880, 77.2100], [28.6304, 77.2177],
                [28.6360, 77.2430], [28.6570, 77.2280]
            ]
        },
        {
            "id": "route-505",
            "type": "route",
            "name": "505: Mehrauli ↔ Shivaji Stadium",
            "crowd_level": "HIGH",
            "avg_speed_kmh": 17.0,
            "routes_count": "7 stops",
            "stops": [
                "Mehrauli", "Saket Bus Stop", "Hauz Khas", "Green Park",
                "AIIMS", "Central Secretariat", "Shivaji Stadium"
            ],
            "coordinates": [
                [28.5195, 77.1818], [28.5204, 77.2015], [28.5435, 77.2150],
                [28.5560, 77.2060], [28.5672, 77.2100], [28.6180, 77.2120],
                [28.6304, 77.2177]
            ]
        },
        {
            "id": "route-419",
            "type": "route",
            "name": "419: Ambedkar Nagar ↔ Old Delhi Railway Station",
            "crowd_level": "HIGH",
            "avg_speed_kmh": 16.5,
            "routes_count": "6 stops",
            "stops": [
                "Ambedkar Nagar Depot", "Andrews Ganj", "Lajpat Nagar",
                "Nizamuddin Railway Station", "Delhi Gate", "Old Delhi Railway Station"
            ],
            "coordinates": [
                [28.5262, 77.2346], [28.5684, 77.2248], [28.5700, 77.2400],
                [28.5886, 77.2530], [28.6360, 77.2430], [28.6570, 77.2280]
            ]
        },
        {
            "id": "route-427",
            "type": "route",
            "name": "427: Mehrauli ↔ Hazrat Nizamuddin",
            "crowd_level": "MODERATE",
            "avg_speed_kmh": 17.4,
            "routes_count": "6 stops",
            "stops": [
                "Mehrauli", "Saket Bus Stop", "Chirag Delhi",
                "Nehru Place", "Ashram", "Nizamuddin Railway Station"
            ],
            "coordinates": [
                [28.5195, 77.1818], [28.5204, 77.2015], [28.5470, 77.2250],
                [28.5494, 77.2528], [28.5700, 77.2550], [28.5886, 77.2530]
            ]
        },
        {
            "id": "route-433",
            "type": "route",
            "name": "433: Badarpur Border ↔ New Delhi Railway Station",
            "crowd_level": "VERY HIGH",
            "avg_speed_kmh": 15.8,
            "routes_count": "6 stops",
            "stops": [
                "Badarpur Border", "Apollo Hospital", "Ashram",
                "Nizamuddin Railway Station", "Pragati Maidan", "New Delhi Railway Station"
            ],
            "coordinates": [
                [28.4984, 77.3045], [28.5350, 77.2800], [28.5700, 77.2550],
                [28.5886, 77.2530], [28.6250, 77.2420], [28.6420, 77.2210]
            ]
        },
        {
            "id": "route-261",
            "type": "route",
            "name": "261: Sarai Kale Khan ↔ Nand Nagri",
            "crowd_level": "HIGH",
            "avg_speed_kmh": 18.1,
            "routes_count": "7 stops",
            "stops": [
                "Sarai Kale Khan", "ITO Ring Road", "Delhi Gate", "Kashmere Gate",
                "Seelampur", "Shahdara", "Nand Nagri"
            ],
            "coordinates": [
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
            "routes_count": "6 stops",
            "stops": [
                "Nizamuddin Railway Station", "ITO Ring Road", "Kashmere Gate",
                "Model Town", "Azadpur", "Jahangirpuri"
            ],
            "coordinates": [
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
            "routes_count": "5 stops",
            "stops": [
                "New Delhi Railway Station", "Shivaji Stadium", "Dhaula Kuan",
                "Mahipal Pur", "Kapashera Border"
            ],
            "coordinates": [
                [28.6420, 77.2210], [28.6304, 77.2177], [28.5921, 77.1614],
                [28.5444, 77.1278], [28.5255, 77.0865]
            ]
        },
        {
            "id": "route-894",
            "type": "route",
            "name": "894: Okhla Depot ↔ Karampura",
            "crowd_level": "HIGH",
            "avg_speed_kmh": 18.5,
            "routes_count": "7 stops",
            "stops": [
                "Okhla Industrial Area", "Nehru Place", "AIIMS", "Dhaula Kuan",
                "Naraina", "Raja Garden", "Karampura"
            ],
            "coordinates": [
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
            "routes_count": "6 stops",
            "stops": [
                "Tuglakabad Extension", "Hamdard Nagar / Sangam Vihar",
                "Chirag Delhi", "AIIMS", "Dhaula Kuan", "Moti Nagar"
            ],
            "coordinates": [
                [28.5080, 77.2600], [28.5126, 77.2485], [28.5470, 77.2250],
                [28.5672, 77.2100], [28.5921, 77.1614], [28.6550, 77.1400]
            ]
        }
    ]

    CACHED_CORRIDORS = corridors_list + routes_list

_load_cached_geojson()
_load_cached_corridors()

@router.get("/geojson")
def get_network_geojson():
    global CACHED_GEOJSON
    if CACHED_GEOJSON is None:
        _load_cached_geojson()
    return JSONResponse(
        content=CACHED_GEOJSON,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Cache-Status": "IN-MEMORY-HIT"
        }
    )

@router.get("/corridors")
def get_corridor_layers():
    global CACHED_CORRIDORS
    if CACHED_CORRIDORS is None:
        _load_cached_corridors()
    return JSONResponse(
        content=CACHED_CORRIDORS,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Cache-Status": "IN-MEMORY-HIT"
        }
    )
