from PyQt5.QtWidgets import QFrame, QGridLayout

from src.features.Watering.widgets.WateringZoneList import WateringZoneList
from src.features.Watering.widgets.WateringCycleList import WateringCycleList
from src.features.Watering.widgets.WateringDurationTable import WateringDurationTable
from src.features.Watering.widgets.WateringCurrState import WateringCurrState

from src.store.ConnectedComponent import ConnectedComponent


class Watering(QFrame):

    def __init__(self, parent=None):

        QFrame.__init__(self, parent)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self._lyt_main = QGridLayout(self)

        self._frm_curr_state = WateringCurrState(self)
        self._frm_zones = WateringZoneList()
        self._frm_cycles = WateringCycleList(self)
        self._frm_durations = WateringDurationTable(self)

        self._lyt_main.addWidget(self._frm_curr_state, 0, 0)
        self._lyt_main.addWidget(self._frm_zones, 1, 0)
        self._lyt_main.addWidget(self._frm_cycles, 0, 1)
        self._lyt_main.addWidget(self._frm_durations, 1, 1)

        # self._layout.setVerticalSpacing(1)
        # self.setMinimumSize(self.sizeHint())



