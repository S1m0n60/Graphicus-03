if __name__ == "__main__":  
    from PIL import Image

    with open(r"ouput_test.txt", 'r') as f:
        raw_data = f.read()
    lines = raw_data.split("\n")

    img = []
    for line in lines:
        line_int = []
        for value in line.split(" "):
            if value.isnumeric():
                if not value == "":
                    img.append(int(value))
                else:
                    print("wtf")
    size = (round(len(img)/(len(lines)-1)), len(lines))
    print(type(size), size)

    im = Image.new("1", size)
    # im = Image.new("1", (4, 4))
    im.putdata(img)
    im.save("your_file.png")
    