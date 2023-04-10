from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTabWidget, QPushButton


from src.features.Watering.widgets.Watering import Watering
from src.features.AlarmLog.widgets.AlarmLog import AlarmLog
from src.features.TestWindow.widgets.TestWatering import TestWatering


class MainWidget(QtWidgets.QWidget):

    def __init__(self, **kwargs):
        QtWidgets.QWidget.__init__(self)
        self._create_ui()

    def _create_ui(self):
        self._lyt_main = QtWidgets.QVBoxLayout(self)
        self._tab_main = QTabWidget(self)

        self._scr_watering = QtWidgets.QScrollArea()
        self._wdg_watering = Watering()
        self._scr_watering.setWidget(self._wdg_watering)

        self._tab_main.addTab(self._scr_watering, 'Полив')

        self._wdg_alarm_log = AlarmLog()

        self._lyt_main.addWidget(self._tab_main)
        self._lyt_main.addWidget(self._wdg_alarm_log)

        # Test window
        self._test_window = None
        self._btn_test_watering = QPushButton('Тест полив')
        self._btn_test_watering.clicked.connect(self._create_test_window)
        self._lyt_main.addWidget(self._btn_test_watering)

    def _create_test_window(self):
        if self._test_window is None:
            self._test_window = TestWatering()
        self._test_window.show()


