import sys
from PySide6.QtCore import QDate, QFile, Qt, QTextStream
from PySide6 import QtWidgets 

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("Project 1")
        self.setMinimumSize(600, 600)

        central = QtWidgets.QTextEdit("Main content")
        self.setCentralWidget(central)

        dockWidget = QtWidgets.QDockWidget("Dock Widget", self)
        dockWidget.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dockWidget.setMaximumWidth(200)
        # dockWidget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
        #                     Qt.DockWidgetArea.RightDockWidgetArea)
        label = QtWidgets.QLabel("This is the dock content")
        dockWidget.setWidget(label)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dockWidget)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    print("Starting")
    sys.exit(app.exec())
