from PIL import Image
from icecream import ic
import json

with open("sortie_bounding_rect_met.json", 'r') as f:
    data:dict = json.load(f)
min_x = 100000
max_x = 0
min_y = 100000
max_y = 0

for key, value in data.items():
    for key_x in value.keys():
        if min_x > int(key_x):
            min_x = int(key_x)
        if max_x < int(key_x):
            max_x = int(key_x)
    if min_y > int(key):
        min_y = int(key)
    if max_y < int(key):
        max_y = int(key)

size = (int(max_x - min_x), int(max_y - min_y))
print(size)

pixel = []

for y in range(max_y - min_y):
    yy = str(y + min_y)
    for x in range(max_x - min_x):
        result = False
        if data.__contains__(yy):
            xx = str(x + min_x)
            if data[yy].__contains__(xx):
                result = data[yy][xx]
        pixel.append(result)


im = Image.new("1", size)
# im = Image.new("1", (4, 4))
im.putdata(pixel)
im.save("out_bonding_rec_met.png")