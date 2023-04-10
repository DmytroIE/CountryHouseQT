from PyQt5.QtWidgets import QVBoxLayout, QWidget
from collections import OrderedDict

from src.features.Watering.widgets.WateringZone import WateringZone
from src.store.store import ConnectedToStoreComponent


def create_watering_zone(data, on_update, parent):
    return WateringZone(data=data,
                        on_update=lambda ID, new_data: on_update(ID, new_data),
                        parent=parent)


class WateringZoneList(ConnectedToStoreComponent, QWidget):

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)
        ConnectedToStoreComponent.__init__(self)

        # self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self._lyt_main = QVBoxLayout(self)
        self._lyt_main.setContentsMargins(0, 0, 0, 0)
        self._children = OrderedDict({})

        self._updater()

    def _on_update_item(self, ID, new_data):
        self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                        'payload': {'ID': ID, 'new_data': new_data}})

    def _get_own_state(self):  # selector
        return self._get_store_state()['watering']['zones']

    def _on_state_update(self, new_state, list_of_ids, action):
        if action == 'ADD':
            for zone_id in list_of_ids:
                new_widget = create_watering_zone(
                    new_state[zone_id],
                    self._on_update_item,
                    self)
                self._children[zone_id] = new_widget

            for _, item in self._children.items():
                self._lyt_main.addWidget(item)

        elif action == 'UPDATE':
            for zone_id in list_of_ids:
                self._children[zone_id].apply_updates(new_state[zone_id])
