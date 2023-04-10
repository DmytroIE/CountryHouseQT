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
    act_cycle_id = process['act cycle ID']  # Вместо exec request, если не None, то это сигнал к запуску
    act_zone_id = process['active zone id']
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
        for zone_id, zone in zones.items():
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

            at_least_one_zone_available = False
            for zone_id, zone in zones.items():
                if zone['available']:
                    at_least_one_zone_available = True

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
                curr_state = WateringProcessStates.CHECK_AVAILABILITY
                again = False

        elif curr_state is WateringProcessStates.STANDBY:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Полив завершен'})
                prev_state = curr_state

            # Постоянные действия
            feedback = ExecDevFeedbacks.FINISHED

            # Переходы
            if act_cycle_id and available and not error:
                curr_state = WateringProcessStates.START_PUMP
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.START_PUMP:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Подача сигнала запуска на насос'})
                pump_outputs['run req from watering'] = True
                feedback = ExecDevFeedbacks.BUSY
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Постоянные действия

            # Переходы
            if not available or not act_cycle_id:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Полив отменен при запуске'})
                pump_outputs['run req from watering'] = False
                feedback_temp = ExecDevFeedbacks.ABORTED
                curr_state = WateringProcessStates.RESETTING
                again = True
            elif error:
                pump_outputs['run req from watering'] = False
                feedback_temp = ExecDevFeedbacks.ABORTED
                curr_state = WateringProcessStates.RESETTING
                again = True
            elif pump['feedback for watering'] is EnableDevFeedbacks.RUN and \
                    state_entry_time.secsTo(QTime.currentTime()) >= SP_STATE_TRANSITION_TYPICAL_DELAY:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Насос запущен'})
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = WateringProcessStates.OPEN_BALL_VALVE
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.OPEN_BALL_VALVE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Подача сигнала открытия на шаровый кран'})
                ball_valve_on = True
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Постоянные действия

            # Переходы
            if not available or not act_cycle_id:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Полив отменен при запуске'})
                feedback_temp = ExecDevFeedbacks.ABORTED
                curr_state = WateringProcessStates.CLOSE_BALL_VALVE
                again = True
            elif error:
                feedback_temp = ExecDevFeedbacks.ABORTED
                curr_state = WateringProcessStates.CLOSE_BALL_VALVE
                again = True
            elif state_entry_time.secsTo(QTime.currentTime()) >= SP_STATE_TRANSITION_TYPICAL_DELAY:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Сигнал открытия шарового крана подан'})
                curr_state = WateringProcessStates.WATER_ZONE
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.WATER_ZONE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Поиск активной зоны для полива'})
                act_zone_id = None
                for zone_id, zone in zones.items():
                    if zone['available']:
                        if zone['available'] and zone['feedback'] is ExecDevFeedbacks.FINISHED:
                            act_zone_id = zone_id
                            zones_outputs[act_zone_id]['exec request'] = True
                            zones_outputs[act_zone_id]['duration'] = durations[act_cycle_id][act_zone_id]['duration']
                            alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                                    'dt_stamp': QDateTime.currentDateTime(),
                                                    'text': f'Process: Подача сигнала запуска на зону {zone["name"]}'})
                            break
                prev_state = curr_state

            # Постоянные действия

            # Переходы
            if not act_zone_id:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Полив выполнен, больше зон для полива не осталось'})
                feedback_temp = ExecDevFeedbacks.DONE
                curr_state = WateringProcessStates.CLOSE_BALL_VALVE
                again = True
            elif not available or not act_cycle_id:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Полив отменен во время работы'})
                feedback_temp = ExecDevFeedbacks.ABORTED
                curr_state = WateringProcessStates.CLOSE_BALL_VALVE
                again = True
            elif error:
                feedback_temp = ExecDevFeedbacks.ABORTED
                curr_state = WateringProcessStates.CLOSE_BALL_VALVE
                again = True
            elif zones[act_zone_id]['feedback'] is ExecDevFeedbacks.DONE or \
                    zones[act_zone_id]['feedback'] is ExecDevFeedbacks.ABORTED:
                curr_state = WateringProcessStates.CHANGE_ZONE
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.CHANGE_ZONE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Смена активной зоны'})
                state_entry_time = QTime.currentTime()
                prev_state = curr_state  # Нужно, чтобы опять прийти в WateringStates.WATER_ZONE и выполнить един дей

            # Постоянные действия

            # Переходы
            if not available or not act_cycle_id:
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
            elif state_entry_time.secsTo(QTime.currentTime()) >= SP_STATE_TRANSITION_TYPICAL_DELAY:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = WateringProcessStates.WATER_ZONE
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.CLOSE_BALL_VALVE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Снятие сигнала открытия с шарового крана'})
                ball_valve_on = False
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Переходы
            if state_entry_time.secsTo(QTime.currentTime()) >= SP_STATE_TRANSITION_TYPICAL_DELAY:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Сигнал открытия с шарового крана снят'})
                curr_state = WateringProcessStates.RESET_ZONES_AFTER_WATERING
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.RESET_ZONES_AFTER_WATERING:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Снятие сигнала запуска с зон'})
                for zone_id, zone in zones.items():
                    zones_outputs[zone_id]['exec request'] = False
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Переходы
            if state_entry_time.secsTo(QTime.currentTime()) >= SP_STATE_TRANSITION_TYPICAL_DELAY:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Сигнал запуска с зон снят'})
                curr_state = WateringProcessStates.STOP_PUMP
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.STOP_PUMP:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Снятие сигнала запуска с насоса'})
                pump_outputs['run req from watering'] = False
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Переходы
            if state_entry_time.secsTo(QTime.currentTime()) >= SP_STATE_TRANSITION_TYPICAL_DELAY:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Сигнал запуска с насоса снят'})
                curr_state = WateringProcessStates.PRESSURE_RELIEF
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.PRESSURE_RELIEF:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Поиск доступной зоны для сброса давления'})
                act_zone_id = None
                for zone_id, zone in zones.items():
                    if zone['available']:
                        if zone['available'] and zone['feedback'] is ExecDevFeedbacks.FINISHED:
                            act_zone_id = zone_id
                            zones_outputs[act_zone_id]['exec request'] = True
                            zones_outputs[act_zone_id]['duration'] = PRESSURE_RELIEF_DURATION
                            alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                                    'dt_stamp': QDateTime.currentDateTime(),
                                                    'text': f'Process: Подача сигнала запуска на зону {zone["name"]}'})
                            break
                prev_state = curr_state

            # Постоянные действия

            # Переходы
            if not act_zone_id:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Сброс давления отменен, нет ни одной доступной зоны'})
                curr_state = WateringProcessStates.RESET_ZONES_AFTER_PRESSURE_RELIEF
                again = True
            elif zones[act_zone_id]['feedback'] is ExecDevFeedbacks.DONE or \
                    zones[act_zone_id]['feedback'] is ExecDevFeedbacks.ABORTED:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Сброс давления выполнен'})
                curr_state = WateringProcessStates.RESET_ZONES_AFTER_PRESSURE_RELIEF
                again = True
            else:
                curr_state = WateringProcessStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringProcessStates.RESET_ZONES_AFTER_PRESSURE_RELIEF:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Снятие сигнала запуска с зон после сброса давления'})
                for zone_id, zone in zones.items():
                    if zone['exec request']:
                        zones_outputs[zone_id]['exec request'] = False
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Переходы
            if state_entry_time.secsTo(QTime.currentTime()) >= SP_STATE_TRANSITION_TYPICAL_DELAY:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Process: Сигнал запуска с зон после сброса давления снят'})
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
            if not act_cycle_id:
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
            prev_state is WateringProcessStates.RESET_ZONES_AFTER_WATERING or \
            prev_state is WateringProcessStates.RESET_ZONES_AFTER_PRESSURE_RELIEF:
        status = OnOffDeviceStatuses.SHUTDOWN

    # обновляем выходы
    process_outputs = {'ackn': ackn,
                       'error': error,
                       'available': available,
                       'feedback': feedback,
                       'feedback temp': feedback_temp,
                       'ball valve on': ball_valve_on,
                       'active zone id': act_zone_id,
                       'curr state': curr_state,
                       'prev state': prev_state,
                       'state entry time': state_entry_time,
                       'raised errors': raised_errors,
                       'raised warnings': raised_warnings,
                       'status': status
                       }
    return process_outputs, zones_outputs, pump_outputs, alarm_log_batch
