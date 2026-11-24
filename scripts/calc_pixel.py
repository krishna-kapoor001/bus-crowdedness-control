import math

# Slippy map tilename calculation
def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
  return (xtile, ytile)

# Pixel inside tile (256x256)
def deg2pixel(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  x = ((lon_deg + 180.0) / 360.0 * n) * 256
  y = ((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n) * 256
  return (x, y)

zoom = 18
p_a = deg2pixel(28.6792029, 77.2081931, zoom)
p_b = deg2pixel(28.6790992, 77.2083695, zoom)
print("Zoom 18:")
print("Node A (28.6792029, 77.2081931):", p_a)
print("Node B (28.6790992, 77.2083695):", p_b)
print("Delta in pixels: dx =", p_b[0] - p_a[0], ", dy =", p_b[1] - p_a[1])
