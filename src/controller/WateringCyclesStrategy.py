from PyQt5.QtCore import QTimer, QTime, QDate
# from enum import IntEnum
from src.store.store import ConnectedToStoreComponent
from src.utils.WateringStatuses import *


class WateringCyclesStates(Enum):
    PENDING = 0
    CHECKING = 1
    EXECUTION = 10
    ABORTING = 200
    RESETTING = 201


class WateringCyclesStrategy(ConnectedToStoreComponent):
    def __init__(self):
        ConnectedToStoreComponent.__init__(self)

        self._act_cycle = None
        self._curr_state = WateringCyclesStates.PENDING
        self._prev_state = WateringCyclesStates.PENDING
        self._prev_exec_time = QTime.currentTime()  # Нужно для точного единоразового назначения акт цикла

    def _on_timer_tick(self):
        cycles = self._get_store_state()['watering']['cycles']
        current = self._get_store_state()['watering']['current']
        # Текущее время - нужно во многих местах
        curr_time = QTime.currentTime()
        # Строка с временем и датой - нужна для сообщений в лог
        timestamp = f'{QDate.currentDate().toString("dd.MM.yy")} {curr_time.toString("hh:mm")}'

        # Автомат
        while True:
            self._again = False

            if self._curr_state is WateringCyclesStates.PENDING:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._prev_state = self._curr_state

                # Постоянные действия
                # отслеживаем, не пришло ли время след полива
                for ind_c, cycle in enumerate(cycles):
                    activation_time = QTime(cycle['hour'], cycle['minute'])
                    if cycle['enabled'] \
                            and (activation_time.msecsTo(curr_time) <= 0 and
                                 activation_time.msecsTo(self._prev_exec_time)) >= 0:
                        self._act_cycle = cycle
                        break

                self._prev_exec_time = curr_time

                # Переходы
                if self._act_cycle:
                    self._curr_state = WateringCyclesStates.CHECKING
                    self._again = True

            if self._curr_state is WateringCyclesStates.CHECKING:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._prev_state = self._curr_state

                # Переходы
                if not current['available']:
                    self._dispatch({'type': 'log/ERROR',
                                    'payload': f'{timestamp} Полив отменен, система полива недоступна'})
                    self._curr_state = WateringCyclesStates.PENDING
                    self._again = True

                elif current['feedback'] is ExecDevFeedbacks.BUSY:
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Полив отменен, система уже работает'})
                    self._curr_state = WateringCyclesStates.PENDING
                    self._again = True

                elif not self._act_cycle['enabled']:
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Полив отменен, т.к. цикл отключен'})
                    self._curr_state = WateringCyclesStates.PENDING
                    self._again = True

                else:
                    self._curr_state = WateringCyclesStates.EXECUTION
                    self._again = True

            if self._curr_state is WateringCyclesStates.EXECUTION:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Полив начат'})
                    self._dispatch({'type': 'wateringcycles/UPDATE_ITEM',
                                    'payload': {'ID': self._act_cycle['ID'],
                                                'new_data': {'status': WateringCycleStatuses.RUN}}})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'exec request': True}})
                    self._prev_state = self._curr_state

                # Переходы
                if not self._act_cycle['enabled']:
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Полив отменен, т.к. цикл отключен'})
                    self._curr_state = WateringCyclesStates.ABORTING
                    self._again = True
                elif not current['available']:
                    if current['feedback'] is ExecDevFeedbacks.ERROR:
                        self._dispatch({'type': 'log/INFO',
                                        'payload': f'{timestamp} Полив отменен, система полива недоступна'})
                    else:
                        self._dispatch({'type': 'log/INFO',
                                        'payload': f'{timestamp} Полив отменен, система полива неисправна'})
                    self._curr_state = WateringCyclesStates.RESETTING
                    self._again = True
                elif current['feedback'] is ExecDevFeedbacks.ABORTED:
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Полив отменен, отмена работы блока полива'})
                    self._curr_state = WateringCyclesStates.RESETTING
                    self._again = True
                elif current['feedback'] is ExecDevFeedbacks.DONE:
                    self._dispatch({'type': 'log/INFO',
                                    'payload': f'{timestamp} Полив завершен планово'})
                    self._curr_state = WateringCyclesStates.RESETTING
                    self._again = True

            if self._curr_state is WateringCyclesStates.ABORTING:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._dispatch({'type': 'wateringcycles/UPDATE_ITEM',
                                    'payload': {'ID': self._act_cycle['ID'],
                                                'new_data': {'status': WateringCycleStatuses.PENDING}}})
                    self._dispatch({'type': 'wateringcommon/UPDATE',
                                    'payload': {'abort': True}})
                    self._prev_state = self._curr_state

                # Переходы
                if current['feedback'] in [ExecDevFeedbacks.ABORTED, ExecDevFeedbacks.ERROR, ExecDevFeedbacks.DONE]\
                        or not current['available']:
                    # раз есть проверка current['available'], то можно было бы ExecDevFeedbacks.ERROR
                    # и не проверять
                    self._curr_state = WateringCyclesStates.PENDING
                    self._again = True

            if self._curr_state is WateringCyclesStates.RESETTING:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._dispatch({'type': 'wateringcycles/UPDATE_ITEM',
                                    'payload': {'ID': self._act_cycle['ID'],
                                                'new_data': {'status': WateringCycleStatuses.PENDING}}})
                    self._act_cycle = None
                    self._prev_state = self._curr_state

                # Переходы
                self._curr_state = WateringCyclesStates.PENDING
                self._again = True

            if not self._again:
                break
