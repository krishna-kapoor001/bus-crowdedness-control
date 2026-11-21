import urllib.request
import os

url = 'https://raw.githubusercontent.com/anandthegreat/OTD-GTFS-Routes/master/stops.txt'
dest = 'data/gtfs_delhi_stops.txt'

print("Downloading Delhi GTFS stops...")
try:
    urllib.request.urlretrieve(url, dest)
    size = os.path.getsize(dest)
    print(f"Downloaded successfully! File size: {size:,} bytes")
    with open(dest, 'r', encoding='utf-8') as f:
        for i in range(10):
            print(f.readline().strip())
except Exception as e:
    print("Download failed:", e)
