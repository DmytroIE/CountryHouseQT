from src.controller.ContactorStrategy import contactor_strategy
from src.utils.WateringStatuses import *

def univ_pump_cont_strategy(pump_cont):
    run_req_from_watering = pump_cont['run req from watering']
    run_req_from_button = pump_cont['run request']
    run_request = run_req_from_watering or run_req_from_button

    enabled_for_watering = pump_cont['enabled for watering']
    enabled_for_button = pump_cont['enabled']
    enabled = enabled_for_watering or enabled_for_button

    contactor = pump_cont.copy()
    contactor['run request'] = run_request
    contactor['enabled'] = enabled
    contactor['feedback'] = EnableDevFeedbacks.PENDING

    cont_updated_outputs, alarm_log_batch = contactor_strategy(contactor)

    feedback_for_watering = cont_updated_outputs['feedback']
    if not run_req_from_watering:
        if cont_updated_outputs['feedback'] is EnableDevFeedbacks.RUN:
            feedback_for_watering = EnableDevFeedbacks.NOT_STOP
        elif cont_updated_outputs['feedback'] is EnableDevFeedbacks.NOT_RUN:
            feedback_for_watering = EnableDevFeedbacks.STOP
    else:
        if cont_updated_outputs['feedback'] is EnableDevFeedbacks.STOP:
            feedback_for_watering = EnableDevFeedbacks.NOT_RUN
        elif cont_updated_outputs['feedback'] is EnableDevFeedbacks.NOT_STOP:
            feedback_for_watering = EnableDevFeedbacks.RUN
    cont_updated_outputs['feedback for watering'] = feedback_for_watering

    feedback_for_button = cont_updated_outputs['feedback']
    if not run_req_from_button:
        if cont_updated_outputs['feedback'] is EnableDevFeedbacks.RUN:
            feedback_for_button = EnableDevFeedbacks.NOT_STOP
        elif cont_updated_outputs['feedback'] is EnableDevFeedbacks.NOT_RUN:
            feedback_for_button = EnableDevFeedbacks.STOP
    else:
        if cont_updated_outputs['feedback'] is EnableDevFeedbacks.STOP:
            feedback_for_button = EnableDevFeedbacks.NOT_RUN
        elif cont_updated_outputs['feedback'] is EnableDevFeedbacks.NOT_STOP:
            feedback_for_button = EnableDevFeedbacks.RUN
    cont_updated_outputs['feedback'] = feedback_for_button

    # обновляем выходы
    return cont_updated_outputs, alarm_log_batch


if __name__ == '__main__':
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import \
        QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextBrowser
    import pydux
    from src.store.ConnectedComponent import ConnectedComponent
    from src.utils.Buttons import *

    keys_to_print = ['error', 'feedback for watering', 'feedback', 'available',
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
            # state = self._get_own_state()

            self.setWindowTitle("Test Pump Strategy")
            self.setGeometry(0, 0, 640, 480)

            self._wdg_central = QWidget()
            self._lyt_main = QVBoxLayout(self._wdg_central)

            self._updated_widgets_map = {}

            self._btn_enable_for_b = QPushButton('Enable for b')
            self._btn_enable_for_b.clicked.connect(
                lambda: self._dispatch({'type': 'pump/UPDATE',
                                        'payload':
                                            {'enabled': not self._get_own_state()['enabled']}
                                        }))
            self._updated_widgets_map['enabled'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_enable_for_b,
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

            self._btn_run_for_b = QPushButton('Run')
            self._btn_run_for_b.clicked.connect(
                lambda: self._dispatch({'type': 'pump/UPDATE',
                                        'payload':
                                            {'run request': not self._get_own_state()['run request']}
                                        }))
            self._updated_widgets_map['run request'] = \
                lambda x: change_toggle_button_style(x,
                                                     self._btn_run_for_b,
                                                     'StandardButton',
                                                     'StandardButton EnabledButton')

            self._btn_run_for_w = QPushButton('Run for w')
            self._btn_run_for_w.clicked.connect(
                lambda: self._dispatch({'type': 'pump/UPDATE',
                                        'payload':
                                            {'run req from watering': not self._get_own_state()['run req from watering']}
                                        }))
            self._updated_widgets_map['run req from watering'] = \
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
            self._lyt_first.addWidget(self._btn_enable_for_b)
            self._lyt_first.addWidget(self._btn_run_for_b)
            self._lyt_first.addWidget(self._btn_cont_fdbk)

            self._lyt_second = QHBoxLayout()
            self._lyt_second.addWidget(self._btn_enable_for_w)
            self._lyt_second.addWidget(self._btn_run_for_w)
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
                new_state_chunk, alarm_log_batch = univ_pump_cont_strategy(state)
                self._dispatch({'type': 'pump/UPDATE', 'payload': new_state_chunk})
                for item in alarm_log_batch:
                    print(f'{item["dt_stamp"].toString("dd.MM.yy mm:ss")} {item["text"]}')
            except Exception as e:
                print(f'Ошибка выполнения автомата, {e}')

        def _updater(self):
            pass

    init_state = {'ID': '1336',
                  'name': 'UnivPump',
                  'ackn': False,
                  'error': False,
                  'feedback for watering': EnableDevFeedbacks.STOP,
                  'feedback': EnableDevFeedbacks.STOP,
                  'contactor feedback': False,
                  'enabled for watering': True,
                  'enabled': True,
                  'run req from watering': False,
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
