from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt5.QtCore import QSize

from src.utils.WateringStatuses import *

# {'ID': 'LZliGv4F', 'typ_flow': 1.2, 'gpio_num': 13, 'enabled': False, 'status': PENDING, 'progress': 0.0,
#     'manu_mode_on': False, 'manually_on': False}


class WateringZone(QFrame):

    def __init__(self, data, parent=None):
        super().__init__(parent)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self._cached = {}

        self._lyt_main = QHBoxLayout(self)

        self._lbl_name = QLabel('Зона 1')
        self._lyt_main.addWidget(self._lbl_name)

        self._lbl_typ_flow = QLabel('1.2')
        self._lbl_typ_flow.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self._lyt_main.addWidget(self._lbl_typ_flow)

        self._lbl_status = QLabel('Ожидание')
        self._lyt_main.addWidget(self._lbl_status)

        self._bar_progress = QProgressBar()
        self._bar_progress.setRange(0, 100)
        self._bar_progress.setValue(24)
        self._lyt_main.addWidget(self._bar_progress)

        self._btn_manu_mode_on = QPushButton('Руч.реж.')
        self._lyt_main.addWidget(self._btn_manu_mode_on)

        self._btn_manually_on = QPushButton('Вкл. в руч.')
        self._lyt_main.addWidget(self._btn_manually_on)

        self.apply_updates(data)
        # self.setMinimumSize(self.sizeHint())
        self.setFixedSize(QSize(400, 50))
        # self.setFixedHeight(50)
        # self.setFixedWidth(400)

    def apply_updates(self, part_data):
        new_data = {**self._cached, **part_data}
        if new_data != self._cached:
            if 'number' in part_data:
                self._lbl_name.setText(f'Зона {part_data["number"]}')
            if 'typ_flow' in part_data:
                self._lbl_typ_flow.setText(f'{part_data["typ_flow"]}')
            if 'status' in part_data:
                self._lbl_status.setText(f'{statuses[part_data["status"]]}')
            if 'progress' in part_data:
                self._bar_progress.setValue(int(part_data["progress"]))
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
