from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

import sys

from src.MainWidget import MainWidget


class MainWindow(QMainWindow):

    def __init__(self, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('My Countryhouse')
        self.setGeometry(0, 0, 800, 480)

        self._wdg_main = MainWidget()

        self.setCentralWidget(self._wdg_main)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

