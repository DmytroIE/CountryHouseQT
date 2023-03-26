from PyQt5.QtCore import QTime, QDate
from src.utils.Timers import TON
from src.store.store import ConnectedToStoreComponent
from src.utils.WateringStatuses import *

SP_DEVIATION_DELAY = 10000  # in milliseconds


class WateringZoneStates(Enum):
    PENDING = 0
    CHECKING_AVAILABILITY = 1
    EXECUTION = 10
    ABORTING = 200
    DONE = 201
    ERROR = 202
    RESETTING = 203


class WateringZoneStrategy(ConnectedToStoreComponent):
    def __init__(self):
        ConnectedToStoreComponent.__init__(self)

        self._act_cycle = None
        self._curr_state = WateringZoneStates.PENDING
        self._prev_state = WateringZoneStates.PENDING
        self._deviation_timer = TON()

    def _on_timer_tick(self, ID, exec_time_secs):
        zone = self._get_store_state()['watering']['zones'][ID]
        current = self._get_store_state()['watering']['current']
        # Текущее время - нужно во многих местах
        curr_time = QTime.currentTime()
        # Строка с временем и датой - нужна для сообщений в лог
        timestamp = f'{QDate.currentDate().toString("dd.MM.yy")} {curr_time.toString("hh:mm")}'
        # actions_to_dispatch = {'wateringzones/UPDATE_ITEM': [],
        #                        'log/INFO': [],
        #                        'log/ERROR': []
        #                        }

        # Квитирование
        if zone['ackn']:
            if zone['error']:
                self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                'payload': {'ID': zone['ID'],
                                            'new_data': {'error': False, 'ackn': False}}})

        # Автомат
        while True:
            self._again = False

            if self._curr_state is WateringZoneStates.PENDING:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._prev_state = self._curr_state

                # Переходы
                self._curr_state = WateringZoneStates.CHECKING_AVAILABILITY
                self._again = True

            elif self._curr_state is WateringZoneStates.CHECKING_AVAILABILITY:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._prev_state = self._curr_state

                if zone['available']:
                    if not zone['enabled']:
                        self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                        'payload': {'ID': zone['ID'],
                                                    'new_data': {'available': False}}})
                else:
                    if zone['enabled'] and not zone['error']:
                        self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                        'payload': {'ID': zone['ID'],
                                                    'new_data': {'available': True}}})

                # Переходы
                if zone['available'] and zone['exec request']:  # and not zone['abort']:
                    self._curr_state = WateringZoneStates.EXECUTION
                    self._again = True
                else:
                    self._curr_state = WateringZoneStates.PENDING
                    self._again = False  # (!!!!!)

            elif self._curr_state is WateringZoneStates.EXECUTION:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                    'payload': {'ID': zone['ID'],
                                                'new_data': {'exec request': False,
                                                             'valve on': True,
                                                             'feedback': ExecDevFeedbacks.BUSY,
                                                             # 'status': WateringZoneStatuses.RUN,
                                                             'progress': 0.0}}})
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Полив зоны {zone["gpio_num"]} начат'})
                    self._time_of_finishing_zone = curr_time.addSecs(exec_time_secs)
                    self._state_entry_time = curr_time
                    self._deviation_timer.reset()
                    self._prev_state = self._curr_state

                # Постоянные действия
                seconds_left = curr_time.secsTo(self._time_of_finishing_zone)
                progress = (exec_time_secs - seconds_left) / exec_time_secs * 100.0
                self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                'payload': {'ID': zone['ID'],
                                            'new_data': {'progress': progress}}})

                deviation = abs(zone['typ_flow'] - current['flowrate']) / zone['typ_flow'] * 100.0
                self._deviation_timer.run(deviation > zone['deviation'], SP_DEVIATION_DELAY)

                # Переходы
                if not zone['enabled']:
                    self._curr_state = WateringZoneStates.ABORTING
                    self._again = True
                elif self._deviation_timer.out:
                    self._curr_state = WateringZoneStates.ERROR
                    self._again = True
                elif seconds_left < 0:
                    self._curr_state = WateringZoneStates.DONE
                    self._again = True

            elif self._curr_state is WateringZoneStates.ABORTING:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._dispatch({'type': 'log/WARNING',
                                    'payload':
                                        f'{timestamp} Полив зоны {zone["gpio_num"]} отменен'})
                    self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                    'payload': {'ID': zone['ID'],
                                                'new_data': {'available': False,
                                                             'feedback': ExecDevFeedbacks.ABORTED,
                                                             # 'status': WateringZoneStatuses.OFF,
                                                             }}})
                    self._prev_state = self._curr_state

                # Переходы
                self._curr_state = WateringZoneStates.RESETTING
                self._again = True

            elif self._curr_state is WateringZoneStates.ERROR:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._dispatch({'type': 'log/ERROR',
                                    'payload':
                                        f'{timestamp} Полив зоны {zone["gpio_num"]} отменен,'
                                        f' расход {current["flowrate"]:.1f} вне пределов'})
                    self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                    'payload': {'ID': zone['ID'],
                                                'new_data': {'available': False,
                                                             'error': True,
                                                             'feedback': ExecDevFeedbacks.ERROR,
                                                             # 'status': WateringZoneStatuses.FAULTY,
                                                             }}})
                    self._prev_state = self._curr_state

                # Переходы
                self._curr_state = WateringZoneStates.RESETTING
                self._again = True

            elif self._curr_state is WateringZoneStates.DONE:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._dispatch({'type': 'log/INFO',
                                    'payload':
                                        f'{timestamp} Полив зоны {zone["gpio_num"]} завершен'})
                    self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                    'payload': {'ID': zone['ID'],
                                                'new_data': {'feedback': ExecDevFeedbacks.DONE,
                                                             # 'status': WateringZoneStatuses.FAULTY,
                                                             }}})
                    self._prev_state = self._curr_state

                # Переходы
                self._curr_state = WateringZoneStates.RESETTING
                self._again = True

            elif self._curr_state is WateringZoneStates.RESETTING:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                    'payload': {'ID': zone['ID'],
                                                'new_data': {'valve on': False}}})
                    self._prev_state = self._curr_state

                # Переходы
                self._curr_state = WateringZoneStates.PENDING
                self._again = True

            if not self._again:
                break
