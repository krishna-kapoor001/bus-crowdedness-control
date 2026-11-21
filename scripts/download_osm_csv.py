import urllib.request
import lzma
import os
import csv

url = "https://download.bbbike.org/osm/bbbike/NewDelhi/NewDelhi.osm.csv.xz"
dest_xz = os.path.join("data", "NewDelhi.osm.csv.xz")
dest_csv = os.path.join("data", "NewDelhi.osm.csv")

print(f"Downloading {url} ...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30) as r:
    data_xz = r.read()

print(f"Downloaded {len(data_xz) / (1024*1024):.2f} MB. Decompressing with lzma...")
csv_content = lzma.decompress(data_xz)

with open(dest_csv, "wb") as f:
    f.write(csv_content)

print(f"Extracted {len(csv_content) / (1024*1024):.2f} MB to {dest_csv}!")

# Inspect first 10 lines
with open(dest_csv, "r", encoding="utf-8", errors="ignore") as f:
    for i in range(15):
        print(f.readline().strip())
