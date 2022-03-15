from PyQt5.QtWidgets import QFrame, QGridLayout, QWidget

from src.features.Watering.widgets.WateringDuration import WateringDuration
from src.store.store import ConnectedToStoreComponent


def create_watering_duration(ID, data, on_update, parent):
    return WateringDuration(data=data,
                            on_update=lambda new_data: on_update(ID=ID, new_data=new_data),
                            parent=parent)


class WateringDurationTable(ConnectedToStoreComponent, QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        ConnectedToStoreComponent.__init__(self)

        # self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self._lyt_main = QGridLayout(self)
        self._lyt_main.setContentsMargins(0, 0, 0, 0)

        self._cached = self._get_store_state()['watering']['durations']
        self._children = [[None for j in range(len(self._cached[i]))] for i in range(len(self._cached))]

        for ind_c, item_c in enumerate(self._cached):
            for ind_z, item_z in enumerate(self._cached[ind_c]):
                # print(f'ind_c={ind_c}, ind_z={ind_z}')
                item = self._cached[ind_c][ind_z]
                self._children[ind_c][ind_z] = create_watering_duration(item['ID'], item, self._on_update_item, self)
                self._lyt_main.addWidget(self._children[ind_c][ind_z], ind_z, ind_c)
        # print(self._children)

    def _on_update_item(self, ID, new_data):
        self._dispatch({'type': 'wateringdurations/UPDATE_ITEM', 'payload': {'ID': ID, 'new_data': new_data}})

    def _updater(self):
        # print(f'old state = {self._cached}')
        new_state = self._get_store_state()["watering"]["durations"]
        if new_state is not self._cached:
            # print(f'{new_state}')
            # ---------------------добавились строка или строки-----------------------
            if len(new_state[0]) > len(self._cached[0]):  # достаточно сравнить первый столбец,
                # как минимум один столбец должен быть

                for ind_c, item_c in enumerate(new_state):
                    for ind_z, item_z in enumerate(new_state[ind_c]):
                        is_in_cach_state = False
                        for ind, item in enumerate(self._cached[ind_c]):
                            if item_z['ID'] == item['ID']:
                                is_in_cach_state = True
                        if not is_in_cach_state:
                            new_widget = create_watering_duration(item_z['ID'], item_z, self._on_update_item, self)
                            self._children[ind_c].insert(ind_z, new_widget)

                for ind_c, item_c in enumerate(self._children):
                    for ind_z, item_z in enumerate(self._children[ind_c]):
                        self._lyt_main.addWidget(self._children[ind_c][ind_z], ind_z, ind_c)

            # ------------------удалили строку или строки--------------------
            elif len(new_state[0]) < len(self._cached[0]):  # удалили строку или строки
                list_of_indexes_of_deleted_items = []
                for ind_c, item_c in enumerate(self._cached):
                    for ind_z, item_z in enumerate(self._cached[ind_c]):
                        is_in_new_state = False
                        for ind, item in enumerate(new_state[ind_c]):
                            if item_z['ID'] == item['ID']:
                                is_in_new_state = True
                        if not is_in_new_state:
                            list_of_indexes_of_deleted_items.append((ind_c, ind_z))
                for item in list_of_indexes_of_deleted_items:
                    self._lyt_main.removeWidget(self._children[item[0]][item[1]])
                    self._children[item[0]][item[1]].deleteLater()
                    self._children[item[0]].pop(item[1])
            # --------------добавился столбец или столбцы------------------------
            elif len(new_state) > len(self._cached):
                for ind_c, item_c in enumerate(new_state):
                    if item_c not in self._cached:
                        new_column = []
                        for item_z in item_c:
                            new_widget = create_watering_duration(item_z['ID'], item_z, self._on_update_item, self)
                            new_column.append(new_widget)
                        self._children.insert(ind_c, new_column)
                for ind_c, item_c in enumerate(self._children):
                    for ind_z, item_z in enumerate(self._children[ind_c]):
                        self._lyt_main.addWidget(self._children[ind_c][ind_z], ind_z, ind_c)
            # ----------------удалили столбец или столбцы---------------------
            elif len(new_state) < len(self._cached):
                list_of_indexes_of_deleted_columns = []
                for ind_c, item_c in enumerate(self._cached):
                    if item_c not in new_state:
                        list_of_indexes_of_deleted_columns.append(ind_c)
                for ind_c in list_of_indexes_of_deleted_columns:
                    for ind_z, _ in enumerate(self._children[0]):
                        self._lyt_main.removeWidget(self._children[ind_c][ind_z])
                        self._children[ind_c][ind_z].deleteLater()
                    self._children.pop(ind_c)
            # ----------------обновление значений в ячейке---------------------
            else:
                for ind_c, item_c in enumerate(self._cached):
                    for ind_z, item_z in enumerate(self._cached[ind_c]):
                        if item_z is not new_state[ind_c][ind_z]:
                            self._children[ind_c][ind_z].apply_updates(new_state[ind_c][ind_z])
            # в конце - перезапись кешированных свойств
            self._cached = new_state
