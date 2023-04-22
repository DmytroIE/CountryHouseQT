from src.controller.ContactorStrategy import ContactorStrategy
from src.utils.WateringStatuses import *


class SplitInputDecorator:
    def __init__(self, strategy, num_of_inputs):
        self._strategy = strategy
        self._num_of_inputs = num_of_inputs

    @property
    def init_data(self):
        init_data = self._strategy.init_data
        init_data['run_req'] = [False for i in range(self._num_of_inputs)]
        init_data['feedback'] = [EnableDevFeedbacks.STOP for i in range(self._num_of_inputs)]
        return init_data

    @property
    def ID(self):
        return self._strategy.ID

    def run(self, own_state):
        enabled = False
        run_req = False
        for i in range(self._num_of_inputs):
            enabled = enabled or own_state['enabled'][i]
            run_req = run_req or (own_state['enabled'][i] and own_state['run_req'][i])

        state = own_state.copy()
        state['run_req'] = run_req
        state['enabled'] = enabled
        state['feedback'] = None
        state['available'] = None
        # print(f'{state=}')
        checked_outputs, alarm_log_batch = self._strategy.run(state)
        # print(f'{checked_outputs=}')
        if 'feedback' in checked_outputs.keys():
            feedback = [checked_outputs['feedback'] for i in range(self._num_of_inputs)]
            for i in range(self._num_of_inputs):
                if not own_state['run_req'][i]:
                    if feedback[i] is EnableDevFeedbacks.RUN:
                        feedback[i] = EnableDevFeedbacks.NOT_STOP
                    elif feedback[i] is EnableDevFeedbacks.NOT_RUN:
                        feedback[i] = EnableDevFeedbacks.STOP
                else:
                    if feedback[i] is EnableDevFeedbacks.STOP:
                        feedback[i] = EnableDevFeedbacks.NOT_RUN
                    elif feedback[i] is EnableDevFeedbacks.NOT_STOP:
                        feedback[i] = EnableDevFeedbacks.RUN
            if own_state['feedback'] != feedback:
                checked_outputs['feedback'] = feedback
            else:
                del checked_outputs['feedback']

        if 'available' in checked_outputs.keys():
            available = [checked_outputs['available'] and own_state['enabled'][i] for i in range(self._num_of_inputs)]
            if own_state['available'] != available:
                checked_outputs['available'] = available
            else:
                del checked_outputs['available']

        # print(f'{checked_outputs=}')
        return checked_outputs, alarm_log_batch


if __name__ == '__main__':
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import \
        QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextBrowser
    from collections import OrderedDict
    from src.store.ConnectedToStoreComponent import ConnectedToStoreComponent
    from src.ConnectedToStoreApplication import ConnectedToStoreApplication
    from src.utils.Buttons import *

    keys_to_print = ['ackn', 'error', 'available', 'enabled', 'cont_on', 'feedback', 'status']


    def root_reducer(state=None, action=None):
        if state is None:
            state = {}
        if action['type'] == 'contactors/UPDATE_ITEM':
            cont_id = action['payload']['ID']
            new_state = state.copy()
            new_state[cont_id] = {**new_state[cont_id], **(action['payload']['new_data'])}
            return new_state
        else:
            return state


    default_state = OrderedDict({'vv3GJie1':
                                     {'ID': 'vv3GJie1',
                                      'name': 'Насос',
                                      'ackn': False,
                                      'error': False,
                                      'cont_on': False,
                                      'cont_feedback': False,
                                      'enabled': [True, True],
                                      'run_req': [False, False],
                                      'available': [True, True],
                                      'feedback': [EnableDevFeedbacks.STOP, EnableDevFeedbacks.STOP],
                                      'raised_errors': {ContactorErrorMessages.NO_FEEDBACK_WHEN_RUN: False},
                                      'raised_warnings': {ContactorWarningMessages.CANT_STOP_CONTACTOR: False},
                                      'status': OnOffDeviceStatuses.STANDBY
                                      }})


    class MainWindow(ConnectedToStoreComponent, QMainWindow):
        def __init__(self):
            QMainWindow.__init__(self)
            ConnectedToStoreComponent.__init__(self)

            self._create_ui()
            self._updater()

        def _get_own_state(self):  # selector
            return self._get_store_state()['vv3GJie1']

        def _on_state_update(self, new_state, updated_keys_list, action):
            if action == 'ADD' or action == 'UPDATE':
                # print(f'{new_state}')

                change_toggle_button_style(new_state['enabled'][0],
                                           self._btn_enable_for_b,
                                           'StandardButton',
                                           'StandardButton EnabledButton')
                change_toggle_button_style(new_state['enabled'][1],
                                           self._btn_enable_for_w,
                                           'StandardButton',
                                           'StandardButton EnabledButton')
                change_toggle_button_style(new_state['run_req'][0],
                                           self._btn_run_for_b,
                                           'StandardButton',
                                           'StandardButton EnabledButton')
                change_toggle_button_style(new_state['run_req'][1],
                                           self._btn_run_for_w,
                                           'StandardButton',
                                           'StandardButton EnabledButton')
                change_toggle_button_style(new_state['cont_feedback'],
                                           self._btn_cont_fdbk,
                                           'StandardButton',
                                           'StandardButton EnabledButton')
                change_toggle_button_style(new_state['ackn'],
                                           self._btn_ackn,
                                           'StandardButton',
                                           'StandardButton EnabledButton')

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

            self.setWindowTitle("Test Univ Pump Strategy")
            self.setGeometry(0, 0, 640, 480)

            self._wdg_central = QWidget()
            self._lyt_main = QVBoxLayout(self._wdg_central)

            self._btn_enable_for_b = QPushButton('Enable for b')
            self._btn_enable_for_b.clicked.connect(
                lambda: self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                        'payload':
                                            {'ID': 'vv3GJie1',
                                             'new_data':
                                                 {'enabled':
                                                      [self._get_own_state()['enabled'][i] if i != 0 else not
                                                      self._get_own_state()['enabled'][i] for i in
                                                       range(len(self._get_own_state()['enabled']))]}
                                             }}))

            self._btn_enable_for_w = QPushButton('Enable for w')
            self._btn_enable_for_w.clicked.connect(
                lambda: self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                        'payload':
                                            {'ID': 'vv3GJie1',
                                             'new_data':
                                                 {'enabled':
                                                      [self._get_own_state()['enabled'][i] if i != 1 else not
                                                      self._get_own_state()['enabled'][i] for i in
                                                       range(len(self._get_own_state()['enabled']))]}
                                             }}))

            self._btn_run_for_b = QPushButton('Run for b')
            self._btn_run_for_b.clicked.connect(
                lambda: self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                        'payload':
                                            {'ID': 'vv3GJie1',
                                             'new_data':
                                                 {'run_req':
                                                      [self._get_own_state()['run_req'][i] if i != 0 else not
                                                      self._get_own_state()['run_req'][i] for i in
                                                       range(len(self._get_own_state()['run_req']))]}
                                             }}))

            self._btn_run_for_w = QPushButton('Run for w')
            self._btn_run_for_w.clicked.connect(
                lambda: self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                        'payload':
                                            {'ID': 'vv3GJie1',
                                             'new_data':
                                                 {'run_req':
                                                      [self._get_own_state()['run_req'][i] if i != 1 else not
                                                      self._get_own_state()['run_req'][i] for i in
                                                       range(len(self._get_own_state()['run_req']))]}
                                             }}))

            self._btn_cont_fdbk = QPushButton('Cont fdbk')
            self._btn_cont_fdbk.clicked.connect(
                lambda: self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                        'payload':
                                            {'ID': 'vv3GJie1',
                                             'new_data':
                                                 {'cont_feedback': not self._get_own_state()['cont_feedback']}
                                             }}))

            self._btn_ackn = QPushButton('Ackn')
            self._btn_ackn.clicked.connect(
                lambda: self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                        'payload':
                                            {'ID': 'vv3GJie1',
                                             'new_data':
                                                 {'ackn': not self._get_own_state()['ackn']}
                                             }}))

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

        def closeEvent(self, event):
            appl = QApplication.instance()
            appl.save_store_on_exit()


    class ContController(ConnectedToStoreComponent):
        def __init__(self):
            ConnectedToStoreComponent.__init__(self)
            self._contactor = SplitInputDecorator(ContactorStrategy('vv3GJie1'), 2)
            self._one_second_timer = QTimer()
            self._one_second_timer.timeout.connect(self._on_timer_tick)
            self._one_second_timer.start(1000)
            self._dispatch({'type': 'contactors/UPDATE_ITEM',
                            'payload': {'ID': self._contactor.ID,
                                        'new_data': self._contactor.init_data
                                        }})

        def _on_timer_tick(self):
            try:
                cont_state = self._get_store_state()[self._contactor.ID]
                checked_outputs, alarm_log_batch = self._contactor.run(cont_state)
                # print(f'{checked_outputs=}')
                if checked_outputs:
                    self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                    'payload': {'ID': self._contactor.ID,
                                                'new_data': checked_outputs}})
                if alarm_log_batch:
                    for item in alarm_log_batch:
                        print(f'{item["dt_stamp"].toString("dd.MM.yy mm:ss")} {item["text"]}')

            except Exception as e:
                print(f'Ошибка выполнения автомата, {e}')

        def _updater(self):
            pass


    app = ConnectedToStoreApplication(root_reducer, default_state)

    controller = ContController()

    window = MainWindow()
    window.show()

    app.exec()
