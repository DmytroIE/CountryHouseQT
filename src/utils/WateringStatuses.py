from enum import Enum
from string import Template


OFF = 0
PENDING = 1
IN_WORK = 2
FAULTY = 3
RUN_OUT = 4

statuses = {OFF: "Выключен", PENDING: "В ожидании", IN_WORK: "В работе", FAULTY: "Неисправность", RUN_OUT: "Выбег"}


class OnOffDeviceStatuses(Enum):
    # OFF = 'Выключен'
    PENDING = 'В ожидании'
    STARTUP = 'Запуск'
    RUN = 'Работа'
    SHUTDOWN = 'Выключение'
    FAULTY = 'Неисправность'


class OnOffDevFeedbacks(Enum):
    PENDING = 0
    RUN = 1
    NOT_RUN = 2
    STOP = 3
    NOT_STOP = 4


class ExecDevFeedbacks(Enum):
    BUSY = 1
    ERROR = 2
    DONE = 3
    ABORTED = 4
    # READY = 5


class WateringStatuses(Enum):
    # OFF = 'Выключен'
    PENDING = 'В ожидании'
    STARTUP = 'Запуск'
    RUN = 'Работа'
    SHUTDOWN = 'Выключение'
    FAULTY = 'Неисправность'


class WateringZoneStatuses(Enum):
    # OFF = 'Выключен'
    PENDING = 'В ожидании'
    RUN = 'Работа'
    FAULTY = 'Неисправность'


class WateringCycleStatuses(Enum):
    # OFF = 'Выключен'
    PENDING = 'В ожидании'
    RUN = 'Работа'


class LogAlarmMessageTypes(Enum):
    WARNING_IN = 1
    WARNING_OUT = 2
    ERROR_IN = 3
    ERROR_OUT = 4


class LogInfoMessageTypes(Enum):
    COMMON_INFO = 1
