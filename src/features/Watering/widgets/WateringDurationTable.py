from PyQt5.QtWidgets import QFrame, QGridLayout, QWidget

from src.features.Watering.widgets.WateringDuration import WateringDuration
from src.store.store import ConnectedToStoreComponent


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
                self._children[ind_c][ind_z] = WateringDuration(item['duration'])
                self._lyt_main.addWidget(self._children[ind_c][ind_z], ind_z, ind_c)


    def _updater(self):
        # print(f'old state = {self._cached}')
        new_state = self._get_store_state()["watering"]["durations"]
        if new_state != self._cached:  # может, is not ??????????????????????????????????????????????????????????????????????
            # ---------------------добавились строка или строки-----------------------
            if len(new_state[0]) > len(self._cached[0]):  # достаточно сравнить первый столбец,
                                                          # как минимум один столбец должен быть
                #print('updater')
                # print(f'new_state = {new_state}')
                for ind_c, item_c in enumerate(new_state):
                    for ind_z, item_z in enumerate(new_state[ind_c]):

                         for ind, item in enumerate(self._cached[ind_c]):
                             if item_z['ID'] != item['ID']:
                                self._children[ind_c].insert(ind_z, WateringDuration(item_z['duration']))

                for ind_c, item_c in enumerate(new_state):
                    for ind_z, item_z in enumerate(new_state[ind_c]):
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


            # в конце - перезапись кешированных свойств
            self._cached = self._get_store_state()["watering"]["durations"]
