from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTabWidget


from src.features.Watering.widgets.Watering import Watering
from src.features.AlarmLog.widgets.AlarmLog import AlarmLog


class MainWidget(QtWidgets.QWidget):

    def __init__(self, **kwargs):
        QtWidgets.QWidget.__init__(self)

        self._lyt_main = QtWidgets.QVBoxLayout(self)
        self._tab_main = QTabWidget(self)

        self._scr_watering = QtWidgets.QScrollArea()
        self._wdg_watering = Watering()
        self._scr_watering.setWidget(self._wdg_watering)

        self._tab_main.addTab(self._scr_watering, 'Полив')

        self._wdg_alarm_log = AlarmLog()

        self._lyt_main.addWidget(self._tab_main)
        self._lyt_main.addWidget(self._wdg_alarm_log)
