from enum import Enum
from string import Template


OFF = 0
STANDBY = 1
IN_WORK = 2
FAULTY = 3
RUN_OUT = 4

statuses = {OFF: "Выключен", STANDBY: "В ожидании", IN_WORK: "В работе", FAULTY: "Неисправность", RUN_OUT: "Выбег"}


class OnOffDeviceStatuses(Enum):
    OFF = 'Выключен'
    STANDBY = 'В ожидании'
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
    FINISHED = 0
    BUSY = 1
    DONE = 2
    ABORTED = 3



# class WateringStatuses(Enum):
#     # OFF = 'Выключен'
#     STANDBY = 'В ожидании'
#     STARTUP = 'Запуск'
#     RUN = 'Работа'
#     SHUTDOWN = 'Выключение'
#     FAULTY = 'Неисправность'


class LogAlarmMessageTypes(Enum):
    WARNING_IN = 1
    WARNING_OUT = 2
    ERROR_IN = 3
    ERROR_OUT = 4


class LogInfoMessageTypes(Enum):
    COMMON_INFO = 1


class ZoneStates(Enum):
    STANDBY = 0
    CHECK_AVAILABILITY = 1
    EXECUTE = 2
    SHUTDOWN = 3
    CHECK_IF_DEVICES_RUNNING = 4
    CHECK_IF_DEVICES_STOPPED = 5


class ZoneErrorMessages(Enum):
    HIGH_FLOWRATE = Template('Зона $name: расход воды высокий ($flowrate), возможен порыв')


class ZoneWarningMessages(Enum):
    LOW_FLOWRATE = Template('Зона $name: малый расход воды ($flowrate)')


class WateringErrorMessages(Enum):
    PUMP_NOT_RUNNING = Template('Полив отменен, насос не работает')


class WateringStates(Enum):
    STANDBY = 0
    CHECK_AVAILABILITY = 1
    START_PUMP = 2
    OPEN_BALL_VALVE = 3
    WATER_ZONE = 4
    CHANGE_ZONE = 5
    CLOSE_BALL_VALVE = 6
    STOP_PUMP = 7
    PRESSURE_RELIEF = 8
    SHUTDOWN = 9
    CHECK_IF_DEVICES_RUNNING = 10
    CHECK_IF_DEVICES_STOPPED = 11


class CycleStates(Enum):
    STANDBY = 0
    CHECK_IF_DEVICES_STOPPED = 1
    CHECK_IF_DEVICES_RUNNING = 2
    CHECK_AVAILABILITY = 3
    EXECUTE = 4
    SHUTDOWN = 5
