from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QTabWidget, QLabel, QListWidget, QListWidgetItem, QStyle


class AlarmList(QTabWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # self._tab_main = QTabWidget(self)

        self._lst_current = QListWidget()

        # self._lst_current.addItems(['fhfjhgjhfgj', 'gdfdgdgg'])
        list1 = ['12113', '547khhftdr', 'ugfd']
        for text in list1:
            pixmapi = getattr(QStyle, 'SP_MessageBoxWarning')
            icon = self.style().standardIcon(pixmapi)
            item = QListWidgetItem(icon, text)
            self._lst_current.addItem(item)

        self.addTab(self._lst_current, 'Current')

        self._lst_log = QListWidget()

        list2 = ['fsgdgdbd', 'srdgr95jfjkhs', 'fsdfsf']
        for text in list2:
            pixmapi = getattr(QStyle, 'SP_MessageBoxCritical')
            icon = self.style().standardIcon(pixmapi)
            item = QListWidgetItem(icon, text)
            self._lst_log.addItem(item)

        self.addTab(self._lst_log, 'Log')
