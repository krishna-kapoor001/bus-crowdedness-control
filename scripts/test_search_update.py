import urllib.request
import urllib.parse
import json

print("=" * 80)
print("  TESTING UPDATED JOURNEY PLANNER SEARCH")
print("=" * 80)

# 1. Test all stops
with urllib.request.urlopen('http://localhost:8000/api/v1/journey/stops') as r:
    all_stops = json.loads(r.read().decode())
    hubs = [s for s in all_stops if s.get('is_major_hub')]
    print(f"Total stops in search catalog: {len(all_stops)}")
    print(f"Total Major Bus Stands:         {len(hubs)}")
    assert len(all_stops) == 757, f"Expected 757 stops, got {len(all_stops)}"
    assert len(hubs) == 38, f"Expected 38 hubs, got {len(hubs)}"

# 2. Test query='bus stand'
with urllib.request.urlopen('http://localhost:8000/api/v1/journey/stops?query=bus+stand') as r:
    bus_stands = json.loads(r.read().decode())
    print(f"\nQuery 'bus stand' returned: {len(bus_stands)} results")
    print(f"Sample 5 bus stands: {[s['name'] for s in bus_stands[:5]]}")
    assert len(bus_stands) == 38, f"Expected 38 bus stands, got {len(bus_stands)}"

# 3. Test query='terminal'
with urllib.request.urlopen('http://localhost:8000/api/v1/journey/stops?query=terminal') as r:
    terminals = json.loads(r.read().decode())
    print(f"\nQuery 'terminal' returned: {len(terminals)} results")

# 4. Test specific stops
for test_q in ['saket', 'dhaula', 'kashmere', 'anand vihar', 'najafgarh', 'wazirpur', 'shivaji stadium']:
    url = f'http://localhost:8000/api/v1/journey/stops?query={urllib.parse.quote(test_q)}'
    with urllib.request.urlopen(url) as r:
        matches = json.loads(r.read().decode())
        print(f"Query '{test_q}': {len(matches)} match(es) -> {[s['name'] for s in matches[:3]]}")
        assert len(matches) > 0, f"No matches for '{test_q}'"

print("\n✓ ALL SEARCH QUERIES VERIFIED AND WORKING PERFECTLY!")
