from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout

from src.store.store import ConnectedToStoreComponent


class WateringCurrState(ConnectedToStoreComponent, QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        ConnectedToStoreComponent.__init__(self)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setStyleSheet("background-color: beige")

        self._frm_curr_flow = QFrame()
        self._frm_curr_flow.setStyleSheet("background-color: rgb(193, 225, 211)")
        self._lyt_curr_flow = QHBoxLayout(self._frm_curr_flow)
        self._lbl_title_curr_flow = QLabel('Тек. расход')
        self._lyt_curr_flow.addWidget(self._lbl_title_curr_flow)
        self._lbl_curr_flow = QLabel('0.86 м3/ч')
        self._lyt_curr_flow.addWidget(self._lbl_curr_flow)

        self._frm_curr_state = QFrame()
        self._frm_curr_state.setStyleSheet("background-color: rgb(193, 225, 211)")
        self._lyt_curr_state = QHBoxLayout(self._frm_curr_state)
        self._lbl_title_curr_state = QLabel('Состояние: ')
        self._lyt_curr_state.addWidget(self._lbl_title_curr_state)
        self._lbl_curr_state = QLabel('В ожидании')
        self._lyt_curr_state.addWidget(self._lbl_curr_state)

        self._lyt_main = QVBoxLayout(self)
        self._lyt_main.addWidget(self._frm_curr_flow)
        self._lyt_main.addWidget(self._frm_curr_state)

        self._lyt_main.setContentsMargins(2, 2, 2, 2)

    def _get_own_state(self):  # selector
        pass

    def _on_state_update(self, new_state, list_, action):
        pass
