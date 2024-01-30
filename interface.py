# Interface Management
from Windows.Graphicus03_Main import Ui_Graphicus03
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsRectItem, QGraphicsPolygonItem
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPolygonF
from modules import PySide_dark_theme
# File Management with explorer
import tkinter
from tkinter import filedialog
# Read data from svg file
from xml.dom import minidom
# from svgpathtools import parse_path
from svgpath2mpl import parse_path
from math import sqrt


class MainWindow(Ui_Graphicus03, QMainWindow):
    def __init__(self):
        """Initilise l'interface
        """
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.scene = QGraphicsScene(0, 0, 200, 140)
        self.screen_info = None
        self.modifySetup()
        self.setupConnection()
        self.selected_file = "None"
        self.polygonItems = []

    def setupConnection(self):
        """Connecte les évènements de l'interface à leur fonction dédiée
        """
        self.PB_selectFile.pressed.connect(self.fileSelection)
        self.PB_launch.pressed.connect(self.startExecution)

    def modifySetup(self):
        """Modifie le setup fait par QtDesing
        """
        self.GV_logo.setScene(self.scene)
        self.CB_material.addItems(["Plastic", "Glass", "Metal"])
        self.CB_unit.addItems(["cm", "mm", "inch"])

    def fileSelection(self):  
        """Ouvre l'exploreur de fichier pour selectionner un SVG
        """
        tkinter.Tk().withdraw()
        selected_file_temp = filedialog.askopenfile(filetypes=[("vector files", ["*.svg"]), ("all files", "*")])
        if selected_file_temp != None:
            self.selected_file = selected_file_temp
        print(self.selected_file.name)
        self.LE_csvFile.setText(self.selected_file.name)
        self.modifyImageViewer()

    def modifyImageViewer(self):
        """Modifie l'image du logo sur le graphique view avec l'image provenant du fichier SVG
        """
        self.scene.clear()
        # get the svg information from file
        doc = minidom.parse(self.selected_file.name)
        path_strings = [path.getAttribute('d') for path
                        in doc.getElementsByTagName('path')]
        width = [svg.getAttribute('width') for svg in doc.getElementsByTagName("svg")]
        height = [svg.getAttribute('height') for svg in doc.getElementsByTagName("svg")]
        doc.unlink()

        # create map of point from svg path
        mpl_path = parse_path(str(path_strings))
        coords = mpl_path.to_polygons()
        self.scene = QGraphicsScene(-10, -10, self.GV_logo.width(), self.GV_logo.height())
        self.GV_logo.setScene(self.scene)
        self.polygonItems = []
        closest_point = []
        fartest_point = []
        for tableau in coords:
            new_polygon = QPolygonF()
            for points in tableau:
                new_point = QPointF(points[0], points[1])
                new_polygon.append(new_point)
            new_item = QGraphicsPolygonItem()
            new_item.setPolygon(new_polygon)
            self.polygonItems.append(new_item)
            self.scene.addItem(new_item)
            # calcul de combien il faut décaller les items pour les ramener à l'origine (0, 0)
            distance = self.get_distance_from_origine(new_item)
            if closest_point == []:
                closest_point = distance
            else:
                if closest_point[1] > distance[1]:
                    closest_point[1] = distance[1]
                if closest_point[2] > distance[2]:
                    closest_point[2] = distance[2]
            if fartest_point == []:
                fartest_point = distance
            else:
                if fartest_point[3] < distance[3]:
                    fartest_point[3] = distance[3]
                if fartest_point[4] < distance[4]:
                    fartest_point[4] = distance[4]
        # déplace tous les items vers l'origine avec le décalage calculé précédement
        for item_ in self.polygonItems:
            item_.setPos(item_.pos() - QPointF(closest_point[1], closest_point[2])) 
        self.scene.setSceneRect(0, 0, fartest_point[3]-closest_point[1], fartest_point[4]-closest_point[2])
        print("fini")
    
    def get_distance_from_origine(self, graphic_item: QGraphicsPolygonItem):
        """Retourne la distance entre le entre l'origine (0, 0) et la position d'un QGraphicsItem

        Args:
            graphic_item (QGraphicsPolygonItem): Un item du QGraphicView

        Returns:
            [float, int, int, int, int] : [distance entre (0, 0) et origine du rectangle, x_origine item, y_origine item, x_final item, y_final item]
        """
        b_rect = graphic_item.boundingRect()
        distance = sqrt(b_rect.x()**2 + b_rect.y()**2)
        return [distance, b_rect.x(), b_rect.y(), b_rect.x()+b_rect.width(), b_rect.y()+b_rect.height()]

    def startExecution(self):
        """lance le signal dans la Queue pour débuter la gravure et initilise la reception des positions pour graver
        """
        self.PB_launch.setDisabled(True)
        cb_unit_index = self.CB_unit.currentIndex()
        cb_material_index = self.CB_material.currentIndex()
        print(f"startExecution - {self.DSB_radius.value()} {self.CB_unit.itemText(cb_unit_index)} - {self.CB_material.itemText(cb_material_index)}")

        Laser = QGraphicsRectItem(0.5, 0.5, 0.01, 0.01)
        self.scene.addItem(Laser)

        width = self.scene.sceneRect().width()
        height = self.scene.sceneRect().height()
        x0 = self.scene.sceneRect().x()
        y0 = self.scene.sceneRect().y()
        
        print(x0, y0, width, height)

        result = ""
        for y in range(int(y0), int(height)):
            last_collision = 0
            for item in self.polygonItems:
                if Laser.collidesWithItem(item):
                    last_collision += 1
            for x in range(int(x0), int(width)):
                #inversed for some reason
                Laser.setPos(x, y)
                collision = 0
                for item in self.polygonItems:
                    if Laser.collidesWithItem(item):
                        collision += 1
                result += str(collision % 2 ) + " "  
                #for smoother result 
                #result += str(collision % 2 * last_collision % 2) + " "
                last_collision = collision
            result += "\n"
        with open("ouput_test.txt", 'w') as f:
            f.write(result)
        print("finished")
        self.PB_launch.setEnabled(True)


if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    PySide_dark_theme.toggleDarkTheme(app, PySide_dark_theme.darkTheme())
    app.exec()