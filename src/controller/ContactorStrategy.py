from PyQt5.QtCore import QTime, QDateTime
from string import Template

from src.utils.WateringStatuses import *

SP_DELAY = 5  # in seconds


class ContactorStates(Enum):
    PENDING = 0
    CHECKING_AVAILABILITY = 1
    STARTUP = 100
    RUN = 10
    SHUTDOWN = 200
    SHUTDOWN_ERROR = 290


class ContactorAlarmMessages(Enum):
    NO_FEEDBACK_WHEN_RUN = {'ID': 'rF0b0Aq_',
                            'text': Template('Авария контактора $name'),
                            'active': False}
    CANT_STOP_CONTACTOR = {'ID': '9JUl1EB5',
                           'text': Template('Невозможно отключить контактор $name'),
                           'active': False}


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
    timer_init_time = contactor['timer init time']
    curr_state = contactor['curr state']
    prev_state = contactor['prev state']
    state_entry_time = contactor['state entry time']
    alarm_log_batch = []

    # Квитирование
    if ackn:
        if error:
            error = False
            poss_error = ContactorAlarmMessages.NO_FEEDBACK_WHEN_RUN
            poss_error.value['active'] = False
            alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_OUT,
                                    'ID': cont_id + poss_error.value['ID'],
                                    'dt_stamp': QDateTime.currentDateTime(),
                                    'text': poss_error.value['text'].substitute(name=name)})
        ackn = False

    # Автомат
    while True:
        again = False

        if curr_state is ContactorStates.PENDING:
            # prev_state_temp = prev_state
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                if prev_state is not ContactorStates.CHECKING_AVAILABILITY:
                    poss_warning = ContactorAlarmMessages.CANT_STOP_CONTACTOR
                    if poss_warning.value['active']:
                        poss_warning.value['active'] = False
                        alarm_log_batch.append({'type': LogAlarmMessageTypes.WARNING_OUT,
                                                'ID': cont_id + poss_warning.value['ID'],
                                                'dt_stamp': QDateTime.currentDateTime(),
                                                'text': poss_warning.value['text'].substitute(name=name)})
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': QDateTime.currentDateTime(),
                                            'text': f'Контактор насоса {name} отключен'})
                feedback = OnOffDevFeedbacks.STOP
                prev_state = curr_state

            # Переходы
            if available and run_request:
                curr_state = ContactorStates.STARTUP
                again = True
            elif contactor_feedback:
                curr_state = ContactorStates.SHUTDOWN_ERROR
                again = True
            else:
                curr_state = ContactorStates.CHECKING_AVAILABILITY
                again = False

        elif curr_state is ContactorStates.CHECKING_AVAILABILITY:
            # Этот шаг исполняется один раз

            if not enabled or error:
                available = False
            else:
                available = True

            # Переходы
            curr_state = prev_state
            prev_state = ContactorStates.CHECKING_AVAILABILITY
            again = True

        elif curr_state is ContactorStates.STARTUP:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                if prev_state is not ContactorStates.CHECKING_AVAILABILITY:
                    poss_warning = ContactorAlarmMessages.CANT_STOP_CONTACTOR
                    if poss_warning.value['active']:
                        poss_warning.value['active'] = False
                        alarm_log_batch.append({'type': LogAlarmMessageTypes.WARNING_OUT,
                                                'ID': cont_id + poss_warning.value['ID'],
                                                'dt_stamp': QDateTime.currentDateTime(),
                                                'text': poss_warning.value['text'].substitute(name=name)})
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': QDateTime.currentDateTime(),
                                            'text': f'Запуск контактора {name}'})
                    cont_on = True
                    feedback = OnOffDevFeedbacks.PENDING
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
            if not run_request:
                curr_state = ContactorStates.SHUTDOWN
                again = True
            elif not available:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Контактор {name} отключен во время запуска'})
                curr_state = ContactorStates.SHUTDOWN
                again = True
            elif timer_init_time and timer_init_time.secsTo(curr_time) > SP_DELAY:
                curr_error = ContactorAlarmMessages.NO_FEEDBACK_WHEN_RUN
                curr_error.value['active'] = True
                alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_IN,
                                        'ID': cont_id + curr_error.value['ID'],
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': curr_error.value['text'].substitute(name=name)})
                error = True
                available = False
                curr_state = ContactorStates.SHUTDOWN
                again = True
            elif contactor_feedback and \
                    state_entry_time.secsTo(QTime.currentTime()) > 2:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = ContactorStates.RUN
                again = True
            else:
                curr_state = ContactorStates.CHECKING_AVAILABILITY
                again = False

        elif curr_state is ContactorStates.RUN:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                if prev_state is not ContactorStates.CHECKING_AVAILABILITY:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': QDateTime.currentDateTime(),
                                            'text': f'Контактор насоса {name} запущен'})
                    feedback = OnOffDevFeedbacks.RUN

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
            if not run_request:
                curr_state = ContactorStates.SHUTDOWN
                again = True
            elif not available:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': f'Насос {name} отключен во время работы'})
                curr_state = ContactorStates.SHUTDOWN
                again = True
            elif timer_init_time and timer_init_time.secsTo(curr_time) > SP_DELAY:
                curr_error = ContactorAlarmMessages.NO_FEEDBACK_WHEN_RUN
                curr_error.value['active'] = True
                alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_IN,
                                        'ID': cont_id + curr_error.value['ID'],
                                        'dt_stamp': QDateTime.currentDateTime(),
                                        'text': curr_error.value['text'].substitute(name=name)})
                error = True
                available = False
                curr_state = ContactorStates.SHUTDOWN
                again = True
            else:
                curr_state = ContactorStates.CHECKING_AVAILABILITY
                again = False

        elif curr_state is ContactorStates.SHUTDOWN:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                if prev_state is not ContactorStates.CHECKING_AVAILABILITY:
                    alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                            'dt_stamp': QDateTime.currentDateTime(),
                                            'text': f'Отключение контактора {name}'})
                    cont_on = False
                    feedback = OnOffDevFeedbacks.PENDING
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
            if run_request and available:
                curr_state = ContactorStates.STARTUP
                again = True
            elif timer_init_time and timer_init_time.secsTo(curr_time) > SP_DELAY:
                curr_state = ContactorStates.SHUTDOWN_ERROR
                again = True
            elif not contactor_feedback:
                curr_state = ContactorStates.PENDING
                again = True
            else:
                curr_state = ContactorStates.CHECKING_AVAILABILITY
                again = False

        elif curr_state is ContactorStates.SHUTDOWN_ERROR:

            if curr_state is not prev_state:
                if prev_state is not ContactorStates.CHECKING_AVAILABILITY:
                    curr_error = ContactorAlarmMessages.CANT_STOP_CONTACTOR
                    if not curr_error.value['active']:
                        curr_error.value['active'] = True
                        alarm_log_batch.append({'type': LogAlarmMessageTypes.WARNING_IN,
                                                'ID': cont_id + curr_error.value['ID'],
                                                'dt_stamp': QDateTime.currentDateTime(),
                                                'text': curr_error.value['text'].substitute(name=name)})
                prev_state = curr_state

            if run_request:
                feedback = OnOffDevFeedbacks.RUN
            else:
                feedback = OnOffDevFeedbacks.NOT_STOP

            # Переходы
            if run_request and available:
                curr_state = ContactorStates.STARTUP
                again = True
            elif not contactor_feedback:
                curr_state = ContactorStates.PENDING
                again = True
            else:
                curr_state = ContactorStates.CHECKING_AVAILABILITY
                again = False

        if not again:
            break

    # обновляем выходы
    return {'ackn': ackn,
            'error': error,
            'feedback': feedback,
            'contactor feedback': contactor_feedback,
            'available': available,
            'cont on': cont_on,
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

    keys_to_print = ['error', 'feedback', 'available',
                     'cont on', 'curr state', 'prev state', 'timer init time']


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
                new_state_chunk, batch = contactor_strategy(state)
            except Exception as e:
                print(f'Ошибка выполнения автомата, {e}')
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
                  'contactor feedback': False,
                  'enabled': True,
                  'run request': False,
                  'available': True,
                  'cont on': False,
                  'timer init time': None,
                  'curr state': ContactorStates.CHECKING_AVAILABILITY,
                  'prev state': ContactorStates.PENDING,
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
    controller = ContController(store)

    window.show()

    app.exec()
