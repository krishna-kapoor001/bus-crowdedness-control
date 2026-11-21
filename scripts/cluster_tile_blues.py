from PIL import Image
import math

im = Image.open("scripts/tile_17_93675_54630.png").convert("RGB")

# Cluster blue pixels
pixels = []
for y in range(im.size[1]):
    for x in range(im.size[0]):
        r, g, b = im.getpixel((x, y))
        if r < 80 and 80 <= g <= 200 and b > 160:
            pixels.append((x, y))

# Let's find connected components or simple density clusters
clusters = []
for p in pixels:
    placed = False
    for c in clusters:
        # if distance < 15 px
        if math.hypot(p[0]-c['x_mean'], p[1]-c['y_mean']) < 25:
            c['pts'].append(p)
            c['x_mean'] = sum(pt[0] for pt in c['pts'])/len(c['pts'])
            c['y_mean'] = sum(pt[1] for pt in c['pts'])/len(c['pts'])
            placed = True
            break
    if not placed:
        clusters.append({'pts': [p], 'x_mean': p[0], 'y_mean': p[1]})

print(f"Clusters found: {len(clusters)}")
for idx, c in enumerate(clusters):
    if len(c['pts']) > 15:
        # Convert to lat lon
        n = 2.0 ** 17
        lon = (93675 + c['x_mean'] / 256.0) / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * (54630 + c['y_mean'] / 256.0) / n)))
        lat = math.degrees(lat_rad)
        print(f"Cluster {idx} ({len(c['pts'])} pts) at px=({c['x_mean']:.1f}, {c['y_mean']:.1f}) -> lat={lat:.6f}, lon={lon:.6f}")
