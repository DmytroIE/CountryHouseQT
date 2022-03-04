from PyQt5.QtWidgets import QFrame, QHBoxLayout

from src.features.Watering.widgets.WateringCycle import WateringCycle
from src.store.store import ConnectedToStoreComponent


class WateringCycleList(ConnectedToStoreComponent, QFrame):

    def __init__(self, store, parent=None):

        QFrame.__init__(self, parent)
        ConnectedToStoreComponent.__init__(self)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self._lyt_main = QHBoxLayout(self)
        self._lyt_main.setContentsMargins(0, 0, 0, 0)

        self._wc1 = WateringCycle(self)
        self._wc2 = WateringCycle(self)
        self._wc3 = WateringCycle(self)

        self._lyt_main.addWidget(self._wc1)
        self._lyt_main.addWidget(self._wc2)
        self._lyt_main.addWidget(self._wc3)

    def _get_own_state(self):  # selector
        return self._get_store_state()['watering']['cycles']

    def _updater(self):
        pass