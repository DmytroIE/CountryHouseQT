from PyQt5.QtCore import QTime


class TON:
    def __init__(self):
        self._start = None
        self.out = False

    def run(self, condition, interval):
        if not condition:
            self._start = None
            self.out = False
            return
        else:
            if self._start is None:
                self._start = QTime.currentTime()
            else:
                if self._start.msecsTo(QTime.currentTime()) > interval:
                    self.out = True

    def reset(self):
        self._start = None
        self.out = False
