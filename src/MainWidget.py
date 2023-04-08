from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTabWidget


from src.features.Watering.widgets.Watering import Watering
from src.features.AlarmLog.widgets.AlarmLog import AlarmLog


class MainWidget(QtWidgets.QWidget):

    def __init__(self, **kwargs):
        QtWidgets.QWidget.__init__(self)
        self.setStyleSheet('.StandardButton {\
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

        self._lyt_main = QtWidgets.QVBoxLayout(self)
        self._tab_main = QTabWidget(self)

        self._scr_watering = QtWidgets.QScrollArea()
        self._wdg_watering = Watering()
        self._scr_watering.setWidget(self._wdg_watering)

        self._tab_main.addTab(self._scr_watering, 'Полив')

        self._wdg_alarm_log = AlarmLog()

        self._lyt_main.addWidget(self._tab_main)
        self._lyt_main.addWidget(self._wdg_alarm_log)
