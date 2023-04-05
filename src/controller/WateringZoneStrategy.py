from PyQt5.QtCore import QTime, QDateTime
from string import Template
from collections import OrderedDict

from src.utils.WateringStatuses import *

SP_DELAY = 5  # in seconds


def watering_zone_strategy(zone, watering):
    zone_id = zone['ID']
    name = zone['name']
    ackn = zone['ackn']
    error = zone['error']
    feedback = zone['feedback']
    enabled = zone['enabled']
    exec_request = zone['exec request']
    available = zone['available']
    valve_on = zone['valve on']
    curr_flowrate = watering['curr flowrate']
    hi_lim_flowrate = zone['hi lim flowrate']
    lo_lim_flowrate = zone['lo lim flowrate']
    duration_sec = zone['duration'] * 60  # from minutes to seconds
    progress = zone['progress']
    flowrate_hi_timer = zone['flowrate hi timer']
    flowrate_lo_timer = zone['flowrate lo timer']
    curr_state = zone['curr state']
    prev_state = zone['prev state']
    state_entry_time = zone['state entry time']
    raised_errors = zone['raised errors']
    raised_warnings = zone['raised warnings']
    status = zone['status']
    alarm_log_batch = []

    # Квитирование
    if ackn:
        if error:
            error_test = False
            for key, val in raised_errors.items():
                if key is ZoneErrorMessages.HIGH_FLOWRATE:
                    if val:  # для более сложных ошибок тут будет еще и условие выхода
                        raised_errors[key] = False
                        alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_OUT,
                                                'alarm ID': key,
                                                'equip ID': zone_id,
                                                'dt_stamp': QDateTime.currentDateTime(),
                                                'text': 'OUT:' + key.value.substitute(name=name,
                                                                                      flowrate=curr_flowrate)})
                        # error_test = False # для др ошибок, если условие выхода на выполнилось, то будет True
            error = error_test
        ackn = False

    # Автомат
    while True:
        again = False

        if curr_state is ZoneStates.CHECK_AVAILABILITY:
            # Этот шаг исполняется один раз

            if not enabled or error:
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
            # Постоянные действия
            curr_time = QTime.currentTime()

            # в случае первого обор можно и не проверять if cont_on, а вот дальше для др обор нужно
            # No contactor feedback timer
            if valve_on and curr_flowrate > hi_lim_flowrate:
                if not flowrate_hi_timer:
                    flowrate_hi_timer = curr_time
            else:
                flowrate_hi_timer = None

            # Здесь могут быть и проверки работы др оборудования

            # Переходы
            error_test = False
            for key, val in raised_errors.items():
                if key is ZoneErrorMessages.HIGH_FLOWRATE:
                    if flowrate_hi_timer:
                        if flowrate_hi_timer.secsTo(curr_time) > SP_DELAY:
                            raised_errors[key] = True
                            alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_IN,
                                                    'alarm ID': key,
                                                    'equip ID': zone_id,
                                                    'dt_stamp': QDateTime.currentDateTime(),
                                                    'text': 'IN:' + key.value.substitute(name=name,
                                                                                         flowrate=curr_flowrate)})
                            flowrate_hi_timer = None
                            error_test = True
            if error_test:
                error = True
                available = False
                feedback = ExecDevFeedbacks.ABORTED
                curr_state = prev_state  # ZoneStates.SHUTDOWN
                again = True
            else:
                curr_state = ZoneStates.CHECK_AVAILABILITY
                again = False

        elif curr_state is ZoneStates.STANDBY:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Зона {name} отключена'})
                prev_state = curr_state

            # Постоянные действия
            feedback = ExecDevFeedbacks.FINISHED

            # Переходы
            if available and exec_request:
                curr_state = ZoneStates.EXECUTE
                again = True
            else:
                curr_state = ZoneStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is ZoneStates.EXECUTE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                curr_time = QTime.currentTime()
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив зоны {name} начат'})
                valve_on = True
                state_entry_time = curr_time
                prev_state = curr_state

            # Постоянные действия
            feedback = ExecDevFeedbacks.BUSY
            curr_time = QTime.currentTime()
            seconds_passed = state_entry_time.secsTo(curr_time)
            progress = seconds_passed / duration_sec * 100.0

            # "Contactor feedback is not off" timer
            if curr_flowrate < lo_lim_flowrate:
                if not flowrate_lo_timer:
                    flowrate_lo_timer = curr_time
            else:
                flowrate_lo_timer = None
            # Здесь могут быть и проверки работы др оборудования

            # В данном случае в цикле только одна проверка, но для сложного объекта их может быть много

            for key, val in raised_warnings.items():
                if key is ZoneWarningMessages.LOW_FLOWRATE:
                    if flowrate_lo_timer:
                        if flowrate_lo_timer.secsTo(curr_time) > SP_DELAY:
                            if not val:
                                raised_warnings[key] = True
                                alarm_log_batch.append({'type': LogAlarmMessageTypes.WARNING_IN,
                                                        'alarm ID': key,
                                                        'equip ID': zone_id,
                                                        'dt_stamp': QDateTime.currentDateTime(),
                                                        'text': 'IN:' + key.value.substitute(name=name,
                                                                                             flowrate=curr_flowrate)})
                    else:
                        if val:
                            raised_warnings[key] = False
                            alarm_log_batch.append({'type': LogAlarmMessageTypes.WARNING_OUT,
                                                    'alarm ID': key,
                                                    'equip ID': zone_id,
                                                    'dt_stamp': QDateTime.currentDateTime(),
                                                    'text': 'OUT:' + key.value.substitute(name=name,
                                                                                          flowrate=curr_flowrate)})

            # Переходы
            if not available or not exec_request:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив зоны {name} отменен'})
                feedback = ExecDevFeedbacks.ABORTED
                curr_state = ZoneStates.SHUTDOWN
                again = True
            elif seconds_passed > duration_sec:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Полив зоны {name} выполнен'})
                feedback = ExecDevFeedbacks.DONE
                curr_state = ZoneStates.SHUTDOWN
                again = True
            else:
                curr_state = ZoneStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is ZoneStates.SHUTDOWN:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                valve_on = False
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Переходы
            if not exec_request:
                curr_state = ZoneStates.STANDBY
                again = True
            else:
                curr_state = ZoneStates.CHECK_IF_DEVICES_STOPPED
                again = True

        if not again:
            break

    # статусы
    if error:
        status = OnOffDeviceStatuses.FAULTY
    elif not available:
        status = OnOffDeviceStatuses.OFF
    elif prev_state is ZoneStates.STANDBY:
        status = OnOffDeviceStatuses.STANDBY
    elif prev_state is ZoneStates.EXECUTE:
        status = OnOffDeviceStatuses.RUN
    elif prev_state is ZoneStates.SHUTDOWN:
        status = OnOffDeviceStatuses.SHUTDOWN

    # обновляем выходы
    return {'ackn': ackn,
            'error': error,
            'available': available,
            'feedback': feedback,
            'valve on': valve_on,
            'progress': progress,
            'flowrate hi timer': flowrate_hi_timer,
            'flowrate lo timer': flowrate_lo_timer,
            'curr state': curr_state,
            'prev state': prev_state,
            'state entry time': state_entry_time,
            'raised errors': raised_errors,
            'raised warnings': raised_warnings,
            'status': status
            }, alarm_log_batch


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

    watering_init_state = {'curr flowrate': 0.0}

    init_state = {'zones': zones_init_state,
                  'watering': watering_init_state}


    def zones_reducer(state=None, action=None):
        if state is None:
            state = {}
        elif action['type'] == 'zones/UPDATE':
            ID = action['payload']['ID']
            new_state = state.copy()
            item_state = new_state[ID].copy()
            new_state[ID] = {**item_state, **(action['payload']['new_data'])}
            return new_state
        elif action['type'] == 'log/ACKNOWLEDGEMENT':
            new_state = state.copy()
            for key, item in state:
                new_item = item.copy()
                new_state[key] = {**new_item, **({'ackn': True})}
            return new_state
        else:
            return state


    def watering_reducer(state=None, action=None):
        if state is None:
            state = {}
        elif action['type'] == 'watering/UPDATE':
            new_state = {**state, **(action['payload'])}
            return new_state
        else:
            return state

    root_reducer = pydux.combine_reducers({'zones': zones_reducer, 'watering': watering_reducer})
    store = pydux.create_store(root_reducer, init_state)

    app = QApplication([])

    window = MainWindow(store)
    controller = ContController(store)

    window.show()

    app.exec()
