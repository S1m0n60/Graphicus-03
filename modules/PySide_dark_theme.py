from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

def darkTheme():
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    dark_palette.setColorGroup(QPalette.Disabled,
    QColor(26, 26, 26), QColor(30, 30, 30),
    QColor(1, 1, 1), QColor(0.627451, 0.627451, 0.627451), QColor(0.627451, 0.627451, 0.627451),
    QColor(122, 122, 122), Qt.darkRed,
    QColor(13, 13, 13), QColor(26, 26, 26),
    )
    return dark_palette
# Toggle theme function

def toggleDarkTheme(app, dark_palette):
    app.setStyle('Fusion')
    app.setPalette(dark_palette)

if __name__ == '__main__':
    #from PyQt5.QtGui import QBrush
    from PySide2.QtWidgets import *
    from PySide2.QtCore import Qt
    from PySide2.QtGui import QPalette, QColor
    app = QApplication([])
    #app.setStyle('Fusion') #Style needed for palette to work
    # Dark Palette (found on github, couldn't track the original author)
    window = QWidget()
    layout = QGridLayout()
    # Make a few Dials and buttons:
    for i in range(0,4):
        Dial = QDial()
        Button = QPushButton('Button ' + str(i))
        Dial.setNotchesVisible(True)
        layout.addWidget(Button,0,i)
        layout.addWidget(Dial,1,i)
    
    # Toggle push button
    togglePushButton = QPushButton("Dark Mode")
    togglePushButton.setCheckable(True)
    togglePushButton.setChecked(True)
    togglePushButton.clicked.connect(lambda: toggleDarkTheme(app, darkTheme()))
    label = QLabel()

    label.setText('holla mi amor')
    layout.addWidget(label, 2, 1, 1, 3)
    layout.addWidget(togglePushButton,2,3)
    window.setLayout(layout)
    window.show()
    app.exec_()