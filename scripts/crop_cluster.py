from PIL import Image

im = Image.open("scripts/tile_18_shahdara.png")
# Crop around x=214, y=202 (box [150, 140, 256, 256])
crop1 = im.crop((150, 140, 256, 256))
crop1.save("scripts/crop_cluster0.png")
print("Saved crop_cluster0.png")
