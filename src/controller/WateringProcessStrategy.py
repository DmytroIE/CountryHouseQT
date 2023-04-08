from PyQt5.QtCore import QTime, QDateTime
from collections import OrderedDict
from src.utils.WateringStatuses import *


PRESSURE_RELIEF_DURATION = 1  # minutes


def watering_process_strategy(process, zones, pump):
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
    for zone_id, zone in zones:
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
                            zones_outputs[zone_id]['duration'] = act_cycle[active_zone_id]
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
    return {'ackn': ackn,
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
            }, zones_outputs, pump_outputs, alarm_log_batch


if __name__ == '__main__':
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import \
        QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, \
        QDoubleSpinBox, QTextBrowser, QLabel
    import pydux
    from src.store.ConnectedComponent import ConnectedComponent
    from src.utils.Buttons import *

    keys_to_print = ['error', 'feedback', 'available',
                     'valve on', 'progress', 'curr state', 'prev state',
                     'status']


    class MainWindow(ConnectedComponent, QMainWindow):
        def __init__(self, store1):
            QMainWindow.__init__(self)
            ConnectedComponent.__init__(self, store1)

            self._create_ui()
            self._updater()

        def _get_own_state(self):  # selector
            return self._get_store_state()

        def _on_state_update(self, new_state, updated_keys_list, action):
            if action == 'ADD' or action == 'UPDATE':
                for key in updated_keys_list:
                    if key in self._updated_widgets_map:
                        self._updated_widgets_map[key](new_state[key])

                new_text = [f'{k}: {new_state[k]}' for k in keys_to_print]
                self._txt_view.setText('\n'.join(new_text))

        def _create_ui(self):
            self.setStyleSheet('.StandardButton {\
                                                     background-color: rgb(250,250,250);\
                                                     border-style: solid;\
                                                     border-width: 1px;\
                                                     border-radius: 4px;\
                                                     border-color: rgb(180,180,180);\
                                                     padding: 4px;\
                                                     }\
                                       .StandardButton:hover {\
                                                     border-color: rgb(190,250,210);\
                                                     background-color: rgb(230,240,240);\
                                                     }\
                                       .EnabledButton {\
                                                     border-color: rgb(150,225,211);\
                                                     background-color: rgb(193, 225, 211);\
                                                    }\
                                       .EnabledButton:hover{\
                                                      border-color: rgb(130,205,191);\
                                                      background-color: rgb(163, 195, 201);}')
            state = self._get_own_state()

            self.setWindowTitle("Test Zone Strategy")
            self.setGeometry(0, 0, 640, 480)

            self._wdg_central = QWidget()
            self._lyt_main = QVBoxLayout(self._wdg_central)

            self._updated_widgets_map = {}

            self._btn_enable = QPushButton('Enable')
            self._btn_enable.clicked.connect(
                lambda: self._dispatch({'type': 'zone/UPDATE',
                                        'payload':
                                            {'enabled': not self._get_own_state()['enabled']}
                                        }))
            self._updated_widgets_map['enabled'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_enable,
                                                     'StandardButton',
                                                     'StandardButton EnabledButton')

            self._btn_exec = QPushButton('Execute')
            self._btn_exec.clicked.connect(
                lambda: self._dispatch({'type': 'zone/UPDATE',
                                        'payload':
                                            {'exec request': not self._get_own_state()['exec request']}
                                        }))
            self._updated_widgets_map['exec request'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_exec,
                                                     'StandardButton',
                                                     'StandardButton EnabledButton')

            self._btn_ackn = QPushButton('Ackn')
            self._btn_ackn.clicked.connect(
                lambda: self._dispatch({'type': 'zone/UPDATE',
                                        'payload':
                                            {'ackn': not self._get_own_state()['ackn']}
                                        }))
            self._updated_widgets_map['ackn'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_ackn,
                                                     'StandardButton',
                                                     'StandardButton EnabledButton')

            self._lyt_first = QHBoxLayout()
            self._lyt_first.addWidget(self._btn_enable)
            self._lyt_first.addWidget(self._btn_exec)
            self._lyt_first.addWidget(self._btn_ackn)

            self._lbl_curr_flowrate = QLabel('Current flowrate simulate')
            self._spb_curr_flowrate = QDoubleSpinBox()
            self._spb_curr_flowrate.setRange(0.0, 2.0)
            self._spb_curr_flowrate.setSingleStep(0.1)
            self._spb_curr_flowrate.setValue(state['curr flowrate'])
            self._spb_curr_flowrate.valueChanged.connect(
                lambda: self._dispatch({'type': 'watering/UPDATE',
                                        'payload':
                                            {'curr flowrate': self._spb_curr_flowrate.value()}
                                        }))

            self._lyt_second = QHBoxLayout()
            self._lyt_second.addWidget(self._lbl_curr_flowrate)
            self._lyt_second.addWidget(self._spb_curr_flowrate)

            self._txt_view = QTextBrowser()

            self._lyt_main.addLayout(self._lyt_first)
            self._lyt_main.addLayout(self._lyt_second)
            self._lyt_main.addWidget(self._txt_view)

            self.setCentralWidget(self._wdg_central)


    class ContController(ConnectedComponent):
        def __init__(self, store1):
            ConnectedComponent.__init__(self, store1)
            self._one_second_timer = QTimer()
            self._one_second_timer.timeout.connect(self._on_timer_tick)
            self._one_second_timer.start(1000)

        def _on_timer_tick(self):
            state = self._get_store_state()
            try:
                new_state_chunk, alarm_log_batch = watering_zone_strategy(state)
                self._dispatch({'type': 'zone/UPDATE', 'payload': new_state_chunk})
                for item in alarm_log_batch:
                    print(f'{item["dt_stamp"].toString("dd.MM.yy mm:ss")} {item["text"]}')
            except Exception as e:
                print(f'Ошибка выполнения автомата, {e}')

        def _updater(self):
            pass


    zones_init_state = OrderedDict({'9966rtdf':
                                        {'ID': '9966rtdf',
                                         'name': 'Zone 1',
                                         'ackn': False,
                                         'error': False,
                                         'feedback': ExecDevFeedbacks.FINISHED,
                                         'enabled': True,
                                         'exec request': False,
                                         'available': True,
                                         'valve on': False,
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
                                    'asdfghjk':
                                        {'ID': 'asdfghjk',
                                         'name': 'Zone 2',
                                         'ackn': False,
                                         'error': False,
                                         'feedback': ExecDevFeedbacks.FINISHED,
                                         'enabled': True,
                                         'exec request': False,
                                         'available': True,
                                         'valve on': False,
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
                                         }})

    watering_init_state = {'ID': '9966rtdf',
                           'curr flowrate': 0.0}

    alarm_log_init_state = {'ID': '9f5u89er',
                            'ackn': False}

    init_state = {'zones': zones_init_state,
                  'watering': watering_init_state,
                  'alarm log': alarm_log_init_state}


    def watering_zones_reducer(state=None, action=None):
        if state is None:
            state = {}
        elif action['type'] == 'wateringzones/UPDATE':
            new_state = state.copy()
            for zone_id, zone in new_state:
                zone_new_item = new_state[zone_id].copy()
                new_state[zone_id] = {**zone_new_item, **(action['payload']['new_data'])}
            return new_state
        elif action['type'] == 'wateringzones/ACKNOWLEDGEMENT':
            new_state = state.copy()
            for key, item in state:
                new_item = item.copy()
                new_state[key] = {**new_item, **({'ackn': True})}
            return new_state
        else:
            return state


    def watering_process_reducer(state=None, action=None):
        if state is None:
            state = {}
        elif action['type'] == 'wateringprocess/UPDATE':
            new_state = {**state, **(action['payload'])}
            return new_state
        else:
            return state


    def alarm_log_reducer(state=None, action=None):
        if state is None:
            state = {}
        elif action['type'] == 'alarmlog/ACKNOWLEDGEMENT':
            new_state = {**state, **{'ackn': True}}  # только для проформы, на самом деле важнее middleware
            return new_state
        else:
            return state


    def alarm_log_middleware(store):
        dispatch, get_state = store['dispatch'], store['get_state']
        print('alarm_log_middleware')

        def disp(next_):
            def act(action):
                next_(action)
                if action['type'] == 'alarmlog/ACKNOWLEDGEMENT':
                    dispatch({'type': 'wateringzones/ACKNOWLEDGEMENT'})

            return act

        return disp


    root_reducer = pydux.combine_reducers({'watering zones': watering_zones_reducer,
                                           'watering process': watering_process_reducer,
                                           'alarm log': alarm_log_reducer})
    store = pydux.create_store(root_reducer, init_state)

    app = QApplication([])

    window = MainWindow(store)
    controller = ContController(store)

    window.show()

    app.exec()
