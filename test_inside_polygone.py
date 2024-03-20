from Windows.Graphicus03_Main import Ui_Graphicus03
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsRectItem, QGraphicsPolygonItem
from PySide2.QtCore import QPointF, QObject, QThread, Signal, Qt
from PySide2.QtGui import QPolygonF, QBrush, QPen


from icecream import ic

def output_to_file(text):
    with open("DEBUG.txt", 'a') as f:
        f.write(text + "\n")

ic.configureOutput(prefix='Debug | ', outputFunction=output_to_file)


class MainWindow(Ui_Graphicus03, QMainWindow):
    def __init__(self):
        """Initilise l'interface
        """
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.scene = QGraphicsScene(0, 0, 200, 140)
        self.screen_info = None
        self.modifySetup()
        self.selected_file = "None"
        self.polygonItems = []
        self.startExecution()

    def modifySetup(self):
        """Modifie le setup fait par QtDesing
        """
        self.GV_logo.setScene(self.scene)
        self.CB_material.addItems(["Plastique", "Vitre", "Métal"])
        for CB_unit in [self.CB_unit_radius, self.CB_unit_Largeur, self.CB_unit_Hauteur]:
            CB_unit.addItems(["cm", "mm", "po"])
        for DSB_item in [self.DSB_radius, self.DSB_Largeur, self.DSB_Hauteur]:
            DSB_item.setValue(50)
        self.progressBar.setValue(0)
    
    def startExecution(self):
        ic()
        poly = QPolygonF()
        poly.append([QPointF(10, 0), QPointF(100, 0), QPointF(100, 100), QPointF(0, 50)])
        I_poly = QGraphicsPolygonItem(poly)
        self.scene.addItem(I_poly)

        ls_laser = {}
        bounding_rec = I_poly.boundingRect()
        
        top     = bounding_rec.topLeft().x()
        left    = bounding_rec.topLeft().y()
        bot     = bounding_rec.bottomRight().x()
        right   = bounding_rec.bottomRight().y()
    
        for y in range(int(right - left)):
            if not ls_laser.__contains__(y):
                ls_laser[int(y + left)] = {}
            for x in range(int(bot - top)):
                ls_laser[int(y + left)][int(x + top)] = I_poly.contains(QPointF(x, y))
        
        ic(ls_laser)
        ic()
                


def initWindow():
    app = QApplication([])
    win = MainWindow()
    win.show()
    # PySide_dark_theme.toggleDarkTheme(app, PySide_dark_theme.darkTheme())
    app.exec_()

if __name__ == "__main__":
    # lance le protocole de test de gravure 
    initWindow()