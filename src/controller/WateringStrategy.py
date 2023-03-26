from PyQt5.QtCore import QTimer, QTime, QDate
# from enum import IntEnum
from src.store.store import ConnectedToStoreComponent
from src.utils.WateringStatuses import *







class WateringStates(IntEnum):
    PENDING = 0
    CHECKING_READYBILITY = 1
    CHECKING = 2
    START_PUMP = 100
    OPEN_BALL_VALVE = 101
    WATERING_ZONE = 10
    SWITCHING_ANOTHER_ZONE = 11
    RUNNING_OUT = 200


class WateringStrategy(ConnectedToStoreComponent):
    def __init__(self):
        ConnectedToStoreComponent.__init__(self)

        self._run_signal = False
        self._curr_state = WateringStates.PENDING
        self._prev_state = WateringStates.PENDING
        self._act_zone_index = 0
        self._act_cycle_index = 0
        self._act_zone = None
        self._act_cycle = None


        self._again = False

        # self._one_second_timer = QTimer()
        # self._one_second_timer.timeout.connect(self._on_timer_tick)
        # self._one_second_timer.start(1000)

    def _on_timer_tick(self):
        cycles = self._get_store_state()['watering']['cycles']
        zones = self._get_store_state()['watering']['zones']
        durations = self._get_store_state()['watering']['durations']
        current = self._get_store_state()['watering']['current']
        pump = self._get_store_state()['contactors']['pump']
        # Текущее время - нужно во многих местах
        curr_time = QTime.currentTime()
        # Строка с временем и датой - нужна для сообщений в лог
        timestamp = f'{QDate.currentDate().toString("dd.MM.yy")} {curr_time.toString("hh:mm")}'

        # Квитирование
        if current['ackn']:
            if not pump['available'] and pump['ackn']:






            # сбрасываем имп сигнал, блок его получил, принял к сведению
            self._dispatch({'type': 'wateringcommon/UPDATE',
                            'payload': {'ackn': False, 'available': True}})

        # Автомат
        while True:
            self._again = False
            if self._curr_state is WateringStates.PENDING:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    if pump['run request']:
                        self._dispatch({'type': 'pump/UPDATE',
                                        'payload': {'run request': False}})
                    if current['ball valve on']:
                        self._dispatch({'type': 'wateringcommon/UPDATE',
                                        'payload': {'ball valve on': False}})
                    if self._act_zone:
                        # Выключаем активную зону
                        self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                        'payload': {'ID': self._act_zone['ID'],
                                                    'new_data': {'on': False, 'status': WateringZoneStatuses.PENDING}}})
                        self._act_zone = None
                        self._act_zone_index = 0
                    self._prev_state = self._curr_state

                # Переходы
                self._curr_state = WateringStates.CHECKING_READYBILITY
                self._again = True

            elif self._curr_state is WateringStates.CHECKING_READYBILITY:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._prev_state = self._curr_state

                ready = False


                # Переходы
                if current['exec request'] and not current['abort']:
                    self._curr_state = WateringStates.CHECKING
                    self._again = True
                else:
                    self._curr_state = WateringStates.PENDING
                    self._again = False  # (!!!!!)

            elif self._curr_state is WateringStates.CHECKING:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    # сбрасываем имп сигнал, блок его получил, принял к сведению
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'exec request': False}})
                    self._prev_state = self._curr_state

                for ind_z, zone in enumerate(zones):
                    # обнуляем прогрессы перед следующим поливом
                    self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                    'payload': {'ID': zones[ind_z]['ID'],
                                                'new_data': {'progress': 0.0}}})
                    if zone['enabled']:
                        self._act_zone = zone
                        self._act_zone_index = ind_z

                # Переходы
                if not self._act_zone:
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Ни одна зона не включена'})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'feedback': ExecDevFeedbacks.ABORTED,
                                                'available': True}})
                    self._curr_state = WateringStates.PENDING
                    self._again = True
                elif not pump['available']:
                    self._dispatch({'type': 'log/ERROR',
                                    'payload': f'{timestamp} Полив отменен, насос недоступен'})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'feedback': ExecDevFeedbacks.ERROR,
                                                'available': False,
                                                'status': OnOffDeviceStatuses.FAULTY}})
                    self._curr_state = WateringStates.PENDING
                    self._again = True

                else:
                    self._curr_state = WateringStates.START_PUMP
                    self._again = True

            elif self._curr_state is WateringStates.START_PUMP:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._dispatch({'type': 'pump/UPDATE',
                                    'payload': {'run request': True}})
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Включение насоса'})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'status': WateringStatuses.STARTUP,
                                                'feedback': ExecDevFeedbacks.BUSY,
                                                }})
                    self._state_entry_time = curr_time
                    self._prev_state = self._curr_state

                # всегда проверяем, есть ли хотя бы одна зона в статусе Pending
                self._act_zone = None
                for ind_z, zone in enumerate(zones):
                    if zone['enabled']:
                        self._act_zone = zone
                        self._act_zone_index = ind_z

                # Переходы
                if not self._act_zone:
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Полив отменен, ни одна зона не включена'})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'feedback': ExecDevFeedbacks.ABORTED,
                                                'available': True}})
                    self._curr_state = WateringStates.PENDING
                    self._again = True
                elif pump['feedback'] is OnOffDevFeedbacks.NOT_RUN or not pump['available']:
                    self._dispatch({'type': 'log/ERROR',
                                    'payload': f'{timestamp} Полив отменен, насос недоступен'})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'feedback': ExecDevFeedbacks.ERROR,
                                                'available': False,
                                                'status': OnOffDeviceStatuses.FAULTY}})
                    self._curr_state = WateringStates.PENDING
                    self._again = True

                elif pump['feedback'] is OnOffDevFeedbacks.RUN and \
                        self._state_entry_time.secsTo(curr_time) > 10:
                    self._curr_state = WateringStates.OPEN_BALL_VALVE
                    self._again = True

            elif self._curr_state is WateringStates.OPEN_BALL_VALVE:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'ball valve on': True}})
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Открытие шарового крана'})
                    self._state_entry_time = curr_time
                    self._prev_state = self._curr_state

                # всегда проверяем, есть ли хотя бы одна зона в статусе Pending
                self._act_zone = None
                for ind_z, zone in enumerate(zones):
                    if zone['enabled']:
                        self._act_zone = zone
                        self._act_zone_index = ind_z

                # Переходы
                if not self._act_zone:
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Полив отменен, ни одна зона не включена'})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'feedback': ExecDevFeedbacks.ABORTED,
                                                'available': True}})
                    self._curr_state = WateringStates.RUNNING_OUT
                    self._again = True
                elif pump['feedback'] is OnOffDevFeedbacks.NOT_RUN or not pump['available']:
                    self._dispatch({'type': 'log/ERROR',
                                    'payload': f'{timestamp} Полив отменен, насос недоступен'})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'feedback': ExecDevFeedbacks.ERROR,
                                                'available': False,
                                                'status': OnOffDeviceStatuses.FAULTY}})
                    self._curr_state = WateringStates.RUNNING_OUT
                    self._again = True
                elif self._state_entry_time.secsTo(curr_time) > 10:
                    # для шарового крана нет фидбека, просто ждем 10 сек
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'status': WateringStatuses.RUN}})
                    self._curr_state = WateringStates.WATERING_ZONE
                    self._again = True

            elif self._curr_state is WateringStates.WATERING_ZONE:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                    'payload': {'ID': self._act_zone['ID'],
                                                'new_data': {'valve on': True,
                                                             'status': WateringZoneStatuses.RUN}}})
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Полив зоны {self._act_zone_index} начат'})
                    self._time_of_finishing_zone = curr_time.addSecs(
                        durations[self._act_cycle_index][self._act_zone_index]['duration'] * 60)
                    self._state_entry_time = curr_time
                    # Если уж мы попали в этот блок кода, то точно хотя бы одна акт зона у нас есть
                    # self._prev_act_zone = self._act_zone
                    # self._prev_act_zone_index = self._act_zone_index
                    self._prev_state = self._curr_state

                # Постоянные действия

                duration_in_secs = durations[self._act_cycle_index][self._act_zone_index]['duration'] * 60
                seconds_left = curr_time.secsTo(self._time_of_finishing_zone)
                progress = (duration_in_secs - seconds_left) / duration_in_secs * 100.0
                self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                'payload': {'ID': zones[self._act_zone_index]['ID'],
                                            'new_data': {'progress': progress}}})

                deviation = abs(self._act_zone['typ_flow'] - current['flowrate']) \
                            / self._act_zone['typ_flow'] * 100.0
                self._deviation_timer.run(deviation > self._act_zone['deviation'], SP_DEVIATION_DELAY)

                # всегда проверяем, есть ли хотя бы одна зона в статусе Pending
                self._act_zone = None
                for ind_z, zone in enumerate(zones):
                    if zone['enabled']:
                        self._act_zone = zone
                        self._act_zone_index = ind_z

                self._next_act_zone = None
                if self._act_zone:
                    for ind_z, zone in enumerate(zones[self._act_zone_index:]):
                        if zone['enabled']:
                            self._next_act_zone = zone
                            self._next_act_zone_index = ind_z

                # Переходы
                if not self._act_zone:
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Полив отменен, ни одна зона не включена'})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'feedback': ExecDevFeedbacks.ABORTED,
                                                'available': True}})
                    self._curr_state = WateringStates.RUNNING_OUT
                    self._again = True
                elif pump['feedback'] is OnOffDevFeedbacks.NOT_RUN or not pump['available']:
                    self._dispatch({'type': 'log/ERROR',
                                    'payload': f'{timestamp} Полив отменен, насос недоступен'})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'feedback': ExecDevFeedbacks.ERROR,
                                                'available': False,
                                                'status': OnOffDeviceStatuses.FAULTY}})
                    self._curr_state = WateringStates.RUNNING_OUT
                    self._again = True
                elif self._deviation_timer.out:
                    self._dispatch({'type': 'log/WARNING',
                                    'payload':
                                        f'{timestamp} Полив зоны отменен, расход {current["flowrate"]:.1f} вне пределов'})
                    if self._next_act_zone:
                        self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                        'payload': {'ID': self._act_zone['ID'],
                                                    'new_data': {'status': WateringZoneStatuses.FAULTY}}})
                        self._curr_state = WateringStates.SWITCHING_ANOTHER_ZONE
                        self._again = True
                    else:
                        self._curr_state = WateringStates.RUNNING_OUT
                        self._again = True
                elif seconds_left < 0:
                    if self._next_act_zone:
                        self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                        'payload': {'ID': self._act_zone['ID'],
                                                    'new_data': {'status': WateringZoneStatuses.PENDING}}})
                        self._curr_state = WateringStates.SWITCHING_ANOTHER_ZONE
                        self._again = True
                    else:
                        self._dispatch({'type': 'log/INFO',
                                        'payload': f'{timestamp} Полив зоны {self._act_zone_index} завершен'})
                        self._curr_state = WateringStates.RUNNING_OUT
                        self._again = True

            elif self._curr_state is WateringStates.SWITCHING_ANOTHER_ZONE:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                    'payload': {'ID': self._act_zone['ID'],
                                                'new_data': {'valve on': False}}})
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Полив зоны {self._act_zone_index} завершен'})
                    self._act_zone = None
                    self._state_entry_time = curr_time
                    self._prev_state = self._curr_state

                # Постоянные действия
                self._next_act_zone = None
                for ind_z, zone in enumerate(zones[self._act_zone_index:]):
                    if zone['enabled']:
                        self._next_act_zone = zone
                        self._next_act_zone_index = ind_z

                # Переходы
                if not self._next_act_zone:
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Полив отменен'})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'feedback': ExecDevFeedbacks.ABORTED,
                                                'available': True}})
                    self._curr_state = WateringStates.RUNNING_OUT
                    self._again = True
                elif pump['feedback'] is OnOffDevFeedbacks.NOT_RUN or not pump['available']:
                    self._dispatch({'type': 'log/ERROR',
                                    'payload': f'{timestamp} Полив отменен, насос недоступен'})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'feedback': ExecDevFeedbacks.ERROR,
                                                'available': False,
                                                'status': OnOffDeviceStatuses.FAULTY}})
                    self._curr_state = WateringStates.RUNNING_OUT
                    self._again = True
                elif self._state_entry_time.secsTo(curr_time) > 5:
                    self._act_zone = self._next_act_zone
                    self._act_zone_index = self._next_act_zone_index
                    self._curr_state = WateringStates.WATERING_ZONE
                    self._again = True

            elif self._curr_state is WateringStates.RUNNING_OUT:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:

                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Сброс давления'})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'ball valve on': False}})
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Закрытие шарового крана'})
                    self._dispatch({'type': 'pump/UPDATE',
                                    'payload': {'run request': False}})
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Выключение насоса'})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'status': WateringStatuses.SHUTDOWN}})
                    # если попали сюда из SWITCHING_ANOTHER_ZONE, когда клапан пред зоны уже закрылся,
                    # а следующему не дали открыться
                    if not self._act_zone:
                        # тогда просто назначим для сброса давления из доступных
                        for ind_z, zone in enumerate(zones):
                            if zone['enabled']:
                                self._act_zone = zone
                                self._act_zone_index = ind_z
                                self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                                'payload': {'ID': self._act_zone['ID'],
                                                            'new_data': {'valve on': True}}})
                                break

                    self._state_entry_time = curr_time
                    self._prev_state = self._curr_state

                # Переходы
                if self._state_entry_time.secsTo(curr_time) > 30:
                    self._curr_state = WateringStates.PENDING
                    self._again = True

            if not self._again:
                break
