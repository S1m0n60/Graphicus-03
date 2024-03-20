import json 
from PIL import Image
from math import sqrt
from icecream import ic

with open("ouput_test_worker.json", 'r') as f:
    data = json.load(f)
data = [
        85,
        186,
        False
    ]
x = [coord[0] for coord in data]
y = [coord[1] for coord in data]
value = [coord[2] for coord in data]
ic()

img = []
for j in range(0, max(y)):
    for i in range(0, max(x)):
        if [i, j] in data:
            img.append(1)
        else:
            img.append(0)


im = Image.new("1", (max(x), max(y)))
# im = Image.new("1", (4, 4))
im.putdata(img)
im.save("your_file_qthread.png")

print( max(x), max(y))
