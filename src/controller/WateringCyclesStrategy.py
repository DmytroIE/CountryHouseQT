from PyQt5.QtCore import QTime, QDateTime
# from enum import IntEnum
from src.store.store import ConnectedToStoreComponent
from src.utils.WateringStatuses import *


def watering_cycle_strategy(cycle, cycles, watering):
    cycle_id = cycle['ID']
    ackn = cycle['ackn']
    curr_state = cycle['curr state']
    prev_state = cycle['prev state']
    prev_time = cycle['prev time']
    enabled = cycle['enabled']
    available = cycle['available']
    active = cycle['active']
    hour = cycle['hour']
    minute = cycle['minute']

    watering_outputs = {'act cycle': watering['act cycle']}

    alarm_log_batch = []

    curr_time = QTime.currentTime()

    # Автомат
    while True:
        again = False

        if curr_state is CycleStates.CHECK_AVAILABILITY:
            # Этот шаг исполняется один раз
            any_other_active_cycle = False
            for c_id, c in cycles:
                if c is not cycle:
                    if c['active']:
                        no_other_active_cycle = True

            if not enabled or \
                    not watering['available'] or \
                    any_other_active_cycle or \
                    watering['feedback'] is not ExecDevFeedbacks.FINISHED:
                available = False
            else:
                available = True

            # Переходы
            curr_state = prev_state
            again = True

        elif curr_state is ZoneStates.CHECK_IF_DEVICES_STOPPED:
            # Здесь этот шаг просто для проформы, чтобы все было единообразно
            curr_state = ZoneStates.CHECK_IF_DEVICES_RUNNING
            again = True

        elif curr_state is ZoneStates.CHECK_IF_DEVICES_RUNNING:
            # Здесь этот шаг просто для проформы, чтобы все было единообразно
            curr_state = ZoneStates.CHECK_AVAILABILITY
            again = False

        elif curr_state is CycleStates.STANDBY:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                prev_state = curr_state

            activation_time = QTime(hour, minute)

            # Переходы
            if (activation_time.msecsTo(curr_time) <= 0 and
                     activation_time.msecsTo(prev_time)) >= 0:
                if available:
                    curr_state = CycleStates.EXECUTE
                    again = True
                else:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': QDateTime.currentDateTime(),
                                            'text': f'Полив {hour}:{minute} отменен'})

            else:
                curr_state = ZoneStates.CHECK_IF_DEVICES_STOPPED
                again = True

        if curr_state is CycleStates.EXECUTE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив {hour}:{minute} начат'})
                watering_outputs['act cycle'] = cycle
                active = True
                prev_state = curr_state

            # Переходы
            if watering['feedback'] is ExecDevFeedbacks.DONE:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив {hour}:{minute} выполнен'})
                curr_state = CycleStates.SHUTDOWN
                again = True
            elif not available or \
                    watering['feedback'] is ExecDevFeedbacks.ABORTED:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив {hour}:{minute} отменен'})
                curr_state = CycleStates.SHUTDOWN
                again = True
            else:
                curr_state = CycleStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is CycleStates.SHUTDOWN:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                watering_outputs['act cycle'] = None
                active = False
                prev_state = curr_state

            # Переходы
            curr_state = ZoneStates.STANDBY
            again = True

        if not again:
            break

        prev_time = curr_time