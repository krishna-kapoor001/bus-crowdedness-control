import urllib.request, json
res = urllib.request.urlopen('http://localhost:8000/api/v1/network/geojson')
data = json.loads(res.read().decode())
check_names = ['esi hospital', 'crpf camp', 'shahbad dairy', 'sultan puri', 'd block janakpuri', 'gtk depot', 'wazirpur depot', 'qutub minar']
for f in data['features']:
    fn = f['properties']['name'].lower()
    for cn in check_names:
        if cn in fn:
            print(f"{f['properties']['name']}: {f['geometry']['coordinates']} (Hub: {f['properties']['is_hub']})")
