from PyQt5.QtWidgets import QFrame, QSpinBox, QVBoxLayout
from PyQt5.QtCore import Qt


class WateringDuration(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self._lyt_main = QVBoxLayout(self)

        self._spb_duration = QSpinBox(self)

        self._lyt_main.addWidget(self._spb_duration)
