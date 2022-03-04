from PyQt5.QtWidgets import QFrame, QSpinBox, QVBoxLayout
from PyQt5.QtCore import Qt


class WateringDuration(QFrame):

    def __init__(self, data, parent=None):
        super().__init__(parent)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self._lyt_main = QVBoxLayout(self)
        self._lyt_main.setContentsMargins(2, 2, 2, 2)

        self._spb_duration = QSpinBox(self)
        self._spb_duration.setValue(data)
        self._spb_duration.setSuffix(' мин')

        self._lyt_main.addWidget(self._spb_duration)

    def apply_updates(self, new_data):
        self._spb_duration.setValue(new_data)
