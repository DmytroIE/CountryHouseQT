from src.store.ConnectedComponent import ConnectedComponent
from PyQt5.QtWidgets import QApplication


class ConnectedToStoreComponent(ConnectedComponent):
    def __init__(self):
        ConnectedComponent.__init__(self, store=QApplication.instance().store)