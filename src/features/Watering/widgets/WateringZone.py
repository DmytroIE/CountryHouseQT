from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QDoubleSpinBox, QProgressBar, QPushButton, QWidget, \
    QStackedLayout, QSpinBox, QToolButton
from PyQt5.QtCore import Qt

from src.utils.WateringStatuses import *
from src.utils.Buttons import *


# {'ID': 'LZliGv4F', 'typ_flow': 1.2, 'gpio_num': 13, 'enabled': False, 'status': PENDING, 'progress': 0.0,
#     'manu_mode_on': False, 'manually_on': False}


class WateringZone(QFrame):

    def __init__(self, index, data, on_update, on_delete, parent=None):
        super().__init__(parent)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setFixedHeight(50)

        self._cached = {'enabled': False}

        self._lyt_main = QHBoxLayout(self)
        self._lyt_main.setContentsMargins(2, 2, 2, 2)

        self._lyt_stacked = QStackedLayout()
        self._lyt_stacked.setContentsMargins(0, 0, 0, 0)

        # --------Layer 1-----------------
        self._wdg_layer1 = QWidget()
        self._lyt_layer1 = QHBoxLayout(self._wdg_layer1)
        self._lyt_layer1.setContentsMargins(2, 2, 2, 2)

        self._lbl_status = QLabel()
        self._lyt_layer1.addWidget(self._lbl_status)

        self._bar_progress = QProgressBar()
        self._bar_progress.setRange(0, 100)
        self._bar_progress.setTextVisible(True)
        self._lyt_layer1.addWidget(self._bar_progress)

        # self._btn_manu_mode_on = QPushButton('Р.реж.')
        # # self._btn_manu_mode_on.setProperty('class', 'StandardButton')
        # self._btn_manu_mode_on.setFixedWidth(65)
        # self._btn_manu_mode_on.clicked.connect(
        #     lambda: on_update(new_data={'manu_mode_on': not self._cached['manu_mode_on']}))
        # self._lyt_layer1.addWidget(self._btn_manu_mode_on)
        #
        # self._btn_manually_on = QPushButton('Вкл. в р.')
        # self._btn_manually_on.setFixedWidth(65)
        # self._btn_manually_on.clicked.connect(
        #     lambda: on_update(new_data={'manually_on': not self._cached['manually_on']}))
        # self._lyt_layer1.addWidget(self._btn_manually_on)

        # ----------Layer 2--------------------
        self._wdg_layer2 = QWidget()
        self._lyt_layer2 = QHBoxLayout(self._wdg_layer2)
        self._lyt_layer2.setContentsMargins(2, 2, 2, 2)

        self._lbl_typ_flow = QLabel()
        self._lbl_typ_flow.setStyleSheet('QLabel {background-color: rgb(220,235,250)}')

        self._spb_deviation = QSpinBox()
        self._spb_deviation.setRange(10, 50)

        # self._spb_deviation.editingFinished.connect(lambda: on_update(new_data={'deviation':
        #                                                                            self._spb_deviation.value()}))

        self._lbl_gpio = QLabel()
        self._lbl_gpio.setStyleSheet('QLabel {background-color: rgb(220,235,250)}')

        self._btn_del = QPushButton('DEL')
        self._btn_del.setProperty('class', 'StandardButton')
        # self._btn_del.setFixedWidth(40)
        self._btn_del.clicked.connect(on_delete)

        self._lyt_layer2.addWidget(self._lbl_typ_flow)
        self._lyt_layer2.addWidget(self._spb_deviation)
        self._lyt_layer2.addWidget(QLabel('%'))
        self._lyt_layer2.addWidget(self._lbl_gpio)
        self._lyt_layer2.addStretch()
        self._lyt_layer2.addWidget(self._btn_del)

        # -----------Add layers--------------
        self._lyt_stacked.addWidget(self._wdg_layer1)
        self._lyt_stacked.addWidget(self._wdg_layer2)

        # -----------Main Layout--------------
        self._btn_name = QPushButton()
        # self._btn_name.setFixedWidth(70)
        # self._btn_name.setProperty('class', 'StandardButton')
        self._btn_name.clicked.connect(lambda: on_update(new_data={'enabled': not self._cached['enabled']}))

        self._btn_next_layer = QToolButton()
        self._btn_next_layer.setArrowType(Qt.RightArrow)
        self._btn_next_layer.setProperty('class', 'StandardButton')
        self._curr_index = 0
        self._btn_next_layer.clicked.connect(lambda: self._lyt_stacked.setCurrentIndex(self._change_curr_index()))

        self.update_index(index)
        self.apply_updates(data)  # чтобы не дублировать код, пользуемся уже готовой функцией

        # эта строка обязательно после апдейта, иначе при записи в спинбокс возникнет бесконечный цикл
        self._spb_deviation.valueChanged.connect(lambda: on_update(new_data={'deviation':
                                                                                 self._spb_deviation.value()}))
        self._lyt_main.addWidget(self._btn_name)
        self._lyt_main.addLayout(self._lyt_stacked)
        self._lyt_main.addWidget(self._btn_next_layer)

    def _change_curr_index(self):
        if self._curr_index == 0:
            self._curr_index = 1
        else:
            self._curr_index = 0
        return self._curr_index

    def update_index(self, ind):
        self._btn_name.setText(f'Зона {ind}')

    def apply_updates(self, new_data):
        self._lbl_typ_flow.setText(f'Тип.расх. {round(new_data["typ_flow"], 1)} м3/ч')
        self._spb_deviation.setValue(new_data['deviation'])
        self._lbl_gpio.setText(f'GPIO {new_data["gpio_num"]}')
        self._lbl_status.setText(f'{statuses[new_data["status"]]}')
        self._bar_progress.setValue(int(new_data['progress']))
        change_toggle_button_style(new_data['enabled'],
                                self._btn_name,
                                'StandardButton',
                                'StandardButton EnabledButton')
        if new_data['valve on']:
            self._btn_next_layer.setStyleSheet('background-color: rgb(193, 225, 211)')
        else:
            self._btn_next_layer.setStyleSheet('background-color: rgb(255, 255, 255)')
        for key in self._cached:
            self._cached[key] = new_data[key]
