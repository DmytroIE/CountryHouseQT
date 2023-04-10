from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QDoubleSpinBox, QProgressBar, QPushButton, QWidget, \
    QStackedLayout, QToolButton
from PyQt5.QtCore import Qt

from src.utils.WateringStatuses import *
from src.utils.Buttons import change_toggle_button_style


class WateringZone(QFrame):

    def __init__(self, data, on_update, parent=None):
        super().__init__(parent)
        self._id = data['ID']
        self._create_ui(data, on_update)

    # @property
    # def widget_id(self):
    #     return self._id

    def _create_ui(self, data, on_update):
        self._cached = {'enabled': data['enabled']}

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

        self._lbl_gpio = QLabel()

        self._lyt_layer2.addWidget(QLabel('Пределы расхода, м3/ч'))
        self._lyt_layer2.addWidget(self._spb_lo_flow)
        self._lyt_layer2.addWidget(self._spb_hi_flow)
        self._lyt_layer2.addWidget(self._lbl_gpio)

        # -----------Add layers--------------
        self._lyt_stacked.addWidget(self._wdg_layer1)
        self._lyt_stacked.addWidget(self._wdg_layer2)

        # -----------Main Layout--------------
        self._btn_name = QPushButton()
        self._btn_name.clicked.connect(
            lambda: on_update(ID=self._id,
                              new_data={'enabled': not self._cached['enabled']})
        )

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
        self._lbl_status.setText(f'{new_data["status"].value}')
        self._bar_progress.setValue(int(new_data['progress']))
        self._spb_lo_flow.setValue(new_data['lo lim flowrate'])
        self._spb_hi_flow.setValue(new_data['hi lim flowrate'])
        self._lbl_gpio.setText(f'GPIO {new_data["gpio_num"]}')
        self._btn_name.setText(new_data['name'])

        change_toggle_button_style(new_data['enabled'],
                                   self._btn_name,
                                   'StandardButton',
                                   'StandardButton EnabledButton')
        change_toggle_button_style(new_data['valve on'],
                                   self._btn_next_layer,
                                   'StandardButton',
                                   'StandardButton EnabledButton')
        for key in self._cached:
            self._cached[key] = new_data[key]
