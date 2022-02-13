from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QTimeEdit
from PyQt5.QtCore import QSize


class WateringCycle(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self._lyt_main = QVBoxLayout(self)

        self._lbl_name = QLabel('Полив 1')
        self._lyt_main.addWidget(self._lbl_name)

        self._tm_time = QTimeEdit()
        self._lyt_main.addWidget(self._tm_time)

        # self.setMinimumSize(self.sizeHint())
        self.setFixedSize(QSize(90, 90))
