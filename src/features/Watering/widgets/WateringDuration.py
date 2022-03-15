from PyQt5.QtWidgets import QFrame, QSpinBox, QVBoxLayout
from PyQt5.QtCore import Qt, QSize


class WateringDuration(QFrame):

    def __init__(self, data, on_update, parent=None):
        super().__init__(parent)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self._lyt_main = QVBoxLayout(self)
        self._lyt_main.setContentsMargins(0, 0, 0, 0)

        self._spb_duration = QSpinBox(self)
        self._spb_duration.setSuffix(' мин')

        self.apply_updates(data)

        self._spb_duration.valueChanged.connect(lambda: on_update(new_data={'duration': self._spb_duration.value()}))

        self._lyt_main.addWidget(self._spb_duration)

    def apply_updates(self, new_data):
        self._spb_duration.setValue(new_data['duration'])
