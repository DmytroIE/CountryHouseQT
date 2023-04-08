from PyQt5.QtCore import QTime, QDateTime
from string import Template

from src.utils.WateringStatuses import *


def contactor_strategy(contactor):
    cont_id = contactor['ID']
    name = contactor['name']
    ackn = contactor['ackn']
    error = contactor['error']
    feedback = contactor['feedback']
    contactor_feedback = contactor['contactor feedback']
    enabled = contactor['enabled']
    run_request = contactor['run request']
    available = contactor['available']
    cont_on = contactor['cont on']
    cont_no_fdbk_timer = contactor['cont no fdbk timer']
    cont_fdbk_not_off_timer = contactor['cont fdbk not off timer']
    curr_state = contactor['curr state']
    prev_state = contactor['prev state']
    state_entry_time = contactor['state entry time']
    raised_errors = contactor['raised errors']
    raised_warnings = contactor['raised warnings']
    status = contactor['status']
    alarm_log_batch = []

    # Квитирование
    if ackn:
        if error:
            error_test = False
            for key, val in raised_errors.items():
                if key is ContactorErrorMessages.NO_FEEDBACK_WHEN_RUN:
                    if val:  # для более сложных ошибок типа перегрева тут будет еще и условие выхода
                        raised_errors[key] = False
                        alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_OUT,
                                                'alarm ID': key,
                                                'equip ID': cont_id,
                                                'dt_stamp': QDateTime.currentDateTime(),
                                                'text': 'OUT:' + key.value.substitute(name=name)})
                        # error_test = False # для др ошибок, если условие выхода на выполнилось, то будет True
            error = error_test
        ackn = False

    # Автомат
    while True:
        again = False

        if curr_state is ContactorStates.CHECK_AVAILABILITY:
            # Этот шаг исполняется один раз

            # if not enabled or error:
            #     available = False
            # else:
            #     available = True
            available = enabled

            # Переходы
            curr_state = prev_state
            again = True

        elif curr_state is ContactorStates.CHECK_IF_DEVICES_STOPPED:
            # Постоянные действия
            curr_time = QTime.currentTime()

            # "Contactor feedback is not off" timer
            if not cont_on and contactor_feedback:
                if not cont_fdbk_not_off_timer:
                    cont_fdbk_not_off_timer = curr_time
            else:
                cont_fdbk_not_off_timer = None
            # Здесь могут быть и проверки работы др оборудования

            # В данном случае в цикле только одна проверка, но для сложного объекта их может быть много

            for key, val in raised_warnings.items():
                if key is ContactorWarningMessages.CANT_STOP_CONTACTOR:
                    if cont_fdbk_not_off_timer:
                        if cont_fdbk_not_off_timer.secsTo(curr_time) > SP_CONTACTOR_TIMER_DELAY:
                            if not val:
                                raised_warnings[key] = True
                                alarm_log_batch.append({'type': LogAlarmMessageTypes.WARNING_IN,
                                                        'alarm ID': key,
                                                        'equip ID': cont_id,
                                                        'dt_stamp': QDateTime.currentDateTime(),
                                                        'text': 'IN:' + key.value.substitute(name=name)})
                    else:
                        # это будет работать и при запуске
                        if val:
                            raised_warnings[key] = False
                            alarm_log_batch.append({'type': LogAlarmMessageTypes.WARNING_OUT,
                                                    'alarm ID': key,
                                                    'equip ID': cont_id,
                                                    'dt_stamp': QDateTime.currentDateTime(),
                                                    'text': 'OUT:' + key.value.substitute(name=name)})

            # если есть хотя бы один активный, но еще не сработавший таймер невыключения
            # когда больше одного таймера, то их собрать в массив и тоже применить any
            list_of_warning_bits = raised_warnings.values()

            if not any(list_of_warning_bits) and cont_fdbk_not_off_timer:
                feedback = EnableDevFeedbacks.PENDING

            # если же хотя бы один таймер невыключения сработал
            if not run_request:
                if any(list_of_warning_bits):
                    feedback = EnableDevFeedbacks.NOT_STOP
            # а уж если все сработали (не в этом случае, когда всего один таймер, а если более сложное устройство)
            else:
                if all(list_of_warning_bits):
                    feedback = EnableDevFeedbacks.RUN

            # Переходы
            curr_state = ContactorStates.CHECK_IF_DEVICES_RUNNING
            # prev_state = prev_state  # это подразумевается, на след цикле после CHECK_AVAILABLE вернемся
            # на тот шаг выключения, где застряли
            again = True

        elif curr_state is ContactorStates.CHECK_IF_DEVICES_RUNNING:
            # Постоянные действия
            curr_time = QTime.currentTime()

            # в случае первого обор можно и не проверять if cont_on, а вот дальше для др обор нужно
            # No contactor feedback timer
            if cont_on and not contactor_feedback:
                if not cont_no_fdbk_timer:
                    cont_no_fdbk_timer = curr_time
            else:
                cont_no_fdbk_timer = None

            # Здесь могут быть и проверки работы др оборудования

            # когда больше одного таймера, то их собрать в массив и применить any
            if cont_no_fdbk_timer:
                feedback = EnableDevFeedbacks.PENDING
            if run_request and (not available or error):
                if not contactor_feedback:  # поменять потом эту строчку, если много подконтрольного
                    # оборудования, то все это проверять задолбешься
                    feedback = EnableDevFeedbacks.NOT_RUN

            # Переходы
            error_test = False
            for key, val in raised_errors.items():
                if key is ContactorErrorMessages.NO_FEEDBACK_WHEN_RUN:
                    if cont_no_fdbk_timer:
                        if cont_no_fdbk_timer.secsTo(curr_time) > SP_CONTACTOR_TIMER_DELAY:
                            # здесь могут быть и др условия через ИЛИ:
                            # ИЛИ сигнала с контактора нет, ИЛИ шаровый кран не открылся ИЛИ ...
                            raised_errors[key] = True
                            alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_IN,
                                                    'alarm ID': key,
                                                    'equip ID': cont_id,
                                                    'dt_stamp': QDateTime.currentDateTime(),
                                                    'text': 'IN:' + key.value.substitute(name=name)})
                            cont_no_fdbk_timer = None
                            error_test = True
            if error_test:
                error = True
                # available = False
                curr_state = prev_state
                # prev_state = prev_state  # это подразумевается
                again = True
            else:
                curr_state = ContactorStates.CHECK_AVAILABILITY
                # prev_state = prev_state  # это подразумевается
                again = False

        elif curr_state is ContactorStates.STANDBY:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Контактор {name} отключен'})
                prev_state = curr_state

            # Постоянные действия
            feedback = EnableDevFeedbacks.STOP

            # Переходы
            if available and not error and run_request:
                curr_state = ContactorStates.STARTUP
                again = True
            else:
                curr_state = ContactorStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is ContactorStates.STARTUP:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Запуск контактора {name}'})
                cont_on = True
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Постоянные действия
            feedback = EnableDevFeedbacks.PENDING

            # Переходы
            if not run_request:
                curr_state = ContactorStates.SHUTDOWN
                again = True
            elif not available:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Контактор {name} выключен во время запуска'})
                curr_state = ContactorStates.SHUTDOWN
                again = True
            elif error:
                curr_state = ContactorStates.SHUTDOWN
                again = True
            elif contactor_feedback and \
                    state_entry_time.secsTo(QTime.currentTime()) > SP_STATE_TRANSITION_TYPICAL_DELAY:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = ContactorStates.RUN
                again = True
            else:
                curr_state = ContactorStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is ContactorStates.RUN:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Контактор {name} запущен'})
                prev_state = curr_state

            # Постоянные действия
            feedback = EnableDevFeedbacks.RUN

            # Переходы
            if not run_request:
                curr_state = ContactorStates.SHUTDOWN
                again = True
            elif not available:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Контактор {name} выключен во время работы'})
                curr_state = ContactorStates.SHUTDOWN
                again = True
            elif error:
                curr_state = ContactorStates.SHUTDOWN
                again = True
            else:
                curr_state = ContactorStates.CHECK_IF_DEVICES_STOPPED
                again = True

        elif curr_state is ContactorStates.SHUTDOWN:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Отключение контактора {name}'})
                cont_on = False
                state_entry_time = QTime.currentTime()
                prev_state = curr_state

            # Постоянные действия
            feedback = EnableDevFeedbacks.PENDING

            # Переходы
            if run_request and not error and available:
                curr_state = ContactorStates.STARTUP
                again = True
            elif not contactor_feedback and \
                    state_entry_time.secsTo(QTime.currentTime()) > SP_STATE_TRANSITION_TYPICAL_DELAY:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = ContactorStates.STANDBY
                again = True
            else:
                curr_state = ContactorStates.CHECK_IF_DEVICES_STOPPED
                again = True

        if not again:
            break

    # статусы
    if prev_state is ContactorStates.STANDBY:
        if error:
            status = OnOffDeviceStatuses.FAULTY
        elif not available:
            status = OnOffDeviceStatuses.OFF
        else:
            status = OnOffDeviceStatuses.STANDBY
    elif prev_state is ContactorStates.STARTUP:
        status = OnOffDeviceStatuses.STARTUP
    elif prev_state is ContactorStates.RUN:
        status = OnOffDeviceStatuses.RUN
    elif prev_state is ContactorStates.SHUTDOWN:
        status = OnOffDeviceStatuses.SHUTDOWN

    # обновляем выходы
    return {'ackn': ackn,
            'error': error,
            'feedback': feedback,
            'available': available,
            'cont on': cont_on,
            'cont no fdbk timer': cont_no_fdbk_timer,
            'cont fdbk not off timer': cont_fdbk_not_off_timer,
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
        QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextBrowser
    import pydux
    from src.store.ConnectedComponent import ConnectedComponent
    from src.utils.Buttons import *

    keys_to_print = ['error', 'feedback', 'available',
                     'cont on', 'curr state', 'prev state', 'cont no fdbk timer', 'cont fdbk not off timer',
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

            self.setWindowTitle("Test Pump Strategy")
            self.setGeometry(0, 0, 640, 480)

            self._wdg_central = QWidget()
            self._lyt_main = QVBoxLayout(self._wdg_central)

            self._updated_widgets_map = {}

            self._btn_enable = QPushButton('Enable')
            self._btn_enable.clicked.connect(
                lambda: self._dispatch({'type': 'pump/UPDATE',
                                        'payload':
                                            {'enabled': not self._get_own_state()['enabled']}
                                        }))
            self._updated_widgets_map['enabled'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_enable,
                                                     'StandardButton',
                                                     'StandardButton EnabledButton')

            self._btn_run = QPushButton('Run')
            self._btn_run.clicked.connect(
                lambda: self._dispatch({'type': 'pump/UPDATE',
                                        'payload':
                                            {'run request': not self._get_own_state()['run request']}
                                        }))
            self._updated_widgets_map['run request'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_run,
                                                     'StandardButton',
                                                     'StandardButton EnabledButton')

            self._btn_cont_fdbk = QPushButton('Cont fdbk')
            self._btn_cont_fdbk.clicked.connect(
                lambda: self._dispatch({'type': 'pump/UPDATE',
                                        'payload':
                                            {'contactor feedback': not self._get_own_state()['contactor feedback']}
                                        }))
            self._updated_widgets_map['contactor feedback'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_cont_fdbk,
                                                     'StandardButton',
                                                     'StandardButton EnabledButton')

            self._btn_ackn = QPushButton('Ackn')
            self._btn_ackn.clicked.connect(
                lambda: self._dispatch({'type': 'pump/UPDATE',
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
            self._lyt_first.addWidget(self._btn_run)

            self._lyt_second = QHBoxLayout()
            self._lyt_second.addWidget(self._btn_cont_fdbk)
            self._lyt_second.addWidget(self._btn_ackn)

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
                new_state_chunk, alarm_log_batch = contactor_strategy(state)
                self._dispatch({'type': 'pump/UPDATE', 'payload': new_state_chunk})
                for item in alarm_log_batch:
                    print(f'{item["dt_stamp"].toString("dd.MM.yy mm:ss")} {item["text"]}')
            except Exception as e:
                print(f'Ошибка выполнения автомата, {e}')

        def _updater(self):
            pass


    init_state = {'ID': '3265',
                  'name': 'Pump',
                  'ackn': False,
                  'error': False,
                  'feedback': EnableDevFeedbacks.STOP,
                  'contactor feedback': False,
                  'enabled': True,
                  'run request': False,
                  'available': True,
                  'cont on': False,
                  'cont no fdbk timer': None,
                  'cont fdbk not off timer': None,
                  'curr state': ContactorStates.CHECK_AVAILABILITY,
                  'prev state': ContactorStates.STANDBY,
                  'state entry time': None,
                  'raised errors': {ContactorErrorMessages.NO_FEEDBACK_WHEN_RUN: False},
                  'raised warnings': {ContactorWarningMessages.CANT_STOP_CONTACTOR: False},
                  'status': OnOffDeviceStatuses.STANDBY
                  }


    def reducer(state=None, action=None):
        if state is None:
            state = {}
        elif action['type'] == 'pump/UPDATE':
            new_state = {**state, **(action['payload'])}
            return new_state
        else:
            return state

    store = pydux.create_store(reducer, init_state)

    app = QApplication([])

    window = MainWindow(store)
    controller = ContController(store)

    window.show()

    app.exec()
