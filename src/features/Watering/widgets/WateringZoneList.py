from PyQt5.QtWidgets import QFrame, QVBoxLayout

from src.features.Watering.widgets.WateringZone import WateringZone
from src.store.store import ConnectedToStoreComponent


class WateringZoneList(ConnectedToStoreComponent, QFrame):

    def __init__(self, parent=None):

        QFrame.__init__(self, parent)
        ConnectedToStoreComponent.__init__(self)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self._lyt_main = QVBoxLayout(self)
        self._lyt_main.setContentsMargins(0, 0, 0, 0)
        self._children = []
        # self._wz1 = WateringZone()
        # self._wz2 = WateringZone()
        # self._wz3 = WateringZone()
        #
        # self._lyt_main.addWidget(self._wz1)
        # self._lyt_main.addWidget(self._wz2)
        # self._lyt_main.addWidget(self._wz3)
        self._updater()
        # Для проверки, как работает вставка виджета на основании экшна wateringzones/ADD_ITEM
        # self._dispatch({'type': 'wateringzones/ADD_ITEM', 'payload': {'index': 1,
        #                                                               'new_item': {'ID': 'LZliGv4F', 'typ_flow': 1.3,
        #                                                                            'gpio_num': 13, 'enabled': False,
        #                                                                            'status': 1, 'progress': 0.0,
        #                                                                            'manu_mode_on': True,
        #                                                                            'manually_on': True}}})

    def _get_own_state(self):  # selector
        return self._get_store_state()['watering']['zones']

    def _on_state_update(self, new_state, list_, action):
        if action == 'ADD':
            # print('ADD')
            for ind, item in enumerate(list_):
                if isinstance(item, dict):
                    new_widget = WateringZone({**new_state[item['index_of_new_item']], 'number': ind + 1}, self)
                    self._children.insert(item['index_of_new_item'], new_widget)
                else:
                    self._children[ind].apply_updates({'number': ind+1})
            for ind2, item2 in enumerate(self._children):
                self._lyt_main.addWidget(item2)

            # self._dispatch()

        elif action == 'DELETE':
            pass
            # for index_of_deleted_item in list_:
            #     self._children[index_of_deleted_item].destroy()
            #     self._children.pop(index_of_deleted_item)

        elif action == 'UPDATE':
            for ind, child in enumerate(self._children):
                if list_[ind] is not None:
                    self._children[ind].apply_updates(list_[ind])
