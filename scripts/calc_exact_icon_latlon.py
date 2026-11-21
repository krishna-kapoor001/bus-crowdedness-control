from PIL import Image
import math

im_tile = Image.open("scripts/tile_18_shahdara.png").convert("RGB")
# The crop was from (150, 140) in im_tile
crop_x0, crop_y0 = 150, 140

im_crop = Image.open("scripts/crop_cluster0.png").convert("RGB")
w, h = im_crop.size

# The blue square of the bus icon: find all pixels of the blue rounded square
# Blue square color: r around 0-10, g around 140-160, b around 210-230
bus_square_px = []
for y in range(h):
    for x in range(w):
        r, g, b = im_crop.getpixel((x, y))
        # strictly the blue background of the bus icon:
        if r < 30 and 130 <= g <= 170 and 200 <= b <= 240:
            bus_square_px.append((x, y))

print(f"Total bus square pixels: {len(bus_square_px)}")
if bus_square_px:
    mean_x = sum(p[0] for p in bus_square_px) / len(bus_square_px)
    mean_y = sum(p[1] for p in bus_square_px) / len(bus_square_px)
    print(f"Mean position inside crop: ({mean_x:.2f}, {mean_y:.2f})")
    
    tile_px = crop_x0 + mean_x
    tile_py = crop_y0 + mean_y
    print(f"Mean position on tile (187350, 109261): ({tile_px:.2f}, {tile_py:.2f})")
    
    n = 2.0 ** 18
    lon = (187350 + tile_px / 256.0) / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * (109261 + tile_py / 256.0) / n)))
    lat = math.degrees(lat_rad)
    
    print(f"\n=======================================================")
    print(f"EXACT LAT/LON OF BLUE BUS ICON: lat={lat:.6f}, lon={lon:.6f}")
    print(f"=======================================================\n")
