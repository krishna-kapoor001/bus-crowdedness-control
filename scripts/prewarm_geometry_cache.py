import json, os, urllib.request, time

def main():
    stops_file = 'data/stops_meta.json'
    corridors_file = 'data/processed/corridors_routed.json'
    cache_file = 'data/processed/osrm_geometry_cache.json'
    
    stops_raw = json.load(open(stops_file, encoding='utf-8'))
    stops_meta = {s['name']: s for s in stops_raw}
    
    # Existing cache
    cache = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            print(f"Loaded existing cache with {len(cache)} entries.")
        except Exception:
            pass

    # 1. Pre-warm from existing 28 corridors
    if os.path.exists(corridors_file):
        corridors = json.load(open(corridors_file, encoding='utf-8'))
        for c in corridors:
            pts = c.get('coordinates', [])
            c_stops = c.get('stops', [])
            if pts and len(pts) >= 10 and len(c_stops) >= 2:
                # Key pairs along corridor
                s_start = c_stops[0]
                s_end = c_stops[-1]
                k1 = f"{s_start}__{s_end}"
                k2 = f"{s_end}__{s_start}"
                if k1 not in cache:
                    cache[k1] = pts
                if k2 not in cache:
                    cache[k2] = list(reversed(pts))
        print(f"Cache now has {len(cache)} entries after corridor harvest.")

    # 2. Key commuter pairs to pre-route via OSRM
    key_pairs = [
        ('Vasant Kunj sec B1', 'Dhaula Kuan'),
        ('Mahipal Pur Village', 'Dhaula Kuan'),
        ('Mahipal Pur Village', 'South Moti Bagh'),
        ('Vasant Kunj sec B1', 'South Moti Bagh'),
        ('ISBT Kashmere Gate', 'AIIMS Transit Hub'),
        ('ISBT Kashmere Gate', 'Dhaula Kuan'),
        ('ISBT Kashmere Gate', 'Anand Vihar ISBT'),
        ('Anand Vihar ISBT', 'ISBT Sarai Kale Khan'),
        ('Anand Vihar ISBT', 'Scindia House'),
        ('Scindia House', 'Dhaula Kuan'),
        ('Scindia House', 'Nehru Place Terminal'),
        ('Saket', 'Dhaula Kuan'),
        ('Saket', 'ISBT Kashmere Gate'),
        ('Saket', 'Nehru Place Terminal'),
        ('Mehrauli Terminal', 'Badarpur Border Terminal'),
        ('Najafgarh Terminal', 'Tilak Nagar Terminal'),
        ('Najafgarh Terminal', 'Dhaula Kuan'),
        ('Uttam Nagar Terminal', 'ISBT Kashmere Gate'),
        ('Karol Bagh Terminal', 'Anand Vihar ISBT'),
        ('Azadpur Terminal', 'ISBT Kashmere Gate'),
        ('Rohini Sector 22 Terminal', 'Azadpur Terminal'),
        ('Punjabi Bagh Terminal', 'Dhaula Kuan'),
        ('Dwarka Mor Bus Stand', 'Dhaula Kuan'),
        ('Badarpur Border Terminal', 'ISBT Sarai Kale Khan'),
        ('Nehru Place Terminal', 'ISBT Kashmere Gate')
    ]

    for o_name, d_name in key_pairs:
        k = f"{o_name}__{d_name}"
        kr = f"{d_name}__{o_name}"
        if k in cache and kr in cache:
            continue
        if o_name not in stops_meta or d_name not in stops_meta:
            continue
        o = stops_meta[o_name]
        d = stops_meta[d_name]
        o_lat, o_lon = o['latitude'], o['longitude']
        d_lat, d_lon = d['latitude'], d['longitude']
        
        try:
            url = f"http://router.project-osrm.org/route/v1/driving/{o_lon:.5f},{o_lat:.5f};{d_lon:.5f},{d_lat:.5f}?overview=full&geometries=geojson"
            req = urllib.request.Request(url, headers={'User-Agent': 'DelhiTransportPlanner/1.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
            if data.get('code') == 'Ok':
                coords = [[round(p[1], 6), round(p[0], 6)] for p in data['routes'][0]['geometry']['coordinates']]
                cache[k] = coords
                cache[kr] = list(reversed(coords))
                print(f"✓ Cached: {o_name} ↔ {d_name} ({len(coords)} street points, {data['routes'][0]['distance']/1000:.1f} km)")
                time.sleep(0.1)
        except Exception as e:
            print(f"✗ Failed {o_name} -> {d_name}: {e}")

    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)
    print(f"\nFinal saved persistent geometry cache: {len(cache)} routes in {cache_file}")

if __name__ == '__main__':
    main()
