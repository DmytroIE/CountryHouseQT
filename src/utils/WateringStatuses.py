from enum import Enum
from string import Template


OFF = 0
STANDBY = 1
IN_WORK = 2
FAULTY = 3
RUN_OUT = 4

statuses = {OFF: "Выключен", STANDBY: "В ожидании", IN_WORK: "В работе", FAULTY: "Неисправность", RUN_OUT: "Выбег"}

SP_STATE_TRANSITION_TYPICAL_DELAY = 2  # in seconds


class OnOffDeviceStatuses(Enum):
    OFF = 'Выключен'
    STANDBY = 'В ожидании'
    STARTUP = 'Запуск'
    RUN = 'Работа'
    SHUTDOWN = 'Завершение'
    FAULTY = 'Неисправность'
    PRESSURE_RELIEF = 'Сброс давления'


class EnableDevFeedbacks(Enum):
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
    RESETTING = 4
    CHECK_IF_DEVICES_RUNNING = 5
    CHECK_IF_DEVICES_STOPPED = 6


class ZoneErrorMessages(Enum):
    HIGH_FLOWRATE = 'Zone: Зона {0}: расход воды высокий ({1}), возможен порыв'


class ZoneWarningMessages(Enum):
    LOW_FLOWRATE = 'Zone: Зона {0}: малый расход воды ({1})'


class WateringProcessErrorMessages(Enum):
    PUMP_NOT_RUNNING = 'Process: Полив отменен, насос не работает'


class WateringProcessStates(Enum):
    STANDBY = 0
    CHECK_AVAILABILITY = 1
    START_PUMP = 2
    OPEN_BALL_VALVE = 3
    WATER_ZONE = 4
    CHANGE_ZONE = 5
    CLOSE_BALL_VALVE = 6
    RESET_ZONES_AFTER_WATERING = 7
    STOP_PUMP = 8
    PRESSURE_RELIEF = 9
    RESET_ZONES_AFTER_PRESSURE_RELIEF = 10
    RESETTING = 11
    CHECK_IF_DEVICES_RUNNING = 12
    CHECK_IF_DEVICES_STOPPED = 13


class CycleStates(Enum):
    CHECK_CONDITIONS_TO_EXECUTE = 0
    STANDBY = 1
    EXECUTE = 2
    SHUTDOWN = 3


class ContactorStates(Enum):
    STANDBY = 0
    CHECK_AVAILABILITY = 1
    STARTUP = 2
    RUN = 3
    SHUTDOWN = 4
    CHECK_IF_DEVICES_RUNNING = 5
    CHECK_IF_DEVICES_STOPPED = 6


class ContactorErrorMessages(Enum):
    NO_FEEDBACK_WHEN_RUN = 'Cont: Авария контактора {0}'


class ContactorWarningMessages(Enum):
    CANT_STOP_CONTACTOR = 'Cont: Невозможно отключить контактор {0}'


SP_CONTACTOR_TIMER_DELAY = 5  # in seconds