import sys, os
sys.path.insert(0, ".")
sys.path.insert(0, "backend")

from backend.app.services.journey_service import journey_service

def analyze_stops(stops):
    coords = []
    for s in stops:
        meta = journey_service.stops_meta.get(s, {})
        coords.append((s, meta.get('latitude', 0), meta.get('longitude', 0)))
    
    cum = 0.0
    print(f"{'Stop':<25} | {'Hop (km)':<10} | {'Cum (km)':<10}")
    print("-" * 50)
    for i in range(len(coords)):
        name, lat, lon = coords[i]
        if i == 0:
            hop = 0.0
        else:
            p_name, p_lat, p_lon = coords[i-1]
            # Delhi urban detour factor ~1.30 on straight distance between stops
            hop = journey_service._haversine(p_lat, p_lon, lat, lon) * 1.30
            cum += hop
        print(f"{name:<25} | {hop:<10.2f} | {cum:<10.2f}")

print("=== SAKET -> DHAULA KUAN (EXPRESS) ===")
analyze_stops(['Saket', 'Mehrauli Terminal', 'Munirka Village', 'Sarojini Nagar Depot', 'Dhaula Kuan'])

print("\n=== ANAND VIHAR -> SHIVAJI STADIUM ===")
reg, exp = journey_service._resolve_corridor_stops("Anand Vihar ISBT", "Shivaji Stadium", 13.0)
analyze_stops([s[0] for s in exp])
