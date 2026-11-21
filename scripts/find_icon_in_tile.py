from PIL import Image
import math

im = Image.open("scripts/tile_17_93675_54630.png").convert("RGB")
print("Image size:", im.size, im.mode)

blue_pixels = []
for y in range(im.size[1]):
    for x in range(im.size[0]):
        r, g, b = im.getpixel((x, y))
        # Blue icon color in OSM standard:
        if r < 80 and 80 <= g <= 200 and b > 160:
            blue_pixels.append((x, y, (r, g, b)))

print(f"Total blue icon-like pixels in tile 17/93675/54630: {len(blue_pixels)}")
if blue_pixels:
    xs = [p[0] for p in blue_pixels]
    ys = [p[1] for p in blue_pixels]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    center_x = sum(xs)/len(xs)
    center_y = sum(ys)/len(ys)
    print(f"Blue pixels bounding box: x in [{min_x}, {max_x}], y in [{min_y}, {max_y}]")
    print(f"Center pixel: ({center_x:.1f}, {center_y:.1f})")
    
    def pixel_to_latlon(tile_x, tile_y, px, py, zoom=17):
        n = 2.0 ** zoom
        lon_deg = (tile_x + px / 256.0) / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * (tile_y + py / 256.0) / n)))
        return math.degrees(lat_rad), lon_deg
    
    icon_lat, icon_lon = pixel_to_latlon(93675, 54630, center_x, center_y, 17)
    print(f"*** EXACT LAT/LON OF BLUE BUS ICON ON OSM TILE ***: lat={icon_lat:.6f}, lon={icon_lon:.6f}")
else:
    # Print distinct colors in the tile
    colors = set(im.getpixel((x, y)) for y in range(im.size[1]) for x in range(im.size[0]))
    print(f"Found {len(colors)} distinct RGB colors.")
    blues = [c for c in colors if c[2] > c[0] + 40 and c[2] > c[1]]
    print(f"Blue shades count: {len(blues)}, examples: {blues[:10]}")
