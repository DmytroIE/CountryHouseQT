from PyQt5.QtWidgets import QFrame, QGridLayout

from src.features.Watering.widgets.WateringZone import WateringZone
from src.features.Watering.widgets.WateringCycle import WateringCycle
from src.features.Watering.widgets.WateringDuration import WateringDuration
from src.features.Watering.widgets.WateringCurrState import WateringCurrState

from src.store.ConnectedComponent import ConnectedComponent


class Watering(ConnectedComponent, QFrame):

    def __init__(self, store, parent=None,):

        QFrame.__init__(self, parent)
        ConnectedComponent.__init__(self, store)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self._lyt_main = QGridLayout(self)

        self._wz1 = WateringZone(self)
        self._wz2 = WateringZone(self)
        self._wz3 = WateringZone(self)

        self._wc1 = WateringCycle(self)
        self._wc2 = WateringCycle(self)
        self._wc3 = WateringCycle(self)
        # self._wc4 = WateringCycle(self)

        self._wd11 = WateringDuration(self)
        self._wd12 = WateringDuration(self)
        self._wd13 = WateringDuration(self)
        self._wd21 = WateringDuration(self)
        self._wd22 = WateringDuration(self)
        self._wd23 = WateringDuration(self)
        self._wd31 = WateringDuration(self)
        self._wd32 = WateringDuration(self)
        self._wd33 = WateringDuration(self)

        self._wcs = WateringCurrState(self)

        self._lyt_main.addWidget(self._wcs, 0, 0)
        self._lyt_main.addWidget(self._wz1, 1, 0)
        self._lyt_main.addWidget(self._wz2, 2, 0)
        self._lyt_main.addWidget(self._wz3, 3, 0)
        self._lyt_main.addWidget(self._wc1, 0, 1)
        self._lyt_main.addWidget(self._wc2, 0, 2)
        self._lyt_main.addWidget(self._wc3, 0, 3)
        # self._layout.addWidget(self._wc4, 0, 4)

        self._lyt_main.addWidget(self._wd11, 1, 1)
        self._lyt_main.addWidget(self._wd12, 1, 2)
        self._lyt_main.addWidget(self._wd13, 1, 3)
        self._lyt_main.addWidget(self._wd21, 2, 1)
        self._lyt_main.addWidget(self._wd22, 2, 2)
        self._lyt_main.addWidget(self._wd23, 2, 3)
        self._lyt_main.addWidget(self._wd31, 3, 1)
        self._lyt_main.addWidget(self._wd32, 3, 2)
        self._lyt_main.addWidget(self._wd33, 3, 3)

        # self._layout.setVerticalSpacing(1)
        # self.setMinimumSize(self.sizeHint())

    def _get_own_state(self):  # selector
        return self._get_store_state()['watering']

    def _updater(self):
        pass



