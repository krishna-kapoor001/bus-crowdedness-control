import math

# Coordinate of Shahdara in data:
s_lat = 28.674025
s_lon = 77.287222

# Coordinate of tree row (Way 691454897):
# node 6481094572 on Bhola Nath Nagar Marg: lat=28.6710011, lon=77.2887046
# tree row: lat=28.672771, lon=77.288036
t_lat = 28.672771
t_lon = 77.288036

# Red line way 1219840287:
r_lat = 28.673152
r_lon = 77.287489

print(f"Shahdara in data ({s_lat}, {s_lon}) vs Red line ({r_lat}, {r_lon}):")
print(f"Lat diff: {s_lat - r_lat} (Shahdara is NORTH of red line by {(s_lat - r_lat)*111000:.1f} meters)")

print(f"Shahdara in data ({s_lat}, {s_lon}) vs Tree row ({t_lat}, {t_lon}):")
print(f"Lat diff: {s_lat - t_lat} (Shahdara is NORTH of tree row by {(s_lat - t_lat)*111000:.1f} meters)")
