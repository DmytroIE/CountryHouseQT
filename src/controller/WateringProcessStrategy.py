from PyQt5.QtCore import QTime, QDateTime
from collections import OrderedDict
from src.utils.WateringStatuses import *

PRESSURE_RELIEF_DURATION = 1  # minutes


def watering_process_strategy(process, zones, pump, durations):
    process_id = process['ID']
    ackn = process['ackn']
    error = process['error']
    feedback = process['feedback']
    feedback_temp = process['feedback temp']
    available = process['available']
    ball_valve_on = process['ball valve on']
    act_cycle = process['act cycle']  # Вместо exec request, если не None, то это сигнал к запуску
    active_zone_id = ['active zone id']
    curr_state = process['curr state']
    prev_state = process['prev state']
    state_entry_time = process['state entry time']
    raised_errors = process['raised errors']
    raised_warnings = process['raised warnings']
    status = process['status']
    pump_outputs = {'run req from watering': pump['run req from watering']}

    zones_outputs = {}
    for zone_id, zone in zones.items():
        zones_outputs[zone_id] = {'exec request': zone['exec request'],
                                  'duration': zone['duration']}
    alarm_log_batch = []

    # Квитирование
    if ackn:
        if error:
            error_test = False
            for key, val in raised_errors.items():
                if key is WateringProcessErrorMessages.PUMP_NOT_RUNNING:
                    if val:
                        if pump['available']:
                            raised_errors[key] = False
                            alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_OUT,
                                                    'alarm ID': key,
                                                    'equip ID': process_id,
                                                    'dt_stamp': QDateTime.currentDateTime(),
                                                    'text': 'OUT:' + key.value})
                        else:
                            error_test = True
            error = error_test
        # проверяем все подчиненные устройства, обнулили ли они свои биты квитирования
        all_devices_acknowledged = True
        for zone in zones:
            if zone['ackn']:
                all_devices_acknowledged = False
        if pump['ackn']:
            all_devices_acknowledged = False
        if all_devices_acknowledged:
            ackn = False

    # Автомат
    while True:
        again = False

        if curr_state is WateringProcessStates.CHECK_AVAILABILITY:
            # Этот шаг исполняется один раз

            at_least_one_zone_available = True
            for zone in zones:
                at_least_one_zone_available = zone['available']

            if not at_least_one_zone_available \
                    or not pump['available']:
                available = False
            else:
                available = True

            # Переходы
            curr_state = prev_state
            again = True

        elif curr_state is WateringProcessStates.CHECK_IF_DEVICES_STOPPED:
            # Здесь этот шаг просто для проформы, чтобы все было единообразно
            # Переходы
            curr_state = WateringProcessStates.CHECK_IF_DEVICES_RUNNING
            again = True

        elif curr_state is WateringProcessStates.CHECK_IF_DEVICES_RUNNING:
            # Переходы
            error_test = False
            for key, val in raised_errors.items():
                if key is WateringProcessErrorMessages.PUMP_NOT_RUNNING:
                    if pump_outputs['run req from watering'] and \
                            pump['feedback for watering'] is EnableDevFeedbacks.NOT_RUN:
                        raised_errors[key] = True
                        alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_IN,
                                                'alarm ID': key,
                                                'equip ID': process_id,
                                                'dt_stamp': QDateTime.currentDateTime(),
                                                'text': 'IN:' + key.value})
                        error_test = True
            if error_test:
                error = True
                curr_state = prev_state
                again = True
            else:
                curr_state = ZoneStates.CHECK_AVAILABILITY
                again = False

        elif curr_state is WateringProcessStates.STANDBY:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив завершен'})
                prev_state = curr_state

            # Постоянные действия
            feedback = ExecDevFeedbacks.FINISHED

            # Переходы
            if available and act_cycle:
                curr_state = WateringProcessStates.START_PUMP
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.START_PUMP:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                pump_outputs['run req from watering'] = True
                feedback = ExecDevFeedbacks.BUSY
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Постоянные действия

            # Переходы
            if not available or not act_cycle:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив отменен при запуске'})
                feedback_temp = ExecDevFeedbacks.ABORTED
                curr_state = WateringProcessStates.STOP_PUMP
                again = True
            elif error:
                feedback_temp = ExecDevFeedbacks.ABORTED
                curr_state = WateringProcessStates.STOP_PUMP
                again = True
            elif pump['feedback for watering'] is EnableDevFeedbacks.RUN and \
                    state_entry_time.secsTo(QTime.currentTime()) > 5:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = WateringProcessStates.OPEN_BALL_VALVE
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.OPEN_BALL_VALVE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                ball_valve_on = True
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Постоянные действия

            # Переходы
            if not available or not act_cycle:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив отменен при запуске'})
                feedback_temp = ExecDevFeedbacks.ABORTED
                curr_state = WateringProcessStates.CLOSE_BALL_VALVE
                again = True
            elif error:
                feedback_temp = ExecDevFeedbacks.ABORTED
                curr_state = WateringProcessStates.CLOSE_BALL_VALVE
                again = True
            elif state_entry_time.secsTo(QTime.currentTime()) > 5:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = WateringProcessStates.WATER_ZONE
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.WATER_ZONE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                active_zone_id = None
                for zone_id, zone in zones:
                    if zone['available']:
                        if zone['feedback'] is ExecDevFeedbacks.FINISHED and not active_zone_id:
                            zones_outputs[zone_id]['exec request'] = True
                            zones_outputs[zone_id]['duration'] = durations[act_cycle['ID']][zone_id]
                            active_zone_id = zone_id
                            break
                prev_state = curr_state

            # Постоянные действия

            # Переходы
            if not active_zone_id:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив выполнен'})
                feedback_temp = ExecDevFeedbacks.DONE
                curr_state = WateringProcessStates.CLOSE_BALL_VALVE
                again = True
            elif not available or not act_cycle:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив отменен'})
                feedback_temp = ExecDevFeedbacks.ABORTED
                curr_state = WateringProcessStates.CLOSE_BALL_VALVE
                again = True
            elif error:
                feedback_temp = ExecDevFeedbacks.ABORTED
                curr_state = WateringProcessStates.CLOSE_BALL_VALVE
                again = True
            elif zones[active_zone_id]['feedback'] is ExecDevFeedbacks.DONE or \
                    zones[active_zone_id]['feedback'] is ExecDevFeedbacks.ABORTED:
                curr_state = WateringProcessStates.CHANGE_ZONE
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.CHANGE_ZONE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                state_entry_time = QTime.currentTime()
                prev_state = curr_state  # Нужно, чтобы опять прийти в WateringStates.WATER_ZONE и выполнить един дей

            # Постоянные действия

            # Переходы
            if not available or not act_cycle:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив отменен'})
                feedback_temp = ExecDevFeedbacks.ABORTED
                curr_state = WateringProcessStates.CLOSE_BALL_VALVE
                again = True
            elif error:
                feedback_temp = ExecDevFeedbacks.ABORTED
                curr_state = WateringProcessStates.CLOSE_BALL_VALVE
                again = True
            elif state_entry_time.secsTo(QTime.currentTime()) > 2:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = WateringProcessStates.WATER_ZONE
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.CLOSE_BALL_VALVE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                for zone_id, zone in zones:
                    zones_outputs[zone_id]['exec request'] = False
                ball_valve_on = False
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Переходы
            if state_entry_time.secsTo(QTime.currentTime()) > 2:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = WateringProcessStates.CLOSE_ZONE_VALVES
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.CLOSE_ZONE_VALVES:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                for zone_id, zone in zones:
                    zones_outputs[zone_id]['exec request'] = False
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Переходы
            if state_entry_time.secsTo(QTime.currentTime()) > 2:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = WateringProcessStates.STOP_PUMP
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.STOP_PUMP:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                pump_outputs['run req from watering'] = False
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Переходы
            if state_entry_time.secsTo(QTime.currentTime()) > 2:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = WateringProcessStates.PRESSURE_RELIEF
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.PRESSURE_RELIEF:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                active_zone_id = None
                for zone_id, zone in zones:
                    if zone['available']:
                        if zone['feedback'] is ExecDevFeedbacks.FINISHED and not active_zone_id:
                            zones_outputs[zone_id]['exec request'] = True
                            zones_outputs[zone_id]['duration'] = PRESSURE_RELIEF_DURATION
                            active_zone_id = zone_id
                            break
                prev_state = curr_state

            # Постоянные действия

            # Переходы
            if not active_zone_id:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Сброс давления отменен, нет ни одной доступной зоны'})
                curr_state = WateringProcessStates.CLOSE_ZONE_VALVE_AFTER_PRESSURE_RELIEF
                again = True
            elif zones[active_zone_id]['feedback'] is ExecDevFeedbacks.DONE or \
                    zones[active_zone_id]['feedback'] is ExecDevFeedbacks.ABORTED:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Сброс давления выполнен'})
                curr_state = WateringProcessStates.CLOSE_ZONE_VALVE_AFTER_PRESSURE_RELIEF
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.CLOSE_ZONE_VALVE_AFTER_PRESSURE_RELIEF:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                for zone_id, zone in zones:
                    if zone['exec request']:
                        zones_outputs[zone_id]['exec request'] = False
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Переходы
            if state_entry_time.secsTo(QTime.currentTime()) > 2:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = WateringProcessStates.RESETTING
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.RESETTING:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                feedback = feedback_temp
                prev_state = curr_state

            # Переходы
            if not act_cycle:
                curr_state = WateringProcessStates.STANDBY
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        if not again:
            break

    # статусы
    if error:
        status = OnOffDeviceStatuses.FAULTY
    elif not available:
        status = OnOffDeviceStatuses.OFF
    elif prev_state is WateringProcessStates.STANDBY:
        status = OnOffDeviceStatuses.STANDBY
    elif prev_state is WateringProcessStates.START_PUMP or \
            prev_state is WateringProcessStates.OPEN_BALL_VALVE:
        status = OnOffDeviceStatuses.STARTUP
    elif prev_state is WateringProcessStates.WATER_ZONE or \
            prev_state is WateringProcessStates.CHANGE_ZONE:
        status = OnOffDeviceStatuses.RUN
    elif prev_state is WateringProcessStates.STOP_PUMP or \
            prev_state is WateringProcessStates.CLOSE_BALL_VALVE or \
            prev_state is WateringProcessStates.CLOSE_ZONE_VALVES or \
            prev_state is WateringProcessStates.CLOSE_ZONE_VALVE_AFTER_PRESSURE_RELIEF:
        status = OnOffDeviceStatuses.SHUTDOWN

    # обновляем выходы
    process_outputs = {'ackn': ackn,
                       'error': error,
                       'available': available,
                       'feedback': feedback,
                       'feedback temp': feedback_temp,
                       'ball valve on': ball_valve_on,
                       'active zone id': active_zone_id,
                       'curr state': curr_state,
                       'prev state': prev_state,
                       'state entry time': state_entry_time,
                       'raised errors': raised_errors,
                       'raised warnings': raised_warnings,
                       'status': status
                       }
    return process_outputs, zones_outputs, pump_outputs, alarm_log_batch
