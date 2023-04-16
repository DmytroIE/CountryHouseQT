from PyQt5.QtCore import QTime, QDateTime
from string import Template

from src.utils.WateringStatuses import *
from src.store.ConnectedComponent import ConnectedComponent


class ContactorStrategy(ConnectedComponent):
    def __init__(self, store_, ID):
        ConnectedComponent.__init__(self, store_)
        self._id = ID
        self._no_fdbk_timer = None
        self._fdbk_not_off_timer = None
        self._curr_state = ContactorStates.CHECK_AVAILABILITY
        self._prev_state = ContactorStates.STANDBY
        self._state_entry_time = None
        self._dispatch({'type': 'contactors/UPDATE_ITEM',
                        'payload': {'ID': self._id,
                                    'new_data': {'ackn': False,
                                                 'feedback': EnableDevFeedbacks.STOP,
                                                 'cont_feedback': False,
                                                 'run_req': False,
                                                 'cont_on': False,
                                                 'status': OnOffDeviceStatuses.STANDBY}
                                    }})

    def _get_own_state(self):
        return self._get_store_state()[self._id]

    def run(self):
        name = self._get_own_state()['name']
        enabled = self._get_own_state()['enabled']
        run_req = self._get_own_state()['run_req']
        cont_feedback = self._get_own_state()['cont_feedback']
        outputs = {'ackn': self._get_own_state()['ackn'],
                   'error': self._get_own_state()['error'],
                   'feedback': self._get_own_state()['feedback'],
                   'available': self._get_own_state()['available'],
                   'cont_on': self._get_own_state()['cont_on'],
                   'raised_errors': self._get_own_state()['raised_errors'].copy(),
                   'raised_warnings': self._get_own_state()['raised_warnings'].copy(),
                   'status': self._get_own_state()['status']}

        alarm_log_batch = []

        curr_time = QDateTime.currentDateTime()

        # Квитирование
        if outputs['ackn']:
            if outputs['error']:
                income_error_test = False
                for key, val in outputs['raised_errors'].items():
                    if key is ContactorErrorMessages.NO_FEEDBACK_WHEN_RUN:
                        if val:  # для более сложных ошибок типа перегрева тут будет еще и условие выхода
                            outputs['raised_errors'][key] = False
                            alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_OUT,
                                                    'alarm_id': key,
                                                    'equip_id': self._id,
                                                    'dt_stamp': curr_time,
                                                    'text': 'OUT:' + key.value.format(name)})
                            # error_test = False # для др ошибок, если условие выхода на выполнилось, то будет True
                outputs['error'] = income_error_test
            outputs['ackn'] = False

        # Автомат
        while True:
            again = False

            if self._curr_state is ContactorStates.CHECK_AVAILABILITY:
                # Этот шаг исполняется один раз
                outputs['available'] = enabled

                # Переходы
                self._curr_state = self._prev_state
                again = True

            elif self._curr_state is ContactorStates.CHECK_IF_DEVICES_STOPPED:
                # Постоянные действия

                # "Contactor feedback is not off" timer
                if not outputs['cont_on'] and cont_feedback:
                    if not self._fdbk_not_off_timer:
                        self._fdbk_not_off_timer = curr_time
                else:
                    self._fdbk_not_off_timer = None
                # Здесь могут быть и проверки работы др оборудования

                # В данном случае в цикле только одна проверка, но для сложного объекта их может быть много

                for key, val in outputs['raised_warnings'].items():
                    if key is ContactorWarningMessages.CANT_STOP_CONTACTOR:
                        if self._fdbk_not_off_timer:
                            if self._fdbk_not_off_timer.secsTo(curr_time) > SP_CONTACTOR_TIMER_DELAY:
                                if not val:
                                    outputs['raised_warnings'][key] = True
                                    alarm_log_batch.append({'type': LogAlarmMessageTypes.WARNING_IN,
                                                            'alarm_id': key,
                                                            'equip_id': self._id,
                                                            'dt_stamp': curr_time,
                                                            'text': 'IN:' + key.value.format(name)})
                        else:
                            # это будет работать и при запуске
                            if val:
                                outputs['raised_warnings'][key] = False
                                alarm_log_batch.append({'type': LogAlarmMessageTypes.WARNING_OUT,
                                                        'alarm_id': key,
                                                        'equip_id': self._id,
                                                        'dt_stamp': curr_time,
                                                        'text': 'OUT:' + key.value.format(name)})

                # если есть хотя бы один активный, но еще не сработавший таймер невыключения
                # когда больше одного таймера, то их собрать в массив и тоже применить any
                list_of_warning_bits = outputs['raised_warnings'].values()
                list_of_started_timers = [self._fdbk_not_off_timer]

                if not any(list_of_warning_bits) and any(list_of_started_timers):
                    outputs['feedback'] = EnableDevFeedbacks.PENDING

                # если же хотя бы один таймер невыключения сработал
                if not run_req:
                    if any(list_of_warning_bits):
                        outputs['feedback'] = EnableDevFeedbacks.NOT_STOP
                # а уж если все сработали (не в этом случае, когда всего один таймер, а если более сложное устройство)
                else:
                    if all(list_of_warning_bits):
                        outputs['feedback'] = EnableDevFeedbacks.RUN

                # Переходы
                self._curr_state = ContactorStates.CHECK_IF_DEVICES_RUNNING
                again = True

            elif self._curr_state is ContactorStates.CHECK_IF_DEVICES_RUNNING:
                # Постоянные действия

                # No contactor feedback timer
                if outputs['cont_on'] and not cont_feedback:
                    if not self._no_fdbk_timer:
                        self._no_fdbk_timer = curr_time
                else:
                    self._no_fdbk_timer = None

                # Здесь могут быть и проверки работы др оборудования

                income_error_test = False
                for key, val in outputs['raised_errors'].items():
                    if key is ContactorErrorMessages.NO_FEEDBACK_WHEN_RUN:
                        if self._no_fdbk_timer:
                            if self._no_fdbk_timer.secsTo(curr_time) > SP_CONTACTOR_TIMER_DELAY:
                                # здесь могут быть и др условия через ИЛИ:
                                # ИЛИ сигнала с контактора нет, ИЛИ шаровый кран не открылся ИЛИ ...
                                outputs['raised_errors'][key] = True
                                alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_IN,
                                                        'alarm_id': key,
                                                        'equip_id': self._id,
                                                        'dt_stamp': curr_time,
                                                        'text': 'IN:' + key.value.format(name)})
                                self._no_fdbk_timer = None
                                income_error_test = True
                if income_error_test:
                    outputs['error'] = True
                list_of_started_timers = [self._no_fdbk_timer]
                if not outputs['error'] and any(list_of_started_timers):
                    outputs['feedback'] = EnableDevFeedbacks.PENDING
                if run_req:
                    if not outputs['available'] or outputs['error']:
                        if not cont_feedback:  # обязательно эта проверка
                            # может появиться cont_feedback даже во время аварии, если есть запрос run_req,
                            # то получается, что он выполняется, раз есть cont_feedback
                            outputs['feedback'] = EnableDevFeedbacks.NOT_RUN
                        # else:
                        #     outputs['feedback'] = EnableDevFeedbacks.RUN

                # Переходы
                if income_error_test:
                    self._curr_state = self._prev_state
                    again = True
                else:
                    self._curr_state = ContactorStates.CHECK_AVAILABILITY
                    again = False

            elif self._curr_state is ContactorStates.STANDBY:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': curr_time,
                                            'text': f'Cont: Контактор {name} отключен'})
                    self._prev_state = self._curr_state

                # Постоянные действия
                outputs['feedback'] = EnableDevFeedbacks.STOP

                # Переходы
                if outputs['available'] and not outputs['error'] and run_req:
                    self._curr_state = ContactorStates.STARTUP
                    again = True
                else:
                    self._curr_state = ContactorStates.CHECK_IF_DEVICES_STOPPED
                    again = True

            elif self._curr_state is ContactorStates.STARTUP:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': curr_time,
                                            'text': f'Cont: Подача сигнала запуска на контактор {name}'})
                    outputs['cont_on'] = True
                    self._state_entry_time = curr_time
                    self._prev_state = self._curr_state

                # Постоянные действия
                outputs['feedback'] = EnableDevFeedbacks.PENDING

                # Переходы
                if not run_req:
                    self._curr_state = ContactorStates.SHUTDOWN
                    again = True
                elif not outputs['available']:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': curr_time,
                                            'text': f'Cont: Работа контактора {name} отменена во время запуска'})
                    self._curr_state = ContactorStates.SHUTDOWN
                    again = True
                elif outputs['error']:
                    self._curr_state = ContactorStates.SHUTDOWN
                    again = True
                elif cont_feedback and \
                        self._state_entry_time.secsTo(curr_time) >= SP_STATE_TRANSITION_TYPICAL_DELAY:
                    # специальная задержка, чтобы побыть какое-то время в этом состоянии
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': curr_time,
                                            'text': f'Cont: Контактор {name} запущен'})
                    self._curr_state = ContactorStates.RUN
                    again = True
                else:
                    self._curr_state = ContactorStates.CHECK_IF_DEVICES_STOPPED
                    again = True

            elif self._curr_state is ContactorStates.RUN:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    self._prev_state = self._curr_state

                # Постоянные действия
                outputs['feedback'] = EnableDevFeedbacks.RUN

                # Переходы
                if not run_req:
                    self._curr_state = ContactorStates.SHUTDOWN
                    again = True
                elif not outputs['available']:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': curr_time,
                                            'text': f'Работа контактора {name} отменена во время работы'})
                    self._curr_state = ContactorStates.SHUTDOWN
                    again = True
                elif outputs['error']:
                    self._curr_state = ContactorStates.SHUTDOWN
                    again = True
                else:
                    self._curr_state = ContactorStates.CHECK_IF_DEVICES_STOPPED
                    again = True

            elif self._curr_state is ContactorStates.SHUTDOWN:
                # Единоразовые действия при входе в шаг
                if self._curr_state is not self._prev_state:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': curr_time,
                                            'text': f'Cont: снятие сигнала запуска с контактора {name}'})
                    outputs['cont_on'] = False
                    self._state_entry_time = curr_time
                    self._prev_state = self._curr_state

                # Постоянные действия
                outputs['feedback'] = EnableDevFeedbacks.PENDING

                # Переходы
                if run_req and not outputs['error'] and outputs['available']:
                    self._curr_state = ContactorStates.STARTUP
                    again = True
                elif not cont_feedback and \
                        self._state_entry_time.secsTo(curr_time) >= SP_STATE_TRANSITION_TYPICAL_DELAY:
                    # специальная задержка, чтобы побыть какое-то время в этом состоянии
                    self._curr_state = ContactorStates.STANDBY
                    again = True
                else:
                    self._curr_state = ContactorStates.CHECK_IF_DEVICES_STOPPED
                    again = True

            if not again:
                break

        # статусы
        if self._prev_state is ContactorStates.STANDBY:
            if outputs['error']:
                outputs['status'] = OnOffDeviceStatuses.FAULTY
            elif not outputs['available']:
                outputs['status'] = OnOffDeviceStatuses.OFF
            else:
                outputs['status'] = OnOffDeviceStatuses.STANDBY
        elif self._prev_state is ContactorStates.STARTUP:
            outputs['status'] = OnOffDeviceStatuses.STARTUP
        elif self._prev_state is ContactorStates.RUN:
            outputs['status'] = OnOffDeviceStatuses.RUN
        elif self._prev_state is ContactorStates.SHUTDOWN:
            outputs['status'] = OnOffDeviceStatuses.SHUTDOWN

        # обновляем выходы
        checked_outputs = {}
        for key, val in outputs.items():
            if val != self._get_own_state()[key]:
                checked_outputs[key] = val
        if checked_outputs:
            # print(f'{checked_outputs=}')
            self._dispatch({'type': 'contactors/UPDATE_ITEM',
                            'payload': {'ID': self._id,
                                        'new_data': checked_outputs}})
        if alarm_log_batch:
            for item in alarm_log_batch:
                print(f'{item["dt_stamp"].toString("dd.MM.yy mm:ss")} {item["text"]}')

    def _updater(self):
        pass


if __name__ == '__main__':
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import \
        QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QTextBrowser
    import pydux
    import pickle
    from collections import OrderedDict
    from src.store.ConnectedComponent import ConnectedComponent
    from src.utils.Buttons import *

    keys_to_print = ['ackn', 'error', 'available', 'enabled', 'cont_on', 'feedback', 'status']


    def reducer(state=None, action=None):
        if state is None:
            state = {}
        if action['type'] == 'contactors/UPDATE_ITEM':
            cont_id = action['payload']['ID']
            new_state = state.copy()
            new_state[cont_id] = {**new_state[cont_id], **(action['payload']['new_data'])}
            return new_state
        else:
            return state


    default_state = OrderedDict({'3RR2fg65': {'ID': '3RR2fg65',
                                              'name': 'Свет',
                                              'ackn': False,
                                              'error': False,
                                              'feedback': EnableDevFeedbacks.STOP,
                                              'cont_feedback': False,
                                              'enabled': True,
                                              'run_req': False,
                                              'available': True,
                                              'cont_on': False,
                                              'raised_errors': {ContactorErrorMessages.NO_FEEDBACK_WHEN_RUN: False},
                                              'raised_warnings': {ContactorWarningMessages.CANT_STOP_CONTACTOR: False},
                                              'status': OnOffDeviceStatuses.STANDBY
                                              }})


    class Application(QApplication):
        def __init__(self, args):
            QApplication.__init__(self, args)
            print('Application created')
            self.store = None
            try:
                with open('store.dat', 'rb') as f:
                    state = pickle.load(f)
                    print(f'state after loading {state}')
                    self.store = pydux.create_store(reducer, state)
            except Exception as e:
                print(f'Could not open dat file, default settings are loaded\nError: {e}')
                self.store = pydux.create_store(reducer, default_state)

        def save_store_on_exit(self):
            try:
                with open('store.dat', 'wb') as f:
                    pickle.dump(self.store.get_state(), f, pickle.HIGHEST_PROTOCOL)
            except Exception as e:
                print(f'Could not save store\nError: {e}')


    class MainWindow(ConnectedComponent, QMainWindow):
        def __init__(self, store_):
            QMainWindow.__init__(self)
            ConnectedComponent.__init__(self, store_)

            self._create_ui()
            self._updater()

        def _get_own_state(self):  # selector
            return self._get_store_state()

        def _on_state_update(self, new_state, updated_keys_list, action):
            # print(f'{new_state=}')
            if action == 'ADD' or action == 'UPDATE':
                for cont_id in new_state:
                    for key in new_state[cont_id]:
                        if key in self._updated_widgets_map:
                            self._updated_widgets_map[key](new_state[cont_id][key])

                    new_text = [f'{k}: {new_state[cont_id][k]}' for k in keys_to_print]
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

            self.setWindowTitle("Test Pump Strategy")
            self.setGeometry(0, 0, 640, 480)

            self._wdg_central = QWidget()
            self._lyt_main = QVBoxLayout(self._wdg_central)

            self._updated_widgets_map = {}

            self._btn_enable = QPushButton('Enable')
            self._btn_enable.clicked.connect(
                lambda: self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                        'payload':
                                            {'ID': '3RR2fg65',
                                             'new_data':
                                                 {'enabled': not self._get_own_state()['3RR2fg65']['enabled']}}
                                        }))
            self._updated_widgets_map['enabled'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_enable,
                                                     'StandardButton',
                                                     'StandardButton EnabledButton')

            self._btn_run = QPushButton('Run')
            self._btn_run.clicked.connect(
                lambda: self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                        'payload':
                                            {'ID': '3RR2fg65',
                                             'new_data':
                                                 {'run_req': not self._get_own_state()['3RR2fg65']['run_req']}}
                                        }))
            self._updated_widgets_map['run_req'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_run,
                                                     'StandardButton',
                                                     'StandardButton EnabledButton')

            self._btn_cont_fdbk = QPushButton('Cont fdbk')
            self._btn_cont_fdbk.clicked.connect(
                lambda: self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                        'payload':
                                            {'ID': '3RR2fg65',
                                             'new_data':
                                                 {'cont_feedback': not self._get_own_state()['3RR2fg65'][
                                                     'cont_feedback']}
                                             }}))
            self._updated_widgets_map['cont_feedback'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_cont_fdbk,
                                                     'StandardButton',
                                                     'StandardButton EnabledButton')

            self._btn_ackn = QPushButton('Ackn')
            self._btn_ackn.clicked.connect(
                lambda: self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                        'payload':
                                            {'ID': '3RR2fg65',
                                             'new_data':
                                                 {'ackn': True}}
                                        }))
            self._updated_widgets_map['ackn'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_ackn,
                                                     'StandardButton',
                                                     'StandardButton EnabledButton')

            self._lyt_first = QHBoxLayout()
            self._lyt_first.addWidget(self._btn_enable)
            self._lyt_first.addWidget(self._btn_run)

            self._lyt_second = QHBoxLayout()
            self._lyt_second.addWidget(self._btn_cont_fdbk)
            self._lyt_second.addWidget(self._btn_ackn)

            self._txt_view = QTextBrowser()

            self._lyt_main.addLayout(self._lyt_first)
            self._lyt_main.addLayout(self._lyt_second)
            self._lyt_main.addWidget(self._txt_view)

            self.setCentralWidget(self._wdg_central)

        def closeEvent(self, event):
            appl = QApplication.instance()
            appl.save_store_on_exit()


    class ContController(ConnectedComponent):
        def __init__(self, store_):
            ConnectedComponent.__init__(self, store_)
            self._contactor = ContactorStrategy(store_, '3RR2fg65')
            self._one_second_timer = QTimer()
            self._one_second_timer.timeout.connect(self._on_timer_tick)
            self._one_second_timer.start(1000)

        def _on_timer_tick(self):
            try:
                self._contactor.run()
            except Exception as e:
                print(f'Ошибка выполнения автомата, {e}')

        def _updater(self):
            pass


    app = Application([])

    controller = ContController(app.store)

    window = MainWindow(app.store)
    window.show()

    app.exec()
