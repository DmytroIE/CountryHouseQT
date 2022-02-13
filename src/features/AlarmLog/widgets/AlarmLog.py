from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QListWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import QSize

from src.features.AlarmLog.widgets.AlarmList import AlarmList


class AlarmLog(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self._lyt_main = QHBoxLayout(self)

        self._button = QPushButton(self)
        self._button.setText('Clear log')

        self._wdg_alarm_list = AlarmList(self)

        self._lyt_main.addWidget(self._button)
        self._lyt_main.addWidget(self._wdg_alarm_list)

        self.setFixedHeight(120)

