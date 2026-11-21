import urllib.request
import json

res = urllib.request.urlopen('http://localhost:8000/api/v1/journey/stops')
stops = json.load(res)
metro_found = [s['name'] for s in stops if 'metro' in s['name'].lower()]
print(f"Total stops matching 'metro': {len(metro_found)}")
if metro_found:
    print("Remaining:", metro_found)
else:
    print("SUCCESS: EXACTLY ZERO stops with 'Metro' in search!")

sample_new = [s['name'] for s in stops if any(k in s['name'] for k in ['Saket Bus Stop', 'Dwarka Mor Bus Stand', 'Karol Bagh Bus Stop', 'Chhatarpur Bus Stop'])]
print("Sample cleaned bus stops in API:", sample_new)
