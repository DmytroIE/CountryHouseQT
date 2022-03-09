from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget

from src.features.Watering.widgets.WateringZone import WateringZone
from src.store.store import ConnectedToStoreComponent


def create_watering_zone(ID, data, index, on_update, on_delete, parent):
    return WateringZone(data={**data, 'number': index + 1},
                        on_update=lambda new_data: on_update(ID=ID, new_data=new_data),
                        on_delete=lambda: on_delete(ID=ID),
                        parent=parent)


class WateringZoneList(ConnectedToStoreComponent, QWidget):

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)
        ConnectedToStoreComponent.__init__(self)

        # self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self._lyt_main = QVBoxLayout(self)
        self._lyt_main.setContentsMargins(0, 0, 0, 0)
        self._children = []

        self._updater()

    def _on_delete_item(self, ID):
        self._dispatch({'type': 'wateringzones/DELETE_ITEM', 'payload': ID})

    def _on_update_item(self, ID, new_data):
        self._dispatch({'type': 'wateringzones/UPDATE_ITEM', 'payload': {'ID': ID, 'new_data': new_data}})

    def _get_own_state(self):  # selector
        return self._get_store_state()['watering']['zones']

    def _on_state_update(self, new_state, list_, action):
        if action == 'ADD':
            # print('ADD')
            for ind, item in enumerate(list_):
                if isinstance(item, dict):
                    new_widget = create_watering_zone(
                        new_state[item['index_of_new_item']]['ID'],
                        new_state[item['index_of_new_item']],
                        ind,
                        self._on_update_item,
                        self._on_delete_item,
                        self)

                    #WateringZone({**new_state[item['index_of_new_item']], 'number': ind + 1}, self)
                    self._children.insert(item['index_of_new_item'], new_widget)
                else:
                    self._children[ind].apply_updates({'number': ind + 1})
            for ind2, item2 in enumerate(self._children):
                self._lyt_main.addWidget(item2)

        elif action == 'DELETE':
            for index_of_deleted_item in list_:
                self._lyt_main.removeWidget(self._children[index_of_deleted_item])
                self._children[index_of_deleted_item].deleteLater()
                self._children.pop(index_of_deleted_item)
            for ind, item in enumerate(self._children):
                item.apply_updates({'number': ind + 1})

        elif action == 'UPDATE':
            for ind, child in enumerate(self._children):
                if list_[ind] is not None:
                    self._children[ind].apply_updates(list_[ind])
