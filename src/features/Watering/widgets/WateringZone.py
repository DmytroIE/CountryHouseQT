from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QDoubleSpinBox, QProgressBar, QPushButton, QWidget, \
    QStackedLayout, QToolButton
from PyQt5.QtCore import Qt

from src.utils.WateringStatuses import *
from src.utils.Buttons import change_toggle_button_style


class WateringZone(QFrame):

    def __init__(self, data, on_update, parent=None):
        super().__init__(parent)
        self._id = data['ID']
        self._cached_for_widget = {'status': None, 'progress': None,
                                   'enabled': None, 'valve on': None,
                                   'lo lim flowrate': -0.1, 'hi lim flowrate': -0.1}
        self._create_ui(data, on_update)

    def _create_ui(self, data, on_update):
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setFixedHeight(50)

        self._lyt_main = QHBoxLayout(self)
        self._lyt_main.setContentsMargins(2, 2, 2, 2)

        self._lyt_stacked = QStackedLayout()
        self._lyt_stacked.setContentsMargins(0, 0, 0, 0)

        # --------Layer 1-----------------
        self._wdg_layer1 = QWidget()
        self._lyt_layer1 = QHBoxLayout(self._wdg_layer1)
        self._lyt_layer1.setContentsMargins(2, 2, 2, 2)

        self._lbl_status = QLabel()
        self._lyt_layer1.addWidget(self._lbl_status)

        self._bar_progress = QProgressBar()
        self._bar_progress.setRange(0, 100)
        self._bar_progress.setTextVisible(True)
        self._lyt_layer1.addWidget(self._bar_progress)

        # ----------Layer 2--------------------
        self._wdg_layer2 = QWidget()
        self._lyt_layer2 = QHBoxLayout(self._wdg_layer2)
        self._lyt_layer2.setContentsMargins(2, 2, 2, 2)

        self._spb_lo_flow = QDoubleSpinBox()
        self._spb_lo_flow.setRange(0.1, 2.0)
        self._spb_lo_flow.setSingleStep(0.1)

        self._spb_hi_flow = QDoubleSpinBox()
        self._spb_hi_flow.setRange(0.1, 2.0)
        self._spb_hi_flow.setSingleStep(0.1)

        self._lbl_gpio = QLabel(f'GPIO {data["gpio_num"]}')

        self._lyt_layer2.addWidget(QLabel('Пределы расхода, м3/ч'))
        self._lyt_layer2.addWidget(self._spb_lo_flow)
        self._lyt_layer2.addWidget(self._spb_hi_flow)
        self._lyt_layer2.addWidget(self._lbl_gpio)

        # -----------Add layers--------------
        self._lyt_stacked.addWidget(self._wdg_layer1)
        self._lyt_stacked.addWidget(self._wdg_layer2)

        # -----------Main Layout--------------
        self._btn_name = QPushButton(data['name'])
        self._btn_name.clicked.connect(
            lambda: on_update(ID=self._id,
                              new_data={
                                  'enabled': not self._cached_for_widget['enabled']
                              }))

        self._btn_next_layer = QToolButton()
        self._btn_next_layer.setArrowType(Qt.RightArrow)
        self._btn_next_layer.setProperty('class', 'StandardButton')
        self._curr_index = 0
        self._btn_next_layer.clicked.connect(
            lambda: self._lyt_stacked.setCurrentIndex(self._change_curr_index())
        )

        self.apply_updates(data)  # чтобы не дублировать код, пользуемся уже готовой функцией

        # эти строки обязательно после self.apply_updates, иначе при записи в спинбокс
        # возникнет бесконечный цикл
        self._spb_lo_flow.valueChanged.connect(
            lambda: on_update(ID=self._id, new_data={'lo lim flowrate': self._spb_lo_flow.value()})
        )
        self._spb_hi_flow.valueChanged.connect(
            lambda: on_update(ID=self._id, new_data={'hi lim flowrate': self._spb_hi_flow.value()})
        )
        self._lyt_main.addWidget(self._btn_name)
        self._lyt_main.addLayout(self._lyt_stacked)
        self._lyt_main.addWidget(self._btn_next_layer)

    def _change_curr_index(self):
        if self._curr_index == 0:
            self._curr_index = 1
        else:
            self._curr_index = 0
        return self._curr_index

    def apply_updates(self, new_data):
        changed = False
        if abs(new_data['lo lim flowrate'] - self._cached_for_widget['lo lim flowrate']) > 0.000001:
            self._spb_lo_flow.setValue(new_data['lo lim flowrate'])
            changed = True

        if abs(new_data['hi lim flowrate'] - self._cached_for_widget['hi lim flowrate']) > 0.000001:
            self._spb_hi_flow.setValue(new_data['hi lim flowrate'])
            changed = True

        if new_data['status'] != self._cached_for_widget['status']:
            self._lbl_status.setText(new_data['status'].value)
            changed = True
        progress = int(new_data['progress'])
        if progress != self._cached_for_widget['progress']:
            self._bar_progress.setValue(progress)
            changed = True
        if new_data['enabled'] != self._cached_for_widget['enabled']:
            change_toggle_button_style(new_data['enabled'],
                                       self._btn_name,
                                       'StandardButton',
                                       'StandardButton EnabledButton')
            changed = True
        if new_data['valve on'] != self._cached_for_widget['valve on']:
            change_toggle_button_style(new_data['valve on'],
                                       self._btn_next_layer,
                                       'StandardButton',
                                       'StandardButton EnabledButton')
            changed = True
        if changed:
            for key in self._cached_for_widget:
                self._cached_for_widget[key] = new_data[key]
                if key == 'progress':
                    self._cached_for_widget[key] = progress
