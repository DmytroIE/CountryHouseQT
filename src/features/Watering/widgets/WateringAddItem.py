from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSpinBox, QLabel, QVBoxLayout
from shortid import ShortId

from src.store.store import ConnectedToStoreComponent


class WateringAddItem(ConnectedToStoreComponent, QWidget):

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)
        ConnectedToStoreComponent.__init__(self)

        self._lyt_main = QVBoxLayout(self)
        self._lyt_main.setContentsMargins(0, 0, 0, 0)

        # ------------new zone row------------
        self._lyt_row1 = QHBoxLayout(self)
        self._lyt_main.setContentsMargins(2, 2, 2, 2)

        self._btn_add_zone = QPushButton('Добавить зону')
        self._btn_add_zone.clicked.connect(self._add_new_zone)

        self._lbl_new_zone_index = QLabel('Индекс вставки')

        self._spb_new_zone_index = QSpinBox()
        self._spb_new_zone_index.setValue(0)
        self._spb_new_zone_index.setToolTip('Индекс вставки новой зоны')

        self._lyt_row1.addWidget(self._btn_add_zone, 1)
        self._lyt_row1.addWidget(self._lbl_new_zone_index)
        self._lyt_row1.addWidget(self._spb_new_zone_index)

        # ------------new cycle row------------
        self._lyt_row2 = QHBoxLayout(self)
        self._lyt_main.setContentsMargins(2, 2, 2, 2)

        self._btn_add_cycle = QPushButton('Добавить цикл')
        # self._btn_add_zone.clicked.connect()

        self._lbl_new_cycle_index = QLabel('Индекс вставки')

        self._spb_new_cycle_index = QSpinBox()
        self._spb_new_cycle_index.setValue(0)
        self._spb_new_cycle_index.setToolTip('Индекс вставки нового цикла')

        self._lyt_row2.addWidget(self._btn_add_cycle, 1)
        self._lyt_row2.addWidget(self._lbl_new_cycle_index)
        self._lyt_row2.addWidget(self._spb_new_cycle_index)

        self._lyt_main.addLayout(self._lyt_row1)
        self._lyt_main.addLayout(self._lyt_row2)

        self._sid = ShortId()

    def _add_new_zone(self):
        self._dispatch({'type': 'wateringzones/ADD_ITEM', 'payload': {'index': self._spb_new_zone_index.value(),
                                                                      'new_item': {'ID': self._sid.generate(),
                                                                                   'typ_flow': 1.2,
                                                                                   'gpio_num': 0, 'enabled': False,
                                                                                   'status': 3, 'progress': 0.0,
                                                                                   'manu_mode_on': False,
                                                                                   'manually_on': False}}})

    def _updater(self):
        pass
