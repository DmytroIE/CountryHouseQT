from PyQt5.QtWidgets import QFrame, QGridLayout

from src.features.Watering.widgets.WateringDuration import WateringDuration
from src.store.store import ConnectedWithStoreComponent


class WateringDurationTable(ConnectedWithStoreComponent, QFrame):

    def __init__(self, store, parent=None):

        QFrame.__init__(self, parent)
        ConnectedWithStoreComponent.__init__(self)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self._lyt_main = QGridLayout(self)
        self._lyt_main.setContentsMargins(0, 0, 0, 0)

        self._wd11 = WateringDuration(self)
        self._wd12 = WateringDuration(self)
        self._wd13 = WateringDuration(self)
        self._wd21 = WateringDuration(self)
        self._wd22 = WateringDuration(self)
        self._wd23 = WateringDuration(self)
        self._wd31 = WateringDuration(self)
        self._wd32 = WateringDuration(self)
        self._wd33 = WateringDuration(self)

        self._lyt_main.addWidget(self._wd11, 0, 0)
        self._lyt_main.addWidget(self._wd12, 0, 1)
        self._lyt_main.addWidget(self._wd13, 0, 2)
        self._lyt_main.addWidget(self._wd21, 1, 0)
        self._lyt_main.addWidget(self._wd22, 1, 1)
        self._lyt_main.addWidget(self._wd23, 1, 2)
        self._lyt_main.addWidget(self._wd31, 2, 0)
        self._lyt_main.addWidget(self._wd32, 2, 1)
        self._lyt_main.addWidget(self._wd33, 2, 2)

    def _get_own_state(self):  # selector
        return self._get_store_state()['watering']['durations']

    def _updater(self):
        pass