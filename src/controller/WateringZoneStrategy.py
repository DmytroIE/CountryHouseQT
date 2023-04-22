from PyQt5.QtCore import QDateTime
from src.store.ConnectedToStoreComponent import ConnectedToStoreComponent

from src.utils.WateringStatuses import *

SP_DELAY = 5  # in seconds


class WateringZoneStrategy:
    def __init__(self, ID):
        self._id = ID
        self._curr_state = ZoneStates.CHECK_AVAILABILITY
        self._prev_state = ZoneStates.STANDBY
        self._state_entry_time = None
        self._flowrate_hi_timer = None
        self._flowrate_lo_timer = None
        self._feedback_temp = ExecDevFeedbacks.FINISHED
        self._init_data = {'ackn': False,
                           'feedback': ExecDevFeedbacks.FINISHED,
                           'cont_feedback': False,
                           'exec_req': False,
                           'valve_on': False,
                           'progress': 0,
                           'raised_warnings': {ZoneWarningMessages.LOW_FLOWRATE: False},
                           'status': OnOffDeviceStatuses.STANDBY}

    @property
    def init_data(self):
        return self._init_data

    @property
    def ID(self):
        return self._id

    def _get_duration_state(self, process_state, durations_state):
        cycle_id = process_state['act_cycle_id']
        if cycle_id:
            return durations_state[cycle_id][self._id]
        else:
            return 0  # эта строчка на всякий случай, защитная

    def run(self, own_state, process_state, durations_state):
        name = own_state['name']
        enabled = own_state['enabled']
        exec_req = own_state['exec_req']
        hi_lim_flowrate = own_state['hi_lim_flowrate']
        lo_lim_flowrate = own_state['lo_lim_flowrate']
        control_flowrate = own_state['control_flowrate']

        ackn = own_state['ackn']
        error = own_state['error']
        feedback = own_state['feedback']
        available = own_state['available']
        valve_on = own_state['valve_on']
        progress = own_state['progress']
        raised_errors = own_state['raised_errors'].copy()
        raised_warnings = own_state['raised_warnings'].copy()
        status = own_state['status']

        curr_flowrate = process_state['curr_flowrate']

        cycle_id = process_state['act_cycle_id']
        if cycle_id:
            duration_sec = durations_state[cycle_id][self._id]['duration'] * 60
        else:
            duration_sec = 0

        alarm_log_batch = []

        curr_time = QDateTime.currentDateTime()

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
                                                    'equip ID': self._id,
                                                    'dt_stamp': curr_time,
                                                    'text': 'OUT:' + key.value.format(name, curr_flowrate)})
                            # error_test = False # для др ошибок, если условие выхода на выполнилось, то будет True
                error = error_test
            ackn = False

        # Автомат
        while True:
            again = False

            if self._curr_state is ZoneStates.CHECK_AVAILABILITY:
                # Этот шаг исполняется один раз

                available = enabled

                # Переходы
                self._curr_state = self._prev_state
                again = True

            elif self._curr_state is ZoneStates.CHECK_IF_DEVICES_STOPPED:
                # Здесь этот шаг просто для проформы, чтобы все было единообразно
                self._curr_state = ZoneStates.CHECK_IF_DEVICES_RUNNING
                again = True

            elif self._curr_state is ZoneStates.CHECK_IF_DEVICES_RUNNING:
                # Постоянные действия
                # curr_time = QDateTime.currentDateTime()

                # в случае первого обор можно и не проверять if cont_on, а вот дальше для др обор нужно
                # No contactor feedback timer
                if valve_on and curr_flowrate > hi_lim_flowrate:
                    if not self._flowrate_hi_timer:
                        self._flowrate_hi_timer = curr_time
                else:
                    self._flowrate_hi_timer = None

                # Здесь могут быть и проверки работы др оборудования

                # Переходы
                error_test = False
                for key, val in raised_errors.items():
                    if key is ZoneErrorMessages.HIGH_FLOWRATE:
                        if self._flowrate_hi_timer and control_flowrate:
                            if self._flowrate_hi_timer.secsTo(curr_time) > SP_DELAY:
                                raised_errors[key] = True
                                alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_IN,
                                                        'alarm ID': key,
                                                        'equip ID': self._id,
                                                        'dt_stamp': curr_time,
                                                        'text': 'IN:' + key.value.format(name, curr_flowrate)})
                                self._flowrate_hi_timer = None
                                error_test = True
                if error_test:
                    error = True
                    self._curr_state = self._prev_state
                    again = True
                else:
                    self._curr_state = ZoneStates.CHECK_AVAILABILITY
                    again = False

            elif self._curr_state is ZoneStates.STANDBY:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': curr_time,
                                            'text': f'Zone: Зона {name} отключена'})
                    self._prev_state = self._curr_state

                # Постоянные действия
                feedback = ExecDevFeedbacks.FINISHED

                # Переходы
                if available and not error and exec_req:
                    if duration_sec > 0:
                        self._curr_state = ZoneStates.EXECUTE
                        again = True
                    else:
                        alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                                'dt_stamp': curr_time,
                                                'text': f'Zone: Полив зоны {name} не выполнялся, время полива 0'})
                        progress = 100
                        self._feedback_temp = ExecDevFeedbacks.DONE
                        self._curr_state = ZoneStates.RESETTING
                        again = True
                else:
                    self._curr_state = ZoneStates.CHECK_IF_DEVICES_STOPPED
                    again = True

            elif self._curr_state is ZoneStates.EXECUTE:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': curr_time,
                                            'text': f'Zone: Подача сигнала открытия на клапан зоны {name}'})
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': curr_time,
                                            'text': f'Zone: Полив зоны {name} начат'})
                    valve_on = True
                    feedback = ExecDevFeedbacks.BUSY
                    self._state_entry_time = curr_time
                    self._prev_state = self._curr_state

                # Постоянные действия
                seconds_passed = self._state_entry_time.secsTo(curr_time)
                if duration_sec > 0:
                    progress = int(seconds_passed / duration_sec * 100.0)
                    if progress > 100:
                        progress = 100
                else:
                    progress = 100

                # "Low flowrate" timer
                if curr_flowrate < lo_lim_flowrate:
                    if not self._flowrate_lo_timer:
                        self._flowrate_lo_timer = curr_time
                else:
                    self._flowrate_lo_timer = None
                # Здесь могут быть и проверки работы др оборудования

                # В данном случае в цикле только одна проверка, но для сложного объекта их может быть много

                for key, val in raised_warnings.items():
                    if key is ZoneWarningMessages.LOW_FLOWRATE:
                        if self._flowrate_lo_timer and control_flowrate:
                            if self._flowrate_lo_timer.secsTo(curr_time) > SP_DELAY:
                                if not val:
                                    raised_warnings[key] = True
                                    alarm_log_batch.append({'type': LogAlarmMessageTypes.WARNING_IN,
                                                            'alarm ID': key,
                                                            'equip ID': self._id,
                                                            'dt_stamp': curr_time,
                                                            'text': 'IN:' + key.value.format(name, curr_flowrate)})
                        else:
                            if val:
                                raised_warnings[key] = False
                                alarm_log_batch.append({'type': LogAlarmMessageTypes.WARNING_OUT,
                                                        'alarm ID': key,
                                                        'equip ID': self._id,
                                                        'dt_stamp': curr_time,
                                                        'text': 'OUT:' + key.value.format(name, curr_flowrate)})

                # Переходы
                if not available or not exec_req:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': curr_time,
                                            'text': f'Zone: Полив зоны {name} отменен'})
                    self._feedback_temp = ExecDevFeedbacks.ABORTED
                    self._curr_state = ZoneStates.SHUTDOWN
                    again = True
                elif error:
                    self._feedback_temp = ExecDevFeedbacks.ABORTED
                    self._curr_state = ZoneStates.SHUTDOWN
                    again = True
                elif progress >= 100:  # seconds_passed >= duration_sec:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': curr_time,
                                            'text': f'Zone: Полив зоны {name} выполнен'})
                    self._feedback_temp = ExecDevFeedbacks.DONE
                    self._curr_state = ZoneStates.SHUTDOWN
                    again = True
                else:
                    self._curr_state = ZoneStates.CHECK_IF_DEVICES_STOPPED
                    again = True

            elif self._curr_state is ZoneStates.SHUTDOWN:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': curr_time,
                                            'text': f'Zone: Снятие сигнала открытия с клапан зоны {name}'})
                    for key, val in raised_warnings.items():
                        if key is ZoneWarningMessages.LOW_FLOWRATE:
                            if val:
                                raised_warnings[key] = False
                                alarm_log_batch.append({'type': LogAlarmMessageTypes.WARNING_OUT,
                                                        'alarm ID': key,
                                                        'equip ID': self._id,
                                                        'dt_stamp': curr_time,
                                                        'text': 'OUT:' + key.value.substitute(name=name,
                                                                                              flowrate=curr_flowrate)})
                    valve_on = False
                    self._state_entry_time = curr_time
                    self._prev_state = self._curr_state

                # Переходы
                if self._state_entry_time.secsTo(QDateTime.currentDateTime()) >= SP_STATE_TRANSITION_TYPICAL_DELAY:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': curr_time,
                                            'text': f'Zone: Сигнал открытия с клапан зоны {name} снят'})
                    self._curr_state = ZoneStates.RESETTING
                    again = True
                else:
                    self._curr_state = ZoneStates.CHECK_IF_DEVICES_STOPPED
                    again = True

            elif self._curr_state is ZoneStates.RESETTING:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    feedback = self._feedback_temp
                    self._prev_state = self._curr_state

                # Переходы
                if not exec_req:
                    self._curr_state = ZoneStates.STANDBY
                    again = True
                else:
                    self._curr_state = ZoneStates.CHECK_IF_DEVICES_STOPPED
                    again = True

            if not again:
                break

        # статусы
        if error:
            status = OnOffDeviceStatuses.FAULTY
        elif not available:
            status = OnOffDeviceStatuses.OFF
        elif self._prev_state is ZoneStates.STANDBY:
            status = OnOffDeviceStatuses.STANDBY
        elif self._prev_state is ZoneStates.EXECUTE:
            status = OnOffDeviceStatuses.RUN
        elif self._prev_state is ZoneStates.SHUTDOWN or \
                self._prev_state is ZoneStates.RESETTING:
            status = OnOffDeviceStatuses.SHUTDOWN

        # обновляем выходы
        outputs = {'ackn': ackn,
                   'error': error,
                   'feedback': feedback,
                   'available': available,
                   'valve_on': valve_on,
                   'progress': progress,
                   'raised_errors': raised_errors,
                   'raised_warnings': raised_warnings,
                   'status': status}

        checked_outputs = {}
        for key, val in outputs.items():
            if val != own_state[key]:
                checked_outputs[key] = val

        return checked_outputs, alarm_log_batch

    def _updater(self):
        pass


if __name__ == '__main__':
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import \
        QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, \
        QDoubleSpinBox, QTextBrowser, QLabel
    import pydux
    from collections import OrderedDict
    from src.ConnectedToStoreApplication import ConnectedToStoreApplication
    from src.utils.Buttons import *

    keys_to_print = ['ackn', 'error', 'available',
                     'valve_on', 'progress', 'feedback', 'status']

    zone_default_state = OrderedDict({
        'LZliGv4F': {'ID': 'LZliGv4F',
                     'gpio_num': 13,
                     'name': 'Зона 1',
                     'ackn': False,
                     'error': False,
                     'feedback': ExecDevFeedbacks.FINISHED,
                     'enabled': True,
                     'exec_req': False,
                     'available': True,
                     'valve_on': False,
                     'control_flowrate': True,
                     'hi_lim_flowrate': 1.6,
                     'lo_lim_flowrate': 0.4,
                     'progress': 0,
                     'raised_errors': {ZoneErrorMessages.HIGH_FLOWRATE: False},
                     'raised_warnings': {ZoneWarningMessages.LOW_FLOWRATE: False},
                     'status': OnOffDeviceStatuses.STANDBY
                     }})
    process_default_state = {'ID': 'gg58d9d8',
                             'curr_flowrate': 0.2,
                             'act_cycle_id': 'CPyCGmQ0F',
                             }
    durations_default_state = OrderedDict({
        'CPyCGmQ0F': OrderedDict({'LZliGv4F': {'cycle_id': 'CPyCGmQ0F', 'zone_id': 'LZliGv4F', 'duration': 2},
                                  'FclCGDyZx': {'cycle_id': 'CPyCGmQ0F', 'zone_id': 'FclCGDyZx', 'duration': 1},
                                  'iPyLGSJbx': {'cycle_id': 'CPyCGmQ0F', 'zone_id': 'iPyLGSJbx', 'duration': 1},
                                  'Fcyi4kPtV': {'cycle_id': 'CPyCGmQ0F', 'zone_id': 'Fcyi4kPtV', 'duration': 1},
                                  'iBwi42jQ1': {'cycle_id': 'CPyCGmQ0F', 'zone_id': 'iBwi42jQ1', 'duration': 1}})})

    default_state = {'watering': {'zones': zone_default_state,
                                  'process': process_default_state,
                                  'durations': durations_default_state}}


    def watering_zone_reducer(state=None, action=None):
        if state is None:
            state = OrderedDict({})
        if action['type'] == 'wateringzones/UPDATE_ITEM':
            zone_id = action['payload']['ID']
            new_state = state.copy()
            new_state[zone_id] = {**new_state[zone_id], **(action['payload']['new_data'])}
            return new_state
        else:
            return state


    def watering_process_reducer(state=None, action=None):
        if state is None:
            state = {}
        if action['type'] == 'wateringprocess/UPDATE':
            new_state = {**state, **(action['payload'])}
            return new_state
        else:
            return state


    def watering_duration_reducer(state=None, action=None):
        if state is None:
            state = OrderedDict({})
        if action['type'] == 'wateringduration/UPDATE':
            return state
        else:
            return state


    watering_reducer = pydux.combine_reducers({'zones': watering_zone_reducer,
                                               'process': watering_process_reducer,
                                               'durations': watering_duration_reducer})
    root_reducer = pydux.combine_reducers({'watering': watering_reducer})


    class Zone(ConnectedToStoreComponent, QWidget):
        def __init__(self, ID):
            QWidget.__init__(self)
            ConnectedToStoreComponent.__init__(self)
            self._id = ID
            self._create_ui()
            self._updater()

        def _get_own_state(self):  # selector
            return self._get_store_state()['watering']['zones'][self._id]

        def _on_state_update(self, new_state, updated_keys_list, action):
            if action == 'ADD' or action == 'UPDATE':
                for key in updated_keys_list:
                    if key in self._updated_widgets_map:
                        self._updated_widgets_map[key](new_state[key])

                new_text = [f'{k}: {new_state[k]}' for k in keys_to_print]
                self._txt_view.setText('\n'.join(new_text))

        def _create_ui(self):
            self._lyt_main = QVBoxLayout(self)

            self._updated_widgets_map = {}

            self._btn_enable = QPushButton('Enable')
            self._btn_enable.clicked.connect(
                lambda: self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                        'payload': {'ID': self._id,
                                                    'new_data':
                                                        {'enabled': not self._get_own_state()['enabled']}}
                                        }))
            self._updated_widgets_map['enabled'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_enable,
                                                     'StandardButton',
                                                     'StandardButton EnabledButton')

            self._btn_exec = QPushButton('Execute')
            self._btn_exec.clicked.connect(
                lambda: self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                        'payload': {'ID': self._id,
                                                    'new_data':
                                                        {'exec_req': not self._get_own_state()['exec_req']}
                                                    }}))
            self._updated_widgets_map['exec_req'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_exec,
                                                     'StandardButton',
                                                     'StandardButton EnabledButton')

            self._btn_ackn = QPushButton('Ackn')
            self._btn_ackn.clicked.connect(
                lambda: self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                        'payload': {'ID': self._id,
                                                    'new_data':
                                                        {'ackn': not self._get_own_state()['ackn']}
                                                    }}))
            self._updated_widgets_map['ackn'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_ackn,
                                                     'StandardButton',
                                                     'StandardButton EnabledButton')

            self._lyt_first = QHBoxLayout()
            self._lyt_first.addWidget(self._btn_enable)
            self._lyt_first.addWidget(self._btn_exec)
            self._lyt_first.addWidget(self._btn_ackn)

            self._txt_view = QTextBrowser()

            self._lyt_main.addLayout(self._lyt_first)
            self._lyt_main.addWidget(self._txt_view)


    class Process(ConnectedToStoreComponent, QWidget):
        def __init__(self):
            QWidget.__init__(self)
            ConnectedToStoreComponent.__init__(self)

            self._create_ui()
            self._updater()

        def _get_own_state(self):  # selector
            return self._get_store_state()['watering']['process']

        def _on_state_update(self, new_state, updated_keys_list, action):
            pass

        def _create_ui(self):
            self._lbl_curr_flowrate = QLabel('Current flowrate simulate')
            self._spb_curr_flowrate = QDoubleSpinBox()
            self._spb_curr_flowrate.setRange(0.0, 2.0)
            self._spb_curr_flowrate.setValue(self._get_own_state()['curr_flowrate'])
            self._spb_curr_flowrate.valueChanged.connect(
                lambda: self._dispatch({'type': 'wateringprocess/UPDATE',
                                        'payload':
                                            {'curr_flowrate': self._spb_curr_flowrate.value()}
                                        }))

            self._lyt_second = QHBoxLayout(self)
            self._lyt_second.addWidget(self._lbl_curr_flowrate)
            self._lyt_second.addWidget(self._spb_curr_flowrate)


    class MainWindow(QMainWindow):
        def __init__(self):
            QMainWindow.__init__(self)
            self._create_ui()

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

            self.setWindowTitle("Test Zone Strategy")
            self.setGeometry(0, 0, 640, 480)

            self._wdg_central = QWidget()
            self._lyt_main = QVBoxLayout(self._wdg_central)

            self._process = Process()
            self._zone = Zone('LZliGv4F')

            self._lyt_main.addWidget(self._process)
            self._lyt_main.addWidget(self._zone)
            self.setCentralWidget(self._wdg_central)

        def closeEvent(self, event):
            appl = QApplication.instance()
            appl.save_store_on_exit()


    class ZoneController(ConnectedToStoreComponent):
        def __init__(self):
            ConnectedToStoreComponent.__init__(self)
            self._zone = WateringZoneStrategy('LZliGv4F')
            self._one_second_timer = QTimer()
            self._one_second_timer.timeout.connect(self._on_timer_tick)
            self._one_second_timer.start(1000)
            self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                            'payload': {'ID': self._zone.ID,
                                        'new_data': self._zone.init_data
                                        }})


        def _on_timer_tick(self):
            try:
                zone_state = self._get_store_state()['watering']['zones'][self._zone.ID]
                process_state = self._get_store_state()['watering']['process']
                durations_state = self._get_store_state()['watering']['durations']
                checked_outputs, alarm_log_batch = self._zone.run(zone_state, process_state, durations_state)
                if checked_outputs:
                    self._dispatch({'type': 'wateringzones/UPDATE_ITEM',
                                    'payload': {'ID': self._zone.ID,
                                                'new_data': checked_outputs}})
                if alarm_log_batch:
                    for item in alarm_log_batch:
                        print(f'{item["dt_stamp"].toString("dd.MM.yy mm:ss")} {item["text"]}')

            except Exception as e:
                print(f'Ошибка выполнения автомата, {e}')

        def _updater(self):
            pass


    app = ConnectedToStoreApplication(root_reducer, default_state)

    window = MainWindow()
    controller = ZoneController()

    window.show()

    app.exec()
