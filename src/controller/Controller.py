from PyQt5.QtCore import QTimer, QTime

from src.store.store import ConnectedToStoreComponent
from src.controller.GpioBoard import GpioBoard

from src.utils.WateringStatuses import *


class Controller(ConnectedToStoreComponent):
    def __init__(self):
        ConnectedToStoreComponent.__init__(self)
        self._gpio = GpioBoard(None)
        self._watering_started = False
        self._watering_step = 0
        self._watering_zone_on_index = 0
        self._watering_cycle_on_index = 0
        self._time_of_finishing_runout = 0
        self._time_of_finishing_zone = 0

        self._one_second_timer = QTimer()
        self._one_second_timer.timeout.connect(self._on_timer_tick)
        self._one_second_timer.start(1000)

    def _on_timer_tick(self):
        # в этой функции будут вызываться "протяженные во времени" алгоритмы, которые обновляют с периодичностью (в
        # нашем случае 1 сек) данные в виджетах. Функции. вызываемые здесь, сами берут данные из store, а также сами
        # диспатчат сообщения. События, на которые нужно реагировать сразу (и контроллеру, и интерфейсной части,
        # например, замкнуть реле пускателя по нажатию софт-кнопки), будут обрабатываться в функциях, которые не
        # "крутятся" в этом цикле. В частности, для обработки таких событий в контроллере используем _updater
        self._update_flowrate_reading()
        self._watering()
        pass

    def _watering(self):
        cycles = self._get_store_state()['watering']['cycles']
        zones = self._get_store_state()['watering']['zones']
        durations = self._get_store_state()['watering']['durations']
        # если есть хотя бы одна зона, включенная в ручном режиме, то плановый полив отменяется,
        # потому что нельзя два клапана открыть одновременно

        curr_time = QTime.currentTime()

        if self._watering_step == 0:
            # переходы
            for ind_c, cycle in enumerate(cycles):
                if cycle.get('enabled') \
                        and cycle.get('hour') == curr_time.hour() \
                        and cycle.get('minute') == curr_time.minute():

                    for ind_z, zone in enumerate(zones):
                        if zone['enabled'] and not zone['on']:
                            self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                            'payload': {'ID': zone.get('ID'),
                                                        'new_data': {'on': True, 'status': IN_WORK}}})
                            self._gpio.open_watering_valve(zone.get('ID'), True)
                            self._watering_zone_on_index = ind_z
                            self._time_of_finishing_zone = \
                                QTime.currentTime().addSecs(
                                    durations[self._watering_cycle_on_index][self._watering_zone_on_index].get(
                                        'duration') * 60)
                            self._dispatch({'type': 'wateringcycles/UPDATE_ITEM',
                                            'payload': {'ID': cycle.get('ID'),
                                                        'new_data': {'on': True}}})
                            self._watering_cycle_on_index = ind_c
                            self._gpio.open_ball_valve(True)
                            self._gpio.open_watering_valve(zone.get('ID'), True)
                            self._watering_step = 1
                            print('Step1')
                            break

        elif self._watering_step == 1:
            duration_in_secs = durations[self._watering_cycle_on_index][self._watering_zone_on_index].get(
                'duration') * 60
            seconds_left = curr_time.secsTo(self._time_of_finishing_zone)
            progress = (duration_in_secs - seconds_left) / duration_in_secs * 100.0
            self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                            'payload': {'ID': zones[self._watering_zone_on_index].get('ID'),
                                        'new_data': {'progress': progress}}})
            # переходы
            if seconds_left <= 0:
                next_watering_zone_on_index = -1
                for ind_z, zone in enumerate(zones):
                    if zone['enabled'] and ind_z > self._watering_zone_on_index:
                        next_watering_zone_on_index = ind_z
                        break
                if next_watering_zone_on_index >= 0:
                    self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                    'payload': {'ID': zones[self._watering_zone_on_index]['ID'],
                                                'new_data': {'on': False, 'status': PENDING}}})
                    self._gpio.open_watering_valve(zones[self._watering_zone_on_index]['ID'], False)
                    self._watering_zone_on_index = next_watering_zone_on_index
                    self._watering_step = 2
                    print('Step2')
                else:
                    # иначе не закрываем последний клапан, закрываем шаровый и сбрасываем давление 60 сек
                    self._gpio.open_ball_valve(False)
                    self._time_of_finishing_runout = curr_time.addSecs(60)
                    self._watering_step = 3  # сбрасываем давление
                    print('Step3')
        elif self._watering_step == 2:  # задержка 1 сек между переключениями клапанов
            self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                            'payload': {'ID': zones[self._watering_zone_on_index]['ID'],
                                        'new_data': {'on': True, 'status': IN_WORK}}})
            self._gpio.open_watering_valve(zones[self._watering_zone_on_index]['ID'], True)
            self._time_of_finishing_zone = \
                QTime.currentTime().addSecs(
                    durations[self._watering_cycle_on_index][self._watering_zone_on_index].get(
                        'duration') * 60)
            self._watering_step = 1
            print('Step1')
        elif self._watering_step == 3:
            seconds_left = curr_time.secsTo(self._time_of_finishing_runout)
            if seconds_left <= 0:
                self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                'payload': {'ID': zones[self._watering_zone_on_index]['ID'],
                                            'new_data': {'on': False, 'status': PENDING}}})
                self._gpio.open_watering_valve(zones[self._watering_zone_on_index]['ID'], False)
                self._watering_zone_on_index = 0
                self._watering_step = 0
                print('Step0')
        else:
            self._watering_step = 0

    def _update_flowrate_reading(self):
        pass

    def _updater(self):
        # print(self._get_store_state())
        pass
