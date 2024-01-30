# from svgpathtools import parse_path
# from xml.dom import minidom

# doc = minidom.parse(r"C:\Users\Francois\Documents\1_UdeS\S4\Projet\interface\test_desing.svg")  # parseString also exists
# path_strings = [path.getAttribute('d') for path
#                 in doc.getElementsByTagName('path')]
# my_path = parse_path(path_strings[0])

# print(my_path.points)
from xml.dom import minidom

doc = minidom.parse(r"C:\Users\Francois\Documents\1_UdeS\S4\Projet\interface\test_losange.svg")  # parseString also exists
path_strings = [path.getAttribute('d') for path
                in doc.getElementsByTagName('path')]
width = [svg.getAttribute('width') for svg in doc.getElementsByTagName("svg")]
height = [svg.getAttribute('height') for svg in doc.getElementsByTagName("svg")]
doc.unlink()


from svgpath2mpl import parse_path



# svgpath = 'M10 10 C 20 20, 40 20, 50 10Z'
mpl_path = parse_path(str(path_strings))
coords = mpl_path.to_polygons()
with open("coordo_output.txt", "w") as f:
    f.write(str(path_strings))
print(coords)