from PyQt5.QtWidgets import QGridLayout, QWidget
from collections import OrderedDict

from src.features.Watering.widgets.WateringDuration import WateringDuration
from src.store.store import ConnectedToStoreComponent


def create_watering_duration(data, on_update, parent):
    return WateringDuration(data=data,
                            on_update=lambda cycle_id, zone_id, new_data: on_update(cycle_id, zone_id, new_data),
                            parent=parent)


class WateringDurationTable(ConnectedToStoreComponent, QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        ConnectedToStoreComponent.__init__(self)

        # self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self._lyt_main = QGridLayout(self)
        self._lyt_main.setContentsMargins(0, 0, 0, 0)
        self._children = OrderedDict({})

        self._cached = self._get_store_state()["watering"]["durations"]

        self._children = OrderedDict({})
        ind_c = 0
        for cycle_id in self._cached:
            self._children[cycle_id] = OrderedDict({})
            ind_z = 0
            for zone_id in self._cached[cycle_id]:
                self._children[cycle_id][zone_id] = create_watering_duration(
                    self._cached[cycle_id][zone_id], self._on_update_item, self)
                self._lyt_main.addWidget(self._children[cycle_id][zone_id], ind_z, ind_c)
                ind_z += 1
            ind_c += 1

    def _on_update_item(self, cycle_id, zone_id, new_data):
        self._dispatch({'type': 'wateringdurations/UPDATE_ITEM',
                        'payload': {'cycle_id': cycle_id,
                                    'zone_id': zone_id,
                                    'new_data': new_data}})

    def _updater(self):
        new_state = self._get_store_state()["watering"]["durations"]
        if new_state is not self._cached:
            # ----------------обновление значений в ячейке---------------------
            for cycle_id in self._cached:
                for zone_id in self._cached[cycle_id]:
                    if self._cached[cycle_id][zone_id] is not new_state[cycle_id][zone_id]:
                        self._children[cycle_id][zone_id].apply_updates(new_state[cycle_id][zone_id])

            self._cached = new_state
