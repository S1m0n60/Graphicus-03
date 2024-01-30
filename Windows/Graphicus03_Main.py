# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Graphicus03_Main.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QGraphicsView,
    QLabel, QLineEdit, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QWidget)

class Ui_Graphicus03(object):
    def setupUi(self, Graphicus03):
        if not Graphicus03.objectName():
            Graphicus03.setObjectName(u"Graphicus03")
        Graphicus03.resize(307, 400)
        Graphicus03.setMinimumSize(QSize(307, 400))
        Graphicus03.setMaximumSize(QSize(307, 400))
        self.centralwidget = QWidget(Graphicus03)
        self.centralwidget.setObjectName(u"centralwidget")
        self.LE_csvFile = QLineEdit(self.centralwidget)
        self.LE_csvFile.setObjectName(u"LE_csvFile")
        self.LE_csvFile.setGeometry(QRect(12, 60, 201, 20))
        self.LB_title = QLabel(self.centralwidget)
        self.LB_title.setObjectName(u"LB_title")
        self.LB_title.setGeometry(QRect(0, 0, 301, 51))
        font = QFont()
        font.setFamilies([u"Source Code Pro"])
        font.setPointSize(24)
        font.setBold(True)
        self.LB_title.setFont(font)
        self.LB_title.setAlignment(Qt.AlignCenter)
        self.PB_selectFile = QPushButton(self.centralwidget)
        self.PB_selectFile.setObjectName(u"PB_selectFile")
        self.PB_selectFile.setGeometry(QRect(220, 60, 71, 23))
        font1 = QFont()
        font1.setFamilies([u"Source Sans Pro"])
        font1.setPointSize(10)
        font1.setBold(False)
        self.PB_selectFile.setFont(font1)
        self.LB_radius = QLabel(self.centralwidget)
        self.LB_radius.setObjectName(u"LB_radius")
        self.LB_radius.setGeometry(QRect(10, 90, 91, 21))
        font2 = QFont()
        font2.setFamilies([u"Source Serif Pro"])
        font2.setPointSize(16)
        font2.setBold(True)
        self.LB_radius.setFont(font2)
        self.DSB_radius = QDoubleSpinBox(self.centralwidget)
        self.DSB_radius.setObjectName(u"DSB_radius")
        self.DSB_radius.setGeometry(QRect(120, 90, 91, 21))
        font3 = QFont()
        font3.setFamilies([u"Source Sans Pro"])
        font3.setPointSize(11)
        font3.setBold(False)
        self.DSB_radius.setFont(font3)
        self.DSB_radius.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.DSB_radius.setAccelerated(True)
        self.DSB_radius.setSingleStep(0.100000000000000)
        self.LB_material = QLabel(self.centralwidget)
        self.LB_material.setObjectName(u"LB_material")
        self.LB_material.setGeometry(QRect(10, 120, 101, 21))
        self.LB_material.setFont(font2)
        self.CB_material = QComboBox(self.centralwidget)
        self.CB_material.setObjectName(u"CB_material")
        self.CB_material.setGeometry(QRect(120, 120, 171, 22))
        self.CB_material.setFont(font1)
        self.CB_unit = QComboBox(self.centralwidget)
        self.CB_unit.setObjectName(u"CB_unit")
        self.CB_unit.setGeometry(QRect(220, 90, 71, 22))
        self.CB_unit.setFont(font1)
        self.PB_launch = QPushButton(self.centralwidget)
        self.PB_launch.setObjectName(u"PB_launch")
        self.PB_launch.setGeometry(QRect(10, 310, 281, 41))
        font4 = QFont()
        font4.setFamilies([u"Source Sans Pro"])
        font4.setPointSize(16)
        font4.setBold(True)
        self.PB_launch.setFont(font4)
        self.GV_logo = QGraphicsView(self.centralwidget)
        self.GV_logo.setObjectName(u"GV_logo")
        self.GV_logo.setGeometry(QRect(10, 150, 281, 151))
        Graphicus03.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Graphicus03)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 307, 21))
        Graphicus03.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Graphicus03)
        self.statusbar.setObjectName(u"statusbar")
        Graphicus03.setStatusBar(self.statusbar)

        self.retranslateUi(Graphicus03)

        QMetaObject.connectSlotsByName(Graphicus03)
    # setupUi

    def retranslateUi(self, Graphicus03):
        Graphicus03.setWindowTitle(QCoreApplication.translate("Graphicus03", u"MainWindow", None))
        self.LB_title.setText(QCoreApplication.translate("Graphicus03", u"Graphicus03", None))
        self.PB_selectFile.setText(QCoreApplication.translate("Graphicus03", u"Select File", None))
        self.LB_radius.setText(QCoreApplication.translate("Graphicus03", u"Radius :", None))
        self.LB_material.setText(QCoreApplication.translate("Graphicus03", u"Material :", None))
        self.PB_launch.setText(QCoreApplication.translate("Graphicus03", u"LAUNCH", None))
    # retranslateUi

