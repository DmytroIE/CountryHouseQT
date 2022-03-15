from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QTimeEdit, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt, QTime

from src.utils.Buttons import changeToggleButtonStyle


class WateringCycle(QFrame):

    def __init__(self, index, data, on_update, on_delete, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setFixedWidth(90)

        self._cached = {'enabled': False}

        self._lyt_main = QVBoxLayout(self)
        self._lyt_main.setContentsMargins(2, 2, 2, 2)

        self._btn_name = QPushButton()
        self._btn_name.clicked.connect(lambda: on_update(new_data={'enabled': not self._cached['enabled']}))
        self._btn_name.setFixedWidth(70)

        self._tm_time = QTimeEdit()

        self._btn_del = QPushButton('DEL')
        self._btn_del.setProperty('class', 'StandardButton')
        self._btn_del.setFixedWidth(40)
        self._btn_del.clicked.connect(on_delete)

        self.update_index(index)
        self.apply_updates(data)

        self._tm_time.timeChanged.connect(lambda: on_update(new_data={'hour': self._tm_time.time().hour(),
                                                                      'minute': self._tm_time.time().minute()}))

        self._lyt_main.addWidget(self._btn_name)
        self._lyt_main.setAlignment(self._btn_name, Qt.AlignHCenter)
        self._lyt_main.addWidget(self._tm_time)
        self._lyt_main.addWidget(self._btn_del)
        self._lyt_main.setAlignment(self._btn_del, Qt.AlignHCenter)

    def update_index(self, ind):
        self._btn_name.setText(f'Полив {ind}')

    def apply_updates(self, new_data):
        self._tm_time.setTime(QTime(new_data['hour'], new_data['minute']))
        changeToggleButtonStyle(new_data['enabled'],
                                self._btn_name,
                                'StandardButton',
                                'StandardButton EnabledButton')
        for key in self._cached:
            self._cached[key] = new_data[key]
