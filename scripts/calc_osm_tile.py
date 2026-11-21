import math
import urllib.request

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

for z in [16, 17, 18]:
    x, y = deg2num(28.6740, 77.2872, z)
    top_lat, left_lon = num2deg(x, y, z)
    bot_lat, right_lon = num2deg(x + 1, y + 1, z)
    print(f"Zoom {z}: tile ({x}, {y}) covers lat {bot_lat:.6f} to {top_lat:.6f}, lon {left_lon:.6f} to {right_lon:.6f}")

    # Let's download zoom 17 tile
    if z == 17:
        url = f"https://tile.openstreetmap.org/17/{x}/{y}.png"
        req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhiResearch/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                with open(f"scripts/tile_17_{x}_{y}.png", "wb") as f:
                    f.write(resp.read())
                print(f"Downloaded tile 17/{x}/{y}.png")
        except Exception as e:
            print("Download tile error:", e)
