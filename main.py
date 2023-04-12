from PyQt5 import QtWidgets
from PyQt5.QtCore import QLocale
from PyQt5.QtWidgets import QApplication, QMainWindow

import sys

from src.MainWidget import MainWidget
from src.controller.Controller import Controller


class MainWindow(QMainWindow):

    def __init__(self, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('Моя дача')
        self.setGeometry(0, 0, 800, 480)

        self._wdg_main = MainWidget()

        self.setCentralWidget(self._wdg_main)
        locale = QLocale(QLocale.Ukrainian, QLocale.Ukraine)
        QLocale.setDefault(locale)
        # print(locale.country())
        # print(locale.language())
        # print(locale.name())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("QVBoxLayout { padding-top: 1px;  padding-bottom: 1px}")  # ???????????????
    app.setStyleSheet('.StandardButton {\
                                                     background-color: rgb(250,250,250);\
                                                     border-style: solid;\
                                                     border-width: 1px;\
                                                     border-radius: 4px;\
                                                     border-color: rgb(180,180,180);\
                                                     padding: 4px;\
                                                     }\
                                       .StandardButton:hover {\
                                                     border-color: rgb(190,250,210);\
                                                     background-color: rgb(230,240,240);\
                                                     }\
                                       .EnabledButton {\
                                                     border-color: rgb(150,225,211);\
                                                     background-color: rgb(193, 225, 211);\
                                                    }\
                                       .EnabledButton:hover{\
                                                      border-color: rgb(130,205,191);\
                                                      background-color: rgb(163, 195, 201);}')
    controller = Controller()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

