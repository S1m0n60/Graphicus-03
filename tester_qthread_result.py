import json 
from PIL import Image
from pprint import pprint

with open("ouput_test_worker.json", 'r') as f:
    data = json.load(f)

x = [coord[0] for coord in data]
y = [coord[1] for coord in data]
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
