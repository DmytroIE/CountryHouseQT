from PyQt5.QtWidgets import \
    QDoubleSpinBox, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextBrowser
from src.store.store import ConnectedToStoreComponent
from src.utils.Buttons import *

pump_keys_to_print = ['available', 'error', 'cont on', 'feedback', 'feedback for watering',
                      'curr state', 'prev state', 'cont no fdbk timer', 'cont fdbk not off timer',
                      'status']
process_keys_to_print = ['available', 'error', 'feedback', 'act cycle', 'active zone id',
                         'ball valve on', 'curr state', 'prev state',
                         'status']


class TestWatering(ConnectedToStoreComponent, QWidget):
    def __init__(self):
        QWidget.__init__(self)
        ConnectedToStoreComponent.__init__(self)

        self._cached_pump = None # self._get_pump_state()
        self._cached_process = None # self._get_process_state()
        self._create_ui()

    def _updater(self):
        new_pump = self._get_store_state()['contactors']['vv3GJie1']
        if new_pump is not self._cached_pump:
            change_toggle_button_style(new_pump['enabled'],
                                       self._btn_enable,
                                       'StandardButton',
                                       'StandardButton EnabledButton')
            change_toggle_button_style(new_pump['enabled for watering'],
                                       self._btn_enable_for_w,
                                       'StandardButton',
                                       'StandardButton EnabledButton')
            change_toggle_button_style(new_pump['run request'],
                                       self._btn_run,
                                       'StandardButton',
                                       'StandardButton EnabledButton')
            change_toggle_button_style(new_pump['contactor feedback'],
                                       self._btn_cont_fdbk,
                                       'StandardButton',
                                       'StandardButton EnabledButton')
            new_text = [f'{k}: {new_pump[k]}' for k in pump_keys_to_print]
            self._txt_pump_view.setText('\n'.join(new_text))
            self._cached_pump = new_pump

        new_process = self._get_store_state()['watering']['process']
        if new_process is not self._cached_process:
            new_text = [f'{k}: {new_process[k]}' for k in process_keys_to_print]
            self._txt_process_view.setText('\n'.join(new_text))
            self._cached_process = new_process

    def _get_pump_state(self):
        return self._get_store_state()['contactors']['vv3GJie1']

    def _get_process_state(self):
        return self._get_store_state()['watering']['process']

    def _create_ui(self):
        self._lyt_main = QVBoxLayout(self)

        self._btn_enable = QPushButton('Enable')
        self._btn_enable.clicked.connect(
            lambda: self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                    'payload':
                                        {'ID': 'vv3GJie1',
                                         'new_data': {'enabled': not self._get_pump_state()['enabled']}
                                         }}))

        self._btn_enable_for_w = QPushButton('Enable for w')
        self._btn_enable_for_w.clicked.connect(
            lambda: self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                    'payload':
                                        {'ID': 'vv3GJie1',
                                         'new_data': {'enabled for watering': not self._get_pump_state()['enabled for '
                                                                                                         'watering']}
                                         }}))

        self._btn_run = QPushButton('Run')
        self._btn_run.clicked.connect(
            lambda: self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                    'payload':
                                        {'ID': 'vv3GJie1',
                                         'new_data': {'run request': not self._get_pump_state()['run request']}
                                         }}))

        self._btn_cont_fdbk = QPushButton('Cont fdbk')
        self._btn_cont_fdbk.clicked.connect(
            lambda: self._dispatch({'type': 'contactors/UPDATE_ITEM',
                                    'payload':
                                        {'ID': 'vv3GJie1',
                                         'new_data': {'contactor feedback': not self._get_pump_state()['contactor '
                                                                                                       'feedback']}
                                         }}))

        self._lyt_first = QHBoxLayout()
        self._lyt_first.addWidget(self._btn_enable)
        self._lyt_first.addWidget(self._btn_run)

        self._lyt_second = QHBoxLayout()
        self._lyt_second.addWidget(self._btn_enable_for_w)
        self._lyt_second.addWidget(self._btn_cont_fdbk)

        self._txt_pump_view = QTextBrowser()
        pump = self._get_pump_state()
        # new_text = [f'{k}: {pump[k]}' for k in pump_keys_to_print]
        # self._txt_pump_view.setText('\n'.join(new_text))

        process = self._get_process_state()

        self._spb_curr_flowrate = QDoubleSpinBox()
        self._spb_curr_flowrate.setRange(0.0, 2.0)
        self._spb_curr_flowrate.setSingleStep(0.1)
        self._spb_curr_flowrate.setValue(process['curr flowrate'])
        self._lyt_third = QHBoxLayout()
        self._lyt_third.addWidget(QLabel('Симуляция расхода'))
        self._lyt_third.addWidget(self._spb_curr_flowrate)

        self._txt_process_view = QTextBrowser()
        # new_text = [f'{k}: {process[k]}' for k in process_keys_to_print]
        # self._txt_process_view.setText('\n'.join(new_text))

        self._updater()

        self._spb_curr_flowrate.valueChanged.connect(
            lambda: self._dispatch({'type': 'wateringprocess/UPDATE',
                                    'payload':
                                        {'new_data': {'curr flowrate': self._spb_curr_flowrate.value()}
                                         }}))

        self._lyt_main.addWidget(QLabel('Насос'))
        self._lyt_main.addLayout(self._lyt_first)
        self._lyt_main.addLayout(self._lyt_second)
        self._lyt_main.addWidget(self._txt_pump_view)
        self._lyt_main.addWidget(QLabel('Процесс'))
        self._lyt_main.addLayout(self._lyt_third)
        self._lyt_main.addWidget(self._txt_process_view)

