from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QTimeEdit, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt, QTime

from src.utils.WateringStatuses import *
from src.utils.Buttons import change_toggle_button_style


class WateringCycle(QFrame):

    def __init__(self, data, on_update, parent=None):
        super().__init__(parent)
        self._id = data['ID']
        self._cached_for_widget = {'hour': None, 'minute': None, 'enabled': None}
        self._create_ui(data, on_update)

    def _create_ui(self, data, on_update):
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setFixedWidth(90)

        self._lyt_main = QVBoxLayout(self)
        self._lyt_main.setContentsMargins(2, 2, 2, 2)

        self._btn_name = QPushButton('Вкл')
        self._btn_name.clicked.connect(
            lambda: on_update(ID=self._id,
                              new_data={
                                  'enabled': not self._cached_for_widget['enabled']
                              }))
        self._btn_name.setFixedWidth(70)

        self._tm_time = QTimeEdit()
        self.apply_updates(data)
        # эти строки обязательно после self.apply_updates, иначе при записи в _tm_tim
        # возникнет бесконечный цикл
        self._tm_time.timeChanged.connect(
            lambda: on_update(ID=self._id,
                              new_data={'hour': self._tm_time.time().hour(),
                                        'minute': self._tm_time.time().minute()}))

        self._lyt_main.addWidget(self._btn_name)
        self._lyt_main.setAlignment(self._btn_name, Qt.AlignHCenter)
        self._lyt_main.addWidget(self._tm_time)

    def apply_updates(self, new_data):
        # print('cycles apply update')
        changed = False
        if new_data['hour'] != self._cached_for_widget['hour'] or \
                new_data['minute'] != self._cached_for_widget['minute']:
            self._tm_time.setTime(QTime(new_data['hour'], new_data['minute']))
            changed = True
        if new_data['enabled'] != self._cached_for_widget['enabled']:
            change_toggle_button_style(new_data['enabled'],
                                       self._btn_name,
                                       'StandardButton',
                                       'StandardButton EnabledButton')
            changed = True

        if changed:
            for key in self._cached_for_widget:
                self._cached_for_widget[key] = new_data[key]
