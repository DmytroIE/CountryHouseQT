from PyQt5.QtCore import QTime, QDate
from src.utils.Timers import TON
from src.store.store import ConnectedToStoreComponent
from src.utils.WateringStatuses import *

SP_DEVIATION_DELAY = 10  # in seconds


class WateringZoneStates(Enum):
    PENDING = 0
    CHECKING_AVAILABILITY = 1
    EXECUTION = 10
    ABORTING = 200
    DONE = 201
    ERROR = 202
    RESETTING = 203


class ZoneAlarmMessages(Enum):
    FLOW_OUT_OF_LIMITS = {'ID': 'zone-xxL6hn91Q', 'text': 'Авария контактора насоса'}


def watering_zone_strategy(zone):

    ackn = zone['ackn']
    error = zone['error']
    feedback = zone['feedback']
    enabled = zone['enabled']
    exec_request = zone['exec request']
    exec_duration = zone['exec duration']
    available = zone['available']
    zone_on = zone['zone on']
    curr_flowrate = zone['curr flowrate']
    typ_flowrate = zone['typ flowrate']
    deviation = zone['deviation']
    name = zone['name']

    curr_state = zone['curr state']
    prev_state = zone['prev state']
    state_entry_time = zone['state entry time']
    timer_init_time = zone['timer init time']
    time_of_finishing_zone = zone['time of finishing act zone']
    progress = zone['progress']
    alarm_log_batch = []
    curr_error = None
    curr_time = None

    # Квитирование
    if ackn:
        if error:
            error = False
            ackn = False

    # Автомат
    while True:
        again = False

        if curr_state is WateringZoneStates.PENDING:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                prev_state = curr_state

            # Переходы
            curr_state = WateringZoneStates.CHECKING_AVAILABILITY
            again = True

        elif curr_state is WateringZoneStates.CHECKING_AVAILABILITY:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                prev_state = curr_state

            if available:
                if not enabled:
                    available = False
            else:
                if enabled and not error:
                    available = True

            # Переходы
            if available and exec_request:  # and not zone['abort']:
                curr_state = WateringZoneStates.EXECUTION
                again = True
            else:
                curr_state = WateringZoneStates.PENDING
                again = False  # (!!!!! обязательно, иначе бесконечный цикл)

        elif curr_state is WateringZoneStates.EXECUTION:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                curr_time = QDate.currentDate()
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': curr_time,
                                        'text': f'Полив зоны {zone["name"]} начат'})
                exec_request = False
                zone_on = True
                feedback = ExecDevFeedbacks.BUSY
                progress = 0.0

                time_of_finishing_zone = curr_time.addSecs(exec_duration)
                state_entry_time = curr_time
                timer_init_time = None
                prev_state = curr_state

            # Постоянные действия
            curr_time = QTime.currentTime()
            # Вычисляем нужные переменные
            seconds_left = curr_time.secsTo(time_of_finishing_zone)
            progress = (exec_duration - seconds_left) / exec_duration * 100.0
            curr_deviation = abs(typ_flowrate - curr_flowrate) / typ_flowrate * 100.0
            # Timer
            if curr_deviation > deviation:
                if not timer_init_time:
                    timer_init_time = curr_time
            else:
                if timer_init_time and curr_deviation < deviation:
                    timer_init_time = None

            # Переходы
            if not enabled:
                curr_state = WateringZoneStates.ABORTING
                again = True
            elif timer_init_time and curr_deviation >= deviation:
                curr_state = WateringZoneStates.ERROR
                again = True
            elif seconds_left < 0:
                curr_state = WateringZoneStates.DONE
                again = True

        elif curr_state is WateringZoneStates.ABORTING:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDate.currentDate(),
                                        'text': f'Полив зоны {name} отменен'})
                available = False
                feedback = ExecDevFeedbacks.ABORTED
                # status = WateringZoneStatuses.OFF
                prev_state = curr_state

            # Переходы
            curr_state = WateringZoneStates.RESETTING
            again = True

        elif curr_state is WateringZoneStates.ERROR:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                dispatch({'type': 'log/ERROR',
                                'payload':
                                    f'{timestamp} Полив зоны {zone["gpio_num"]} отменен,'
                                    f' расход {current["flowrate"]:.1f} вне пределов'})
                dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                'payload': {'ID': zone['ID'],
                                            'new_data': {'available': False,
                                                         'error': True,
                                                         'feedback': ExecDevFeedbacks.ERROR,
                                                         # 'status': WateringZoneStatuses.FAULTY,
                                                         }}})
                prev_state = curr_state

            # Переходы
            curr_state = WateringZoneStates.RESETTING
            again = True

        elif curr_state is WateringZoneStates.DONE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                dispatch({'type': 'log/INFO',
                                'payload':
                                    f'{timestamp} Полив зоны {zone["gpio_num"]} завершен'})
                dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                'payload': {'ID': zone['ID'],
                                            'new_data': {'feedback': ExecDevFeedbacks.DONE,
                                                         # 'status': WateringZoneStatuses.FAULTY,
                                                         }}})
                prev_state = curr_state

            # Переходы
            curr_state = WateringZoneStates.RESETTING
            again = True

        elif curr_state is WateringZoneStates.RESETTING:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                'payload': {'ID': zone['ID'],
                                            'new_data': {'valve on': False}}})
                prev_state = curr_state

            # Переходы
            curr_state = WateringZoneStates.PENDING
            again = True

        if not again:
            break
