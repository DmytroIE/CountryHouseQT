from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt5.QtCore import QSize


class WateringZone(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

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

        # self.setMinimumSize(self.sizeHint())
        self.setFixedSize(QSize(400, 50))
        # self.setFixedHeight(50)
        # self.setFixedWidth(400)



