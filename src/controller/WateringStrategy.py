from PyQt5.QtCore import QTime, QDateTime
from collections import OrderedDict
from src.utils.WateringStatuses import *

watering_durations_initial = OrderedDict({
    'CPyCGmQ0F': OrderedDict({'LZliGv4F': 15,
                              'FclCGDyZx': 15,
                              'iPyLGSJbx': 15,
                              'Fcyi4kPtV': 15,
                              'iBwi42jQ1': 15}),
    'Lcli4yFwL': OrderedDict({'LZliGv4F': 15,
                              'FclCGDyZx': 15,
                              'iPyLGSJbx': 15,
                              'Fcyi4kPtV': 15,
                              'iBwi42jQ1': 15})
})

watering_zones_initial = OrderedDict({
    'LZliGv4F': {'gpio_num': 13,
                 'name': 'Зона 1',
                 'ackn': False,
                 'error': False,
                 'feedback': ExecDevFeedbacks.FINISHED,
                 'enabled': True,
                 'exec request': False,
                 'available': True,
                 'valve on': False,
                 'curr flowrate': 0.0,
                 'hi lim flowrate': 1.6,
                 'lo lim flowrate': 0.4,
                 'duration': 1,
                 'progress': 0.0,
                 'flowrate hi timer': None,
                 'flowrate lo timer': None,
                 'curr state': ZoneStates.CHECK_AVAILABILITY,
                 'prev state': ZoneStates.STANDBY,
                 'state entry time': None,
                 'raised errors': {ZoneErrorMessages.HIGH_FLOWRATE: False},
                 'raised warnings': {ZoneWarningMessages.LOW_FLOWRATE: False},
                 'status': OnOffDeviceStatuses.STANDBY},
    'FclCGDyZx': {'gpio_num': 14,
                  'name': 'Зона 2',
                  'ackn': False,
                  'error': False,
                  'feedback': ExecDevFeedbacks.FINISHED,
                  'enabled': True,
                  'exec request': False,
                  'available': True,
                  'valve on': False,
                  'curr flowrate': 0.0,
                  'hi lim flowrate': 1.6,
                  'lo lim flowrate': 0.4,
                  'duration': 1,
                  'progress': 0.0,
                  'flowrate hi timer': None,
                  'flowrate lo timer': None,
                  'curr state': ZoneStates.CHECK_AVAILABILITY,
                  'prev state': ZoneStates.STANDBY,
                  'state entry time': None,
                  'raised errors': {ZoneErrorMessages.HIGH_FLOWRATE: False},
                  'raised warnings': {ZoneWarningMessages.LOW_FLOWRATE: False},
                  'status': OnOffDeviceStatuses.STANDBY
                  },
    'iPyLGSJbx': {'gpio_num': 15,
                  'name': 'Зона 3',
                  'ackn': False,
                  'error': False,
                  'feedback': ExecDevFeedbacks.FINISHED,
                  'enabled': True,
                  'exec request': False,
                  'available': True,
                  'valve on': False,
                  'curr flowrate': 0.0,
                  'hi lim flowrate': 1.6,
                  'lo lim flowrate': 0.4,
                  'duration': 1,
                  'progress': 0.0,
                  'flowrate hi timer': None,
                  'flowrate lo timer': None,
                  'curr state': ZoneStates.CHECK_AVAILABILITY,
                  'prev state': ZoneStates.STANDBY,
                  'state entry time': None,
                  'raised errors': {ZoneErrorMessages.HIGH_FLOWRATE: False},
                  'raised warnings': {ZoneWarningMessages.LOW_FLOWRATE: False},
                  'status': OnOffDeviceStatuses.STANDBY
                  },
    'Fcyi4kPtV': {'gpio_num': 16,
                  'name': 'Зона 4',
                  'ackn': False,
                  'error': False,
                  'feedback': ExecDevFeedbacks.FINISHED,
                  'enabled': True,
                  'exec request': False,
                  'available': True,
                  'valve on': False,
                  'curr flowrate': 0.0,
                  'hi lim flowrate': 1.6,
                  'lo lim flowrate': 0.4,
                  'duration': 1,
                  'progress': 0.0,
                  'flowrate hi timer': None,
                  'flowrate lo timer': None,
                  'curr state': ZoneStates.CHECK_AVAILABILITY,
                  'prev state': ZoneStates.STANDBY,
                  'state entry time': None,
                  'raised errors': {ZoneErrorMessages.HIGH_FLOWRATE: False},
                  'raised warnings': {ZoneWarningMessages.LOW_FLOWRATE: False},
                  'status': OnOffDeviceStatuses.STANDBY
                  },
    'iBwi42jQ1': {'gpio_num': 17,
                  'name': 'Палисадник',
                  'ackn': False,
                  'error': False,
                  'feedback': ExecDevFeedbacks.FINISHED,
                  'enabled': True,
                  'exec request': False,
                  'available': True,
                  'valve on': False,
                  'curr flowrate': 0.0,
                  'hi lim flowrate': 1.6,
                  'lo lim flowrate': 0.4,
                  'duration': 1,
                  'progress': 0.0,
                  'flowrate hi timer': None,
                  'flowrate lo timer': None,
                  'curr state': ZoneStates.CHECK_AVAILABILITY,
                  'prev state': ZoneStates.STANDBY,
                  'state entry time': None,
                  'raised errors': {ZoneErrorMessages.HIGH_FLOWRATE: False},
                  'raised warnings': {ZoneWarningMessages.LOW_FLOWRATE: False},
                  'status': OnOffDeviceStatuses.STANDBY
                  }
})

watering_cycles_initial = OrderedDict({
    'CPyCGmQ0F': {'enabled': True,
                  'hour': 6,
                  'minute': 0,
                  'status': OnOffDeviceStatuses.STANDBY},
    'Lcli4yFwL': {'enabled': True,
                  'hour': 20,
                  'minute': 0,
                  'status': OnOffDeviceStatuses.STANDBY}
})

PRESSURE_RELIEF_DURATION = 1  # minutes


def watering_strategy(watering, zones, pump):
    watering_id = watering['ID']
    ackn = watering['ackn']
    error = watering['error']
    feedback = watering['feedback']
    available = watering['available']
    ball_valve_on = watering['ball valve on']
    act_cycle = watering['act cycle']  # Вместо exec request, если не None, то это сигнал к запуску
    active_zone_id = ['active zone id']
    curr_state = watering['curr state']
    prev_state = watering['prev state']
    state_entry_time = watering['state entry time']
    raised_errors = watering['raised errors']
    raised_warnings = watering['raised warnings']
    status = watering['status']
    pump_outputs = {'run req from watering': pump['run req from watering']}

    zones_outputs = {}
    for zone_id, zone in zones:
        zones_outputs[zone_id] = {'exec request': zone['exec request'],
                                  'duration': zone['duration']}
    alarm_log_batch = []

    # Квитирование
    if ackn:
        if error:
            error_test = False
            for key, val in raised_errors.items():
                if key is WateringErrorMessages.PUMP_NOT_RUNNING:
                    if val:
                        if pump['available']:
                            raised_errors[key] = False
                            alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_OUT,
                                                    'alarm ID': key,
                                                    'equip ID': watering_id,
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

        if curr_state is WateringStates.CHECK_AVAILABILITY:
            # Этот шаг исполняется один раз

            at_least_one_zone_available = True
            for zone in zones:
                at_least_one_zone_available = zone['available']

            if not at_least_one_zone_available \
                    or not pump['available'] \
                    or error:
                available = False
            else:
                available = True

            # Переходы
            curr_state = prev_state
            again = True

        elif curr_state is WateringStates.CHECK_IF_DEVICES_STOPPED:
            # Здесь этот шаг просто для проформы, чтобы все было единообразно
            # Переходы
            curr_state = WateringStates.CHECK_IF_DEVICES_RUNNING
            again = True

        elif curr_state is WateringStates.CHECK_IF_DEVICES_RUNNING:
            # Переходы
            error_test = False
            for key, val in raised_errors.items():
                if key is WateringErrorMessages.PUMP_NOT_RUNNING:
                    if pump_outputs['run req from watering'] and \
                            pump['feedback for watering'] is OnOffDevFeedbacks.NOT_RUN:
                        raised_errors[key] = True
                        alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_IN,
                                                'alarm ID': key,
                                                'equip ID': watering_id,
                                                'dt_stamp': QDateTime.currentDateTime(),
                                                'text': 'IN:' + key.value})
                        error_test = True
            if error_test:
                error = True
                available = False
                # feedback = ExecDevFeedbacks.ABORTED
                curr_state = prev_state  # WateringStates.CLOSE_BALL_VALVE
                again = True
            else:
                curr_state = ZoneStates.CHECK_AVAILABILITY
                again = False

        elif curr_state is WateringStates.STANDBY:
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
                curr_state = WateringStates.START_PUMP
                again = True
            else:
                curr_state = WateringStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringStates.START_PUMP:
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
                feedback = ExecDevFeedbacks.ABORTED
                curr_state = WateringStates.STOP_PUMP
                again = True
            elif pump['feedback for watering'] is OnOffDevFeedbacks.RUN and \
                    state_entry_time.secsTo(QTime.currentTime()) > 5:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = WateringStates.OPEN_BALL_VALVE
                again = True
            else:
                curr_state = WateringStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringStates.OPEN_BALL_VALVE:
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
                feedback = ExecDevFeedbacks.ABORTED
                curr_state = WateringStates.SHUTDOWN
                again = True
            elif state_entry_time.secsTo(QTime.currentTime()) > 5:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = WateringStates.WATER_ZONE
                again = True
            else:
                curr_state = WateringStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringStates.WATER_ZONE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                active_zone_id = None
                for zone_id, zone in zones:
                    if zone['available']:
                        if zone['feedback'] is ExecDevFeedbacks.FINISHED and not active_zone_id:
                            zones_outputs[zone_id]['exec request'] = True
                            zones_outputs[zone_id]['duration'] = act_cycle[active_zone_id]
                            active_zone_id = zone_id
                prev_state = curr_state

            # Постоянные действия

            # Переходы
            if not active_zone_id:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив выполнен'})
                feedback = ExecDevFeedbacks.DONE
                for zone_id, zone in zones:
                    zones_outputs[zone_id]['exec request'] = False
                curr_state = WateringStates.CLOSE_BALL_VALVE
                again = True
            elif not available or not act_cycle:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив отменен'})
                for zone_id, zone in zones:
                    zones_outputs[zone_id]['exec request'] = False
                feedback = ExecDevFeedbacks.ABORTED
                curr_state = WateringStates.CLOSE_BALL_VALVE
                again = True

            elif zones[active_zone_id]['feedback'] is ExecDevFeedbacks.DONE or \
                    zones[active_zone_id]['feedback'] is ExecDevFeedbacks.ABORTED:
                curr_state = WateringStates.CHANGE_ZONE
                again = True
            else:
                curr_state = WateringStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringStates.CHANGE_ZONE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                state_entry_time = QTime.currentTime()
                prev_state = curr_state  # Нужно, чтобы опять прийти в WateringStates.WATER_ZONE и выполнить един дей

            # Постоянные действия

            # Переходы
            if state_entry_time.secsTo(QTime.currentTime()) > 2:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = WateringStates.WATER_ZONE
                again = True
            else:
                curr_state = WateringStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringStates.CLOSE_BALL_VALVE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                ball_valve_on = False
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Переходы
            if state_entry_time.secsTo(QTime.currentTime()) > 2:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = WateringStates.STOP_PUMP
                again = True
            else:
                curr_state = WateringStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringStates.STOP_PUMP:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                pump_outputs['run req from watering'] = False
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Переходы
            if state_entry_time.secsTo(QTime.currentTime()) > 2:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = WateringStates.PRESSURE_RELIEF
                again = True
            else:
                curr_state = WateringStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringStates.PRESSURE_RELIEF:
            # Единоразовые действия при входе в шаг
            already_busy_zone_id = None  # Защита от дурака, вдруг уже есть включенная зона (ручной р, например)
            if curr_state is not prev_state:
                active_zone_id = None
                for zone_id, zone in zones:
                    if zone['available']:
                        if zone['feedback'] is ExecDevFeedbacks.FINISHED and not active_zone_id:
                            zones_outputs[zone_id]['exec request'] = True
                            zones_outputs[zone_id]['duration'] = PRESSURE_RELIEF_DURATION
                            active_zone_id = zone_id
                        elif zone['feedback'] is ExecDevFeedbacks.BUSY:
                            already_busy_zone_id = zone_id
                prev_state = curr_state

            # Постоянные действия

            # Переходы
            if not active_zone_id:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Сброс давления отменен, нет ни одной доступной зоны'})
                curr_state = WateringStates.SHUTDOWN
                again = True
            elif already_busy_zone_id:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Сброс давления отменен, одна из зон уже включена'})
                curr_state = WateringStates.SHUTDOWN
                again = True
            elif zones[active_zone_id]['feedback'] is ExecDevFeedbacks.DONE or \
                    zones[active_zone_id]['feedback'] is ExecDevFeedbacks.ABORTED:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Сброс давления выполнен'})
                curr_state = WateringStates.SHUTDOWN
                again = True
            else:
                curr_state = WateringStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is WateringStates.SHUTDOWN:
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
                curr_state = WateringStates.STANDBY
                again = True
            else:
                curr_state = WateringStates.CHECK_IF_DEVICES_STOPPED
                again = True

        if not again:
            break

    # статусы
    if error:
        status = OnOffDeviceStatuses.FAULTY
    elif not available:
        status = OnOffDeviceStatuses.OFF
    elif prev_state is WateringStates.STANDBY:
        status = OnOffDeviceStatuses.STANDBY
    elif prev_state is WateringStates.START_PUMP or \
            prev_state is WateringStates.OPEN_BALL_VALVE:
        status = OnOffDeviceStatuses.STARTUP
    elif prev_state is WateringStates.WATER_ZONE or \
            prev_state is WateringStates.CHANGE_ZONE:
        status = OnOffDeviceStatuses.RUN
    elif prev_state is WateringStates.STOP_PUMP or \
            prev_state is WateringStates.CLOSE_BALL_VALVE or \
            prev_state is WateringStates.SHUTDOWN:
        status = OnOffDeviceStatuses.SHUTDOWN

    # обновляем выходы
    return {'ackn': ackn,
            'error': error,
            'available': available,
            'feedback': feedback,
            'ball valve on': ball_valve_on,
            'active zone id': active_zone_id,
            'curr state': curr_state,
            'prev state': prev_state,
            'state entry time': state_entry_time,
            'raised errors': raised_errors,
            'raised warnings': raised_warnings,
            'status': status
            }, zones_outputs, pump_outputs, alarm_log_batch
