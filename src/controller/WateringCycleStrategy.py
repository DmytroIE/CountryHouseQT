from PyQt5.QtCore import QTime, QDateTime
# from enum import IntEnum
from src.store.store import ConnectedToStoreComponent
from src.utils.WateringStatuses import *


def watering_cycle_strategy(cycle, cycles, process):
    cycle_id = cycle['ID']
    ackn = cycle['ackn']
    curr_state = cycle['curr state']
    prev_state = cycle['prev state']
    prev_time = cycle['prev time']
    enabled = cycle['enabled']
    active = cycle['active']
    hour = cycle['hour']
    minute = cycle['minute']
    status = cycle['status']

    process_outputs = {'act cycle ID': process['act cycle ID']}

    alarm_log_batch = []

    # Автомат
    while True:
        again = False

        if curr_state is CycleStates.STANDBY:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив {hour:02d}:{minute:02d} завершен'})
                prev_state = curr_state

            # Постоянные действия
            curr_time = QTime.currentTime()
            activation_time = QTime(hour, minute, 0, 0)
            if not prev_time:
                prev_time = curr_time

            # Переходы
            if (activation_time.msecsTo(curr_time) >= 0) and \
                    (activation_time.msecsTo(prev_time) <= 0):
                any_other_active_cycle = False
                for c_id, c in cycles.items():
                    if c is not cycle:
                        if c['active']:
                            any_other_active_cycle = True

                if not enabled or \
                        not process['available'] or \
                        process['error'] or \
                        any_other_active_cycle or \
                        (process['feedback'] is not ExecDevFeedbacks.FINISHED and process['act cycle ID']):
                    ready_to_execute = False
                else:
                    ready_to_execute = True

                if ready_to_execute:
                    curr_state = CycleStates.EXECUTE
                    again = True
                else:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': QDateTime.currentDateTime(),
                                            'text': f'Cycle:Полив {hour:02d}:{minute:02d} отменен'})
                    again = False
            else:
                again = False
            prev_time = curr_time

        if curr_state is CycleStates.EXECUTE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Cycle:Полив {hour:02d}:{minute:02d} начат'})
                process_outputs['act cycle ID'] = cycle_id
                active = True
                prev_state = curr_state

            # Переходы
            if process['feedback'] is ExecDevFeedbacks.DONE:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Cycle:Полив {hour:02d}:{minute:02d} выполнен'})
                curr_state = CycleStates.SHUTDOWN
                again = True
            elif not enabled or \
                    process['feedback'] is ExecDevFeedbacks.ABORTED:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Cycle:Полив {hour:02d}:{minute:02d} отменен'})
                curr_state = CycleStates.SHUTDOWN
                again = True

        elif curr_state is CycleStates.SHUTDOWN:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                process_outputs['act cycle ID'] = None
                prev_state = curr_state

            # Переходы
            if process['feedback'] is ExecDevFeedbacks.FINISHED:
                active = False
                curr_state = CycleStates.STANDBY
                again = True

        if not again:
            break

    # статусы
    if not enabled:
        status = OnOffDeviceStatuses.OFF
    elif prev_state is CycleStates.STANDBY:
        status = OnOffDeviceStatuses.STANDBY
    elif prev_state is CycleStates.EXECUTE:
        status = OnOffDeviceStatuses.RUN
    elif prev_state is CycleStates.SHUTDOWN:
        status = OnOffDeviceStatuses.SHUTDOWN

    # обновляем выходы
    cycle_outputs = {'ackn': ackn,
                     'active': active,
                     'curr state': curr_state,
                     'prev state': prev_state,
                     'prev time': prev_time,
                     'status': status
                     }
    return cycle_outputs, process_outputs, alarm_log_batch
