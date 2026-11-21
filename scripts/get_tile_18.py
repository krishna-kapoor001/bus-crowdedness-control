import urllib.request
from PIL import Image

url = "https://tile.openstreetmap.org/18/187350/109261.png"
req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhiResearch/1.0'})
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        with open("scripts/tile_18_shahdara.png", "wb") as f:
            f.write(resp.read())
        print("Downloaded tile_18_shahdara.png")
except Exception as e:
    print("Download error:", e)
