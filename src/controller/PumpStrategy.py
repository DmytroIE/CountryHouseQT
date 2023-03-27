from PyQt5.QtCore import QTime, QDateTime
from string import Template

from src.utils.WateringStatuses import *

SP_DELAY = 5  # in seconds


class ContactorUnivPumpStates(Enum):
    PENDING = 0
    CHECKING_AVAILABILITY = 1
    STARTUP = 100
    RUN = 10
    DONE = 200
    RUNNING_DISRUPTED = 201
    SHUTDOWN = 202
    SHUTDOWN_ERROR = 290


class ContactorUnivPumpAlarmMessages(Enum):
    NO_FEEDBACK_WHEN_RUN = {'ID': 'tCoPB053',
                            'text': Template('Авария контактора насоса $name'),
                            'active': False}
    CANT_STOP_CONTACTOR = {'ID': 'oC1wQuu5',
                           'text': Template('Невозможно отключить контактор насоса $name'),
                           'active': False}


def contactor_univ_pump_strategy(contactor):
    pump_id = contactor['ID']
    name = contactor['name']
    ackn = contactor['ackn']
    error = contactor['error']
    feedback = contactor['feedback']
    feedback_for_watering = contactor['feedback for watering']
    contactor_feedback = contactor['contactor feedback']
    enabled = contactor['enabled']
    enabled_for_watering = contactor['enabled for watering']
    run_request = contactor['run request']
    run_request_for_watering = contactor['run request for watering']
    available = contactor['available']
    available_for_watering = contactor['available for watering']
    pump_on = contactor['pump on']
    timer_init_time = contactor['timer init time']
    curr_state = contactor['curr state']
    prev_state = contactor['prev state']
    state_entry_time = contactor['state entry time']
    alarm_log_batch = []
    message_passed_to_log = None
    curr_time = None  # используется, когда нужно тек. время несколько раз в шаге,
    # чтобы не вызывать постоянно QTime.currentTime()

    # Квитирование
    if ackn:
        if error:
            error = False
            poss_error = ContactorUnivPumpAlarmMessages.NO_FEEDBACK_WHEN_RUN
            poss_error.value['active'] = False
            alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_OUT,
                                    'ID': pump_id + poss_error.value['ID'],
                                    'dt_stamp': QDateTime.currentDateTime(),
                                    'text': poss_error.value['text'].substitute(name=name)})
        ackn = False

    # Автомат
    while True:
        again = False

        if curr_state is ContactorUnivPumpStates.PENDING:
            prev_state_temp = prev_state
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                if prev_state is not ContactorUnivPumpStates.CHECKING_AVAILABILITY:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': QDateTime.currentDateTime(),
                                            'text': f'Контактор насоса {name} отключен'})
                if run_request:
                    feedback = OnOffDevFeedbacks.NOT_RUN
                else:
                    feedback = OnOffDevFeedbacks.STOP
                if run_request_for_watering:
                    feedback_for_watering = OnOffDevFeedbacks.NOT_RUN
                else:
                    feedback_for_watering = OnOffDevFeedbacks.STOP
                prev_state = curr_state

            # Переходы
            if prev_state_temp is ContactorUnivPumpStates.CHECKING_AVAILABILITY:
                curr_state = ContactorUnivPumpStates.CHECKING_AVAILABILITY
                again = False
            else:
                curr_state = ContactorUnivPumpStates.CHECKING_AVAILABILITY
                again = True

        elif curr_state is ContactorUnivPumpStates.CHECKING_AVAILABILITY:
            # Этот шаг исполняется один раз
            prev_state = curr_state

            if available:
                if not enabled:
                    available = False
            else:
                if enabled and not error:
                    available = True

            if available_for_watering:
                if not enabled_for_watering:
                    available_for_watering = False
            else:
                if enabled_for_watering and not error:
                    available_for_watering = True

            # Переходы
            if (available and run_request) or \
                    (available_for_watering and run_request_for_watering):
                poss_warning = ContactorUnivPumpAlarmMessages.CANT_STOP_CONTACTOR
                if poss_warning.value['active']:
                    poss_warning.value['active'] = False
                    alarm_log_batch.append({'type': LogAlarmMessageTypes.WARNING_OUT,
                                            'ID': pump_id + poss_warning.value['ID'],
                                            'dt_stamp': QDateTime.currentDateTime(),
                                            'text': poss_warning.value['text'].substitute(name=name)})
                curr_state = ContactorUnivPumpStates.STARTUP
                again = True
            elif contactor_feedback:
                curr_state = ContactorUnivPumpStates.SHUTDOWN_ERROR
                again = True
            else:
                curr_state = ContactorUnivPumpStates.PENDING
                again = True

        elif curr_state is ContactorUnivPumpStates.STARTUP:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Запуск контактора насоса {name}'})
                pump_on = True
                feedback = OnOffDevFeedbacks.PENDING
                feedback_for_watering = OnOffDevFeedbacks.PENDING
                state_entry_time = QTime.currentTime()
                timer_init_time = None
                prev_state = curr_state

            # Постоянные действия
            curr_time = QTime.currentTime()
            # Timer
            if not contactor_feedback:
                if not timer_init_time:
                    timer_init_time = curr_time
            else:
                if timer_init_time and timer_init_time.secsTo(curr_time) < SP_DELAY:
                    timer_init_time = None

            # Переходы
            if (not run_request) and (not run_request_for_watering):
                curr_state = ContactorUnivPumpStates.SHUTDOWN
                again = True
            elif (not enabled) and (not enabled_for_watering):
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Насос {name} отключен во время запуска'})
                available = False
                available_for_watering = False
                curr_state = ContactorUnivPumpStates.SHUTDOWN
                again = True
            elif timer_init_time and timer_init_time.secsTo(curr_time) > SP_DELAY:
                curr_error = ContactorUnivPumpAlarmMessages.NO_FEEDBACK_WHEN_RUN
                curr_error.value['active'] = True
                alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_IN,
                                        'ID': pump_id + curr_error.value['ID'],
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': curr_error.value['text'].substitute(name=name)})
                error = True
                available = False
                available_for_watering = False
                curr_state = ContactorUnivPumpStates.SHUTDOWN
                again = True
            elif contactor_feedback and \
                    state_entry_time.secsTo(QTime.currentTime()) > 2:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = ContactorUnivPumpStates.RUN
                again = True

        elif curr_state is ContactorUnivPumpStates.RUN:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Контактор насоса {name} запущен'})
                if run_request:
                    feedback = OnOffDevFeedbacks.RUN
                else:
                    feedback = OnOffDevFeedbacks.NOT_STOP
                if run_request_for_watering:
                    feedback_for_watering = OnOffDevFeedbacks.RUN
                else:
                    feedback_for_watering = OnOffDevFeedbacks.NOT_STOP
                timer_init_time = None
                prev_state = curr_state

            # Постоянные действия
            curr_time = QTime.currentTime()
            if not contactor_feedback:
                if not timer_init_time:
                    timer_init_time = curr_time
            else:
                if timer_init_time and timer_init_time.secsTo(curr_time) < SP_DELAY:
                    timer_init_time = None

            # Переходы
            if (not run_request) and (not run_request_for_watering):
                curr_state = ContactorUnivPumpStates.SHUTDOWN
                again = True
            elif (not enabled) and (not enabled_for_watering):
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Насос {name} отключен во время работы'})
                available = False
                available_for_watering = False
                curr_state = ContactorUnivPumpStates.SHUTDOWN
                again = True
            elif timer_init_time and timer_init_time.secsTo(curr_time) > SP_DELAY:
                curr_error = ContactorUnivPumpAlarmMessages.NO_FEEDBACK_WHEN_RUN
                curr_error.value['active'] = True
                alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_IN,
                                        'ID': pump_id + curr_error.value['ID'],
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': curr_error.value['text'].substitute(name=name)})
                error = True
                available = False
                available_for_watering = False
                curr_state = ContactorUnivPumpStates.SHUTDOWN
                again = True

        elif curr_state is ContactorUnivPumpStates.SHUTDOWN:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Отключение контактора насоса {name}'})
                pump_on = False
                feedback = OnOffDevFeedbacks.PENDING
                feedback_for_watering = OnOffDevFeedbacks.PENDING
                # state_entry_time = QTime.currentTime()
                timer_init_time = None
                prev_state = curr_state

            # Постоянные действия
            curr_time = QTime.currentTime()
            if contactor_feedback:
                if not timer_init_time:
                    timer_init_time = curr_time
            else:
                if timer_init_time and timer_init_time.secsTo(curr_time) < SP_DELAY:
                    timer_init_time = None

            # Переходы
            if run_request or run_request_for_watering:
                if not error:
                    curr_state = ContactorUnivPumpStates.CHECKING_AVAILABILITY
                else:
                    curr_state = ContactorUnivPumpStates.PENDING
                again = True
            elif timer_init_time and timer_init_time.secsTo(curr_time) > SP_DELAY:
                curr_state = ContactorUnivPumpStates.SHUTDOWN_ERROR
                again = True
            elif not contactor_feedback:
                curr_state = ContactorUnivPumpStates.PENDING
                again = True

        elif curr_state is ContactorUnivPumpStates.SHUTDOWN_ERROR:
            prev_state_temp = prev_state
            if curr_state is not prev_state:
                curr_error = ContactorUnivPumpAlarmMessages.CANT_STOP_CONTACTOR
                if not curr_error.value['active']:
                    curr_error.value['active'] = True
                    alarm_log_batch.append({'type': LogAlarmMessageTypes.WARNING_IN,
                                            'ID': pump_id + curr_error.value['ID'],
                                            'dt_stamp': QDateTime.currentDateTime(),
                                            'text': curr_error.value['text'].substitute(name=name)})
                    if run_request:
                        feedback = OnOffDevFeedbacks.RUN
                    else:
                        feedback = OnOffDevFeedbacks.NOT_STOP
                    if run_request_for_watering:
                        feedback_for_watering = OnOffDevFeedbacks.RUN
                    else:
                        feedback_for_watering = OnOffDevFeedbacks.NOT_STOP
                prev_state = curr_state

            # Переходы
            if prev_state_temp is ContactorUnivPumpStates.CHECKING_AVAILABILITY:
                curr_state = ContactorUnivPumpStates.SHUTDOWN_ERROR
                again = False
            elif run_request or run_request_for_watering:
                curr_state = ContactorUnivPumpStates.CHECKING_AVAILABILITY
                again = True
            elif not contactor_feedback:
                curr_state = ContactorUnivPumpStates.PENDING
                again = True

        if not again:
            break

    # обновляем выходы
    return {'ackn': ackn,
            'error': error,
            'feedback': feedback,
            'feedback for watering': feedback_for_watering,
            'contactor feedback': contactor_feedback,
            'available': available,
            'available for watering': available_for_watering,
            'pump on': pump_on,
            'timer init time': timer_init_time,
            'curr state': curr_state,
            'prev state': prev_state,
            'state entry time': state_entry_time
            }, alarm_log_batch


if __name__ == '__main__':
    from PyQt5.QtCore import QSize, Qt, QTimer
    from PyQt5.QtWidgets import \
        QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextBrowser
    import pydux
    from src.store.ConnectedComponent import ConnectedComponent
    from src.utils.Buttons import *

    keys_to_print = ['error', 'feedback', 'feedback for watering', 'available', 'available for watering',
                     'pump on', 'curr state', 'prev state', 'timer init time']

    class MainWindow(ConnectedComponent, QMainWindow):
        def __init__(self, store1):
            QMainWindow.__init__(self)
            ConnectedComponent.__init__(self, store1)

            self._create_ui()

            # self._dispatch({'type': 'pump/INIT_UPDATE'})
            self._updater()

        def _get_own_state(self):  # selector
            return self._get_store_state()

        def _on_state_update(self, new_state, updated_keys_list, action):
            if action == 'ADD' or action == 'UPDATE':
                # print(updated_keys_list)
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

            self._btn_enable_for_w = QPushButton('Enable for w')
            self._btn_enable_for_w.clicked.connect(
                lambda: self._dispatch({'type': 'pump/UPDATE',
                                        'payload':
                                            {'enabled for watering': not self._get_own_state()['enabled for watering']}
                                        }))
            self._updated_widgets_map['enabled for watering'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_enable_for_w,
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

            self._btn_run_for_w = QPushButton('Run for w')
            self._btn_run_for_w.clicked.connect(
                lambda: self._dispatch({'type': 'pump/UPDATE',
                                        'payload':
                                            {'run request for watering':
                                                 not self._get_own_state()['run request for watering']}
                                        }))
            self._updated_widgets_map['run request for watering'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_run_for_w,
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
            self._lyt_first.addWidget(self._btn_enable_for_w)
            self._lyt_first.addWidget(self._btn_run)
            self._lyt_first.addWidget(self._btn_run_for_w)

            self._lyt_second = QHBoxLayout()
            self._lyt_second.addWidget(self._btn_cont_fdbk)
            self._lyt_second.addWidget(self._btn_ackn)

            self._txt_view = QTextBrowser()

            self._lyt_main.addLayout(self._lyt_first)
            self._lyt_main.addLayout(self._lyt_second)
            self._lyt_main.addWidget(self._txt_view)

            self.setCentralWidget(self._wdg_central)

    class PumpController(ConnectedComponent):
        def __init__(self, store1):
            ConnectedComponent.__init__(self, store1)
            self._one_second_timer = QTimer()
            self._one_second_timer.timeout.connect(self._on_timer_tick)
            self._one_second_timer.start(1000)

        def _on_timer_tick(self):
            state = self._get_store_state()
            new_state_chunk, batch = contactor_univ_pump_strategy(state)
            self._dispatch({'type': 'pump/UPDATE', 'payload': new_state_chunk})
            for item in batch:
                print(f'{item["dt_stamp"].toString("dd.MM.yy mm:ss")} {item["text"]}')
            # self._dispatch({'type': 'pump/UPDATE', 'payload': {'timer init time': QTime.currentTime()}})

        def _updater(self):
            pass

    init_state = {'ID': '3265',
                  'name': 'Pump',
                  'ackn': False,
                  'error': False,
                  'feedback': OnOffDevFeedbacks.STOP,
                  'feedback for watering': OnOffDevFeedbacks.STOP,
                  'contactor feedback': False,
                  'enabled': True,
                  'enabled for watering': True,
                  'run request': False,
                  'run request for watering': False,
                  'available': True,
                  'available for watering': True,
                  'pump on': False,
                  'timer init time': None,
                  'curr state': ContactorUnivPumpStates.PENDING,
                  'prev state': ContactorUnivPumpStates.PENDING,
                  'state entry time': None
                  }


    def reducer(state=None, action=None):
        if state is None:
            state = {}
        elif action['type'] == 'pump/UPDATE':
            new_state = {**state, **(action['payload'])}
            return new_state
        # elif action['type'] == 'pump/INIT_UPDATE':
        #     new_state = state.copy()
        #     return new_state
        else:
            return state


    store = pydux.create_store(reducer, init_state)

    app = QApplication([])

    window = MainWindow(store)
    controller = PumpController(store)

    window.show()

    app.exec()
