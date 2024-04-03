# Interface Management
from Windows.Graphicus03_Main import Ui_Graphicus03
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsRectItem, QGraphicsPolygonItem
from PySide2.QtCore import QPointF, QObject, QThread, Signal, Qt
from PySide2.QtGui import QPolygonF, QBrush, QPen
from modules import PySide_dark_theme
# File Management with explorer
import tkinter
from tkinter import filedialog
# Read data from svg file
from xml.dom import minidom
# from svgpathtools import parse_path
from svgpath2mpl import parse_path
from math import sqrt
from queue import Queue
# test output
import json
from time import sleep
# controle laser
import RPi.GPIO as GPIO

class MainWindow(Ui_Graphicus03, QMainWindow):
    def __init__(self, queueOut: Queue, queueIn: Queue, is_test = False):
        """Initilise l'interface
        """
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.scene = QGraphicsScene(0, 0, 200, 140)
        self.screen_info = None
        self.modifySetup()
        self.setupConnection(is_test)
        self.selected_file = "None"
        self.polygonItems = []
        self.queueIn = queueIn
        self.queueOut = queueOut

    def setupConnection(self, is_test):
        """Connecte les évènements de l'interface à leur fonction dédiée
        """
        self.PB_selectFile.pressed.connect(self.fileSelection)
        if not is_test:
            self.PB_launch.pressed.connect(self.startExecution)
        else:
            self.PB_launch.pressed.connect(self.startExecution_test_print)

    def modifySetup(self):
        """Modifie le setup fait par QtDesing
        """
        self.GV_logo.setScene(self.scene)
        self.CB_material.addItems(["Plastique", "Vitre", "Métal"])
        for CB_unit in [self.CB_unit_radius, self.CB_unit_Largeur, self.CB_unit_Hauteur]:
            CB_unit.addItems(["cm", "mm", "po"])
        self.progressBar.setValue(0)
        for DSB_item in [self.DSB_Hauteur, self.DSB_Largeur, self.DSB_radius]:
            DSB_item.setValue(5)

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
            self.changeColorItem()

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
                    
        scale_to_img_x = self.GV_logo.width()/(fartest_point[3]-closest_point[1])
        scale_to_img_y = self.GV_logo.height()/(fartest_point[4]-closest_point[2])
        print(scale_to_img_x, scale_to_img_y)
        scale = scale_to_img_x/2
        if scale_to_img_y < scale_to_img_x:
            scale = scale_to_img_y/2
        self.scale_pic = scale
        # déplace tous les items vers l'origine avec le décalage calculé précédement        
        pen_item = QPen(
            Qt.black,
            0.5/scale,
            Qt.SolidLine,
            Qt.RoundCap,
            Qt.RoundJoin
            )
        for item_ in self.polygonItems:
            item_.setScale(scale)
            item_.setPos(item_.pos() - QPointF(closest_point[1]*scale, closest_point[2]*scale)) 
            item_.setPen(pen_item)
        self.scene.setSceneRect(0, 0, fartest_point[3]*scale-closest_point[1]*scale, fartest_point[4]*scale-closest_point[2]*scale)
        self.x_offset = closest_point[0]
        self.y_offset = closest_point[1]
        
        

        print("fini")
    
    def changeColorItem(self):
        for item in self.polygonItems:
            collision_count = self.get_item_collisions(item) 
            # print(item.zValue())
            # if collision_count == 1:
            #     continue
            # elif collision_count == 0:
            #     item.setBrush(Qt.white)
            # elif collision_count == 2:
            #     item.setBrush(Qt.red)
            # elif collision_count >= 3:
            #     item.setBrush(Qt.blue)
            # else:
            #     item.setBrush(Qt.black)

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
        ls_laser = {}
        max_x = 0
        max_y = 0
        min_x = []
        min_y = []
        width  = self.getMesureInmm(self.DSB_Largeur.value(), self.CB_unit_Largeur.currentText())
        height = self.getMesureInmm(self.DSB_Hauteur.value(), self.CB_unit_Hauteur.currentText())
        radius = self.getMesureInmm(self.DSB_radius.value() , self.CB_unit_radius.currentText())
        
        for item in self.scene.items():
            bounding_rec = item.boundingRect()  
            delta = 10          

            top     = (bounding_rec.topLeft().x() -delta) * self.scale_pic
            left    = (bounding_rec.topLeft().y() -delta) * self.scale_pic
            bot     = (bounding_rec.bottomRight().x() +delta) * self.scale_pic
            right   = (bounding_rec.bottomRight().y() +delta) * self.scale_pic
            min_x.append(top - self.x_offset)
            min_y.append(left - self.y_offset)
            # print(top, bot, left, right)
            precision:int = 1
            for y in range(int(right - left)*precision):
                yy = int(y + left - self.y_offset) 
                if not ls_laser.__contains__(yy):
                    ls_laser[yy] = {}
                for x in range(int(bot - top)*precision):
                    xx = int(x + top - self.x_offset)
                    if not ls_laser[yy].__contains__(xx):
                        ls_laser[yy][xx] = False
                    if item.contains(QPointF((x + top)/self.scale_pic, (y + left)/self.scale_pic)):
                        ls_laser[yy][xx] = not ls_laser[yy][xx]
            if xx>max_x:
                max_x = xx
            if yy>max_y:
                max_y = yy
      
        myKeys = list(ls_laser.keys())
        myKeys.sort()
        myValues = list(list(ls_laser.values())[0].keys())
        myValues.sort()
        min_value = min(min_x)
        min_key = min(min_y)
        new_ls_laser = {}
        length_x = max_x - min_value
        length_y = max_y - min_key
        self.dim_zone = (length_x, length_y)
        for key in ls_laser.keys():
            value = ls_laser[key]
            new_value = {}
            for value_key in value.keys():
                new_value[width*(value_key - min_value - delta/2)/length_x] = value[value_key]
            new_ls_laser[height*(int(key) - min_key - delta/2)/length_y] = new_value
        with open("sortie_bounding_rect_met.json", 'w') as f:
            json.dump(new_ls_laser, f, indent=4)
        self.ls_laser = new_ls_laser
        self.startExecution_qthread()
        print("finis ic")
        sleep(2)
        self.queueOut.put(["debut", width, height, radius, self.ls_laser])
        print("put done")

    def startExecution_qthread(self):
        """lance le signal dans la Queue pour débuter la gravure et initilise la reception des positions pour graver
        """
        # print("thread initialise")
        # rapport_h = self.dim_zone[0]/(self.DSB_Hauteur.value()*10)              # self.scene.itemsBoundingRect().x()
        # rapport_l = self.dim_zone[1]/(self.DSB_Largeur.value()*10)              # self.scene.itemsBoundingRect().y()

        # self.thread = QThread()
        # self.worker = worker(self.queueIn, self.ls_laser, self.progress_done, rapport_h, rapport_l, self.dim_zone)
        # self.worker.moveToThread(self.thread)
        # # connecter les signaux entre le worker et la thread associé
        # self.thread.started.connect(self.worker.run_)
        # self.worker.finished.connect(self.thread.quit)
        # self.worker._progress.connect(self.updateProgress)
        # self.worker.finished.connect(self.worker.deleteLater)
        # self.thread.finished.connect(self.thread.deleteLater)
        # # start the thread
        # self.thread.start()

        # # controle laser
        # GPIO.setup(LASER, GPIO.OUT)

    @staticmethod
    def getMesureInmm(value, unit):
        # TODO RIGHT HERE
        if unit == "mm":
            return value
        elif unit == "cm":
            return value*10
        elif unit == "po":
            return value*25.4
        else:
            return 0

    def progress_done(self):
        self.progressBar.setValue(self.progressBar.maximum())

    def updateProgress(self, coords):
        x = coords[0]
        y = coords[1]
        collision = self.get_collisions(x, y)
        # TODO allumer le laser en fonction de collision
        self.progressBar.setValue(y * int(self.scene.sceneRect().height()))

    def startExecution_test_print(self):
        """test la génération de signal pour le laser
        analyse chaque pixel de l'interface pour générer une image représentant si le laser est allumé ou fermé
        à combiner avec "from_bin_map_to_image.py"
        """
        self.PB_launch.setDisabled(True)
        cb_unit_index = self.CB_unit_radius.currentIndex()
        cb_material_index = self.CB_material.currentIndex()
        print(f"startExecution - {self.DSB_radius.value()} {self.CB_unit_radius.itemText(cb_unit_index)} - {self.CB_material.itemText(cb_material_index)}")

        Laser = QGraphicsRectItem(0.5, 0.5, 0.01, 0.01)
        self.scene.addItem(Laser)

        width = self.scene.sceneRect().width()
        height = self.scene.sceneRect().height()
        x0 = self.scene.sceneRect().x()
        y0 = self.scene.sceneRect().y()
        
        print(x0, y0, width, height)

        result = ""
        self.progressBar.setMaximum((int(height) - int(y0)) * (int(width) - int(x0)))
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
                self.progressBar.setValue(y*int(width) + x) 
                last_collision = collision

            result += "\n"
        with open("ouput_test.txt", 'w') as f:
            f.write(result)
        self.progressBar.setValue(self.progressBar.maximum())
        self.PB_launch.setEnabled(True)

    def get_collisions(self, x, y) -> bool:
        self.Laser.setPos(x, y)
        collision = 0
        for item in self.polygonItems:
            if self.Laser.collidesWithItem(item):
                collision += 1
        # GPIO.output(LASER, collision%2)        
        return collision % 2 
    
    def get_item_collisions(self, item) -> bool:
        collision = -1
        for other_item in self.polygonItems:
            if item.collidesWithItem(other_item):
                collision += 1                
        return (collision)
    
# class worker(QObject):
#     finished = Signal()
#     _progress = Signal(tuple)

#     def __init__(self, queueIn:Queue, target_func, end_call_func, rH, rL, dimension):
#         super().__init__()
#         print("worker init")
#         self.queueIn = queueIn
#         self.callback = target_func
#         self.end_call_func = end_call_func
#         self.rH = rH
#         self.rL = rL
#         self.dim = dimension

#     def run_(self):
#         stop = False
#         result_worker = []
#         while not stop:
#             if not self.queueIn.empty():
#                 lecture = self.queueIn.get_nowait()
#                 if type(lecture) == str:
#                     if lecture == "finis":
#                         self.end_call_func()
#                         stop = True
#                 elif type(lecture) == list:
#                     # TODO scaling from mm to image
#                     x = lecture[0]*self.rH
#                     y = lecture[1]*self.rL
#                     res_y = self.ls_laser.get(y) or self.ls_laser[min(self.ls_laser.keys(), key = lambda key: abs(key-y))]
#                     res_x = res_y.get(x) or res_y[min(res_y.keys(), key = lambda key: abs(key-x))]
#                     # GPIO.output(LASER, res_x)
#                     self._progress.emit((x, y))                    
        
#         sleep(5)
#         self.finished.emit()


def initWindow(queueOut, queueIn, is_test = False):
    app = QApplication([])
    win = MainWindow(queueOut, queueIn, is_test)
    win.show()
    # PySide_dark_theme.toggleDarkTheme(app, PySide_dark_theme.darkTheme())
    app.exec_()

if __name__ == "__main__":
    # lance le protocole de test de gravure 
    initWindow(None, None, True)