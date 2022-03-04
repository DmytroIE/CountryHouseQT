from PyQt5.QtWidgets import QFrame, QGridLayout

from src.features.Watering.widgets.WateringDuration import WateringDuration
from src.store.store import ConnectedToStoreComponent




class WateringDurationTable(ConnectedToStoreComponent, QFrame):

    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        ConnectedToStoreComponent.__init__(self)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self._lyt_main = QGridLayout(self)
        self._lyt_main.setContentsMargins(0, 0, 0, 0)

        self._cached = self._get_store_state()['watering']['durations']
        self._children = [[None for j in range(len(self._cached[i]))] for i in range(len(self._cached))]
        for ind_c, item_c in enumerate(self._cached):
            for ind_z, item_z in enumerate(self._cached[ind_c]):
                # print(f'ind_c={ind_c}, ind_z={ind_z}')
                item = self._cached[ind_c][ind_z]
                self._children[ind_c][ind_z] = WateringDuration(item)
                self._lyt_main.addWidget(self._children[ind_c][ind_z], ind_z, ind_c)

        #  # к этому моменту уже должны существовать данные в store, касающиеся zones и cycles
        # zones = self._get_store_state()['watering']['zones']
        # cycles = self._get_store_state()['watering']['cycles']
        # # self._children = [[WateringDuration(DEFAULT_DURATION, self) for i in range(len(zones))]
        # #                                                             for j in range(len(cycles))]
        # self._children = [[None for i in range(len(zones))] for j in
        #                   range(len(cycles))]
        # self._cached = self._get_store_state()['watering']['durations']
        # self._cached_zone_ids = [zones[i]['ID'] for i in range(len(zones))]
        # self._cached_cycle_ids = [cycles[i]['ID'] for i in range(len(cycles))]
        #
        # for ind_c, item_c in enumerate(cycles):
        #     for ind_z, item_z in enumerate(zones):
        #         key_tuple = (item_c['ID'], item_z["ID"])
        #         # проверяем, есть ли продолжительность для данной комбинации зоны и цикла (ведь данные в store
        #         # будут загружаться из файла и могут быть повреждены - перенести потом эту проверку в операцию загрузки
        #         # store из внешнего файла, чтобы в store изначально не было мусора
        #         # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #         # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #         # if key_tuple in own_state:
        #         #     self._children[ind_c][ind_z].apply_updates(own_state[key_tuple]['duration'])
        #         # else:
        #         #     self._cached[key_tuple] = {'ID': key_tuple, 'duration': DEFAULT_DURATION}
        #         self._children[ind_c][ind_z] = WateringDuration(self._cached[key_tuple]['duration'])
        #         self._lyt_main.addWidget(self._children[ind_c][ind_z], ind_z, ind_c)

    def _updater(self):
        # print(f'old state = {self._cached[0]}')
        new_state = self._get_store_state()["watering"]["durations"]
        if new_state[0] != self._cached[0]:  # достаточно сравнить первый столбец
            print('updater')
        self._cached = self._get_store_state()["watering"]["durations"]
        # pass
        # zones = self._get_store_state()['watering']['zones']
        # cycles = self._get_store_state()['watering']['cycles']
        #
        # diff_c = len(cycles) - len(self._cached_cycle_ids)
        # diff_z = len(zones) - len(self._cached_zone_ids)
        #
        # # добавление новой зоны (считаем, что за одно изменение store может добавиться только \
        # # одна зона или только один цикл
        # if diff_z > 0:
        #     ind_of_new_item = -1
        #     new_zone_id = ''
        #
        #     for ind_z, item_z in enumerate(zones):
        #         if item_z['ID'] not in self._cached_zone_ids:
        #             ind_of_new_item = ind_z
        #             new_zone_id = item_z['ID']
        #             break
        #     print(ind_of_new_item)
        #
        #     self._cached_zone_ids.insert(ind_of_new_item, new_zone_id)
