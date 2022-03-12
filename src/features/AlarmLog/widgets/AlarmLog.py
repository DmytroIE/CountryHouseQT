from shortid import ShortId
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QListWidget, QHBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import QSize

from src.features.AlarmLog.widgets.AlarmList import AlarmList
from src.store.store import ConnectedToStoreComponent


class AlarmLog(ConnectedToStoreComponent, QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        ConnectedToStoreComponent.__init__(self)

        self._lyt_main = QHBoxLayout(self)

        self._wdg_buttons = QWidget(self)
        self._lyt_buttons = QVBoxLayout(self._wdg_buttons)

        self._btn_ackn = QPushButton('Ackn')
        self._btn_ackn.setProperty('class', 'StandardButton')
        self._btn_ackn.clicked.connect(self._on_ackn)

        self._btn_clear = QPushButton('Очистить')
        self._btn_clear.setProperty('class', 'StandardButton')
        self._btn_clear.clicked.connect(self._on_clear)

        self._lyt_buttons.addWidget(self._btn_ackn)
        self._lyt_buttons.addWidget(self._btn_clear)

        self._wdg_alarm_list = AlarmList(self)

        self._lyt_main.addWidget(self._wdg_buttons)
        self._lyt_main.addWidget(self._wdg_alarm_list)

        self.setFixedHeight(120)

        self._sid = ShortId()

    # временная функция для проверки добавления или удаления виджета в wateringzonelist
    # функции обработки нажатия на кнопки содержат пока проверочный код
    def _on_ackn(self):
        pass

    def _on_clear(self):
        pass

    def _updater(self):
        pass
