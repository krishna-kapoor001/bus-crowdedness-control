import urllib.request
import re

url = 'https://download.bbbike.org/osm/bbbike/NewDelhi/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8')
        links = re.findall(r'href="([^"]+)"', html)
        for l in links:
            if any(ext in l for ext in ['.pbf', '.geojson', '.csv', '.osm.gz']):
                print('Found file:', l)
except Exception as e:
    print('Error:', e)
