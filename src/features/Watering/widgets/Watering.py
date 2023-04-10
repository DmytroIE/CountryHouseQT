from PyQt5.QtWidgets import QFrame, QGridLayout, QWidget, QLayout

# from src.features.Watering.widgets.WateringAddItem import WateringAddItem
from src.features.Watering.widgets.WateringZoneList import WateringZoneList
from src.features.Watering.widgets.WateringCycleList import WateringCycleList
from src.features.Watering.widgets.WateringDurationTable import WateringDurationTable
from src.features.Watering.widgets.WateringCurrState import WateringCurrState

from src.store.ConnectedComponent import ConnectedComponent
from src.store.store import ConnectedToStoreComponent


class Watering(QWidget):

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)

        # self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self._lyt_main = QGridLayout(self)

        self._frm_curr_state = WateringCurrState(self)
        self._frm_zones = WateringZoneList()
        self._frm_cycles = WateringCycleList(self)
        self._frm_durations = WateringDurationTable(self)

        self._lyt_main.addWidget(self._frm_curr_state, 0, 0)
        self._lyt_main.addWidget(self._frm_zones, 1, 0)
        self._lyt_main.addWidget(self._frm_cycles, 0, 1)
        self._lyt_main.addWidget(self._frm_durations, 1, 1)

        self._lyt_main.setSizeConstraint(QLayout.SetFixedSize)
        # https://stackoverflow.com/questions/14980620/qt-layout-resize-to-minimum-after-widget-size-changes



