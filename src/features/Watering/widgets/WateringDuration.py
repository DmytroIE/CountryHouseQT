from PyQt5.QtWidgets import QFrame, QSpinBox, QVBoxLayout
from PyQt5.QtCore import Qt, QSize


class WateringDuration(QFrame):

    def __init__(self, data, on_update, parent=None):
        super().__init__(parent)
        self._cycle_id = data['cycle_id']
        self._zone_id = data['zone_id']
        self._cached_for_widget = {'duration': -1}
        self._create_ui(data, on_update)

    def _create_ui(self, data, on_update):

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self._lyt_main = QVBoxLayout(self)
        self._lyt_main.setContentsMargins(0, 0, 0, 0)

        self._spb_duration = QSpinBox(self)
        self._spb_duration.setSuffix(' мин')

        self.apply_updates(data)

        self._spb_duration.valueChanged.connect(
            lambda: on_update(self._cycle_id,
                              self._zone_id,
                              {'duration': self._spb_duration.value()}))

        self._lyt_main.addWidget(self._spb_duration)

    def apply_updates(self, new_data):
        changed = False
        if new_data['duration'] != self._cached_for_widget['duration']:
            self._spb_duration.setValue(new_data['duration'])
            changed = True

        if changed:
            for key in self._cached_for_widget:
                self._cached_for_widget[key] = new_data[key]

