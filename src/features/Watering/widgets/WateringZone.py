from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QDoubleSpinBox, QProgressBar, QPushButton, QWidget, \
    QStackedLayout, QSpinBox
from PyQt5.QtCore import QSize

from src.utils.WateringStatuses import *

# {'ID': 'LZliGv4F', 'typ_flow': 1.2, 'gpio_num': 13, 'enabled': False, 'status': PENDING, 'progress': 0.0,
#     'manu_mode_on': False, 'manually_on': False}


class WateringZone(QFrame):

    def __init__(self, data, on_update, on_delete, parent=None):
        super().__init__(parent)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setFixedHeight(50)

        self._cached = {}

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

        self._btn_manu_mode_on = QPushButton('Р.реж.')
        self._btn_manu_mode_on.setMaximumWidth(60)
        self._lyt_layer1.addWidget(self._btn_manu_mode_on)

        self._btn_manually_on = QPushButton('Вкл. в р.')
        self._btn_manually_on.setMaximumWidth(60)
        self._lyt_layer1.addWidget(self._btn_manually_on)

        # ----------Layer 2--------------------
        self._wdg_layer2 = QWidget()
        self._lyt_layer2 = QHBoxLayout(self._wdg_layer2)
        self._lyt_layer2.setContentsMargins(2, 2, 2, 2)

        self._lbl_typ_flow = QLabel('Тип.расх.')

        self._dspb_typ_flow = QDoubleSpinBox()
        self._dspb_typ_flow.setSingleStep(0.1)

        self._lbl_gpio = QLabel('GPIO')

        self._spb_gpio = QSpinBox()
        self._spb_gpio.setRange(0, 31)

        self._btn_del = QPushButton('DEL')
        self._btn_del.setMaximumWidth(40)
        self._btn_del.clicked.connect(on_delete)

        self._lyt_layer2.addWidget(self._lbl_typ_flow)
        self._lyt_layer2.addWidget(self._dspb_typ_flow)
        self._lyt_layer2.addWidget(self._lbl_gpio)
        self._lyt_layer2.addWidget(self._spb_gpio)
        self._lyt_layer2.addWidget(self._btn_del)

        # -----------Add layers--------------
        self._lyt_stacked.addWidget(self._wdg_layer1)
        self._lyt_stacked.addWidget(self._wdg_layer2)

        # -----------Main Layout--------------
        self._btn_name = QPushButton()
        self.apply_updates(data)

        self._curr_index = 0
        self._btn_name.clicked.connect(lambda: self._lyt_stacked.setCurrentIndex(self._change_curr_index()))
        self._btn_name.setMaximumWidth(70)
        self._lyt_main.addWidget(self._btn_name)
        self._lyt_main.addLayout(self._lyt_stacked)

        self._on_update = on_update
        self._on_delete = on_delete

        # self.setFixedSize(QSize(400, 50))

    def _change_curr_index(self):
        if self._curr_index == 0:
            self._curr_index = 1
        else:
            self._curr_index = 0
        return self._curr_index

    def _on_delete_item(self):
        self._dispatch()

    def apply_updates(self, part_data):
        new_data = {**self._cached, **part_data}
        if new_data != self._cached:
            if 'number' in part_data:
                self._btn_name.setText(f'Зона {part_data["number"]}')
            if 'typ_flow' in part_data:
                self._dspb_typ_flow.setValue(float(part_data['typ_flow']))
            if 'gpio_num' in part_data:
                self._spb_gpio.setValue(int(part_data['gpio_num']))
            if 'status' in part_data:
                self._lbl_status.setText(f'{statuses[part_data["status"]]}')
            if 'progress' in part_data:
                self._bar_progress.setValue(int(part_data['progress']))
            if 'manu_mode_on' in part_data:
                bg_color = 'grey'
                if part_data['manu_mode_on']:
                    bg_color = 'green'
                self._btn_manu_mode_on.setStyleSheet(f'background-color: {bg_color}')
            if 'manually_on' in part_data:
                bg_color = 'grey'
                if part_data['manually_on']:
                    bg_color = 'green'
                self._btn_manually_on.setStyleSheet(f'background-color: {bg_color}')
            self._cached = new_data

# class WateringZone(QFrame):
#
#     def __init__(self, data, on_update=0, on_delete=None, parent=None):
#         super().__init__(parent)
#
#         self.setFrameStyle(QFrame.Panel | QFrame.Raised)
#
#         self._cached = {}
#
#         self._lyt_main = QHBoxLayout(self)
#
#         self._lbl_name = QLabel()
#         self._lyt_main.addWidget(self._lbl_name)
#
#         self._dspb_typ_flow = QDoubleSpinBox()
#         # self._lbl_typ_flow.setFrameStyle(QFrame.Panel | QFrame.Sunken)
#         self._dspb_typ_flow.setSingleStep(0.1)
#         # self._lyt_main.addWidget(self._dspb_typ_flow)
#
#         self._lbl_status = QLabel()
#         self._lyt_main.addWidget(self._lbl_status)
#
#         self._bar_progress = QProgressBar()
#         self._bar_progress.setRange(0, 100)
#         self._bar_progress.setTextVisible(True)
#         self._lyt_main.addWidget(self._bar_progress)
#
#         self._btn_manu_mode_on = QPushButton('Р.реж.')
#         self._lyt_main.addWidget(self._btn_manu_mode_on)
#
#         self._btn_manually_on = QPushButton('Вкл. в р.')
#         self._lyt_main.addWidget(self._btn_manually_on)
#
#         self.apply_updates(data)
#         self._on_update = on_update
#         self._on_delete = on_delete
#
#         self.setFixedSize(QSize(400, 50))