from PyQt5.QtCore import QTime, QDate
from shortid import ShortId

from src.utils.Timers import TON
from src.store.store import ConnectedToStoreComponent
from src.utils.WateringStatuses import *

SP_DELAY = 15  # in seconds


class PumpStates(Enum):
    PENDING = 0
    CHECKING_AVAILABILITY = 1
    STARTUP = 100
    RUN = 10
    DONE = 200
    SHUTDOWN = 201
    ERROR = 202


class PumpAlarmMessages(Enum):
    NO_FEEDBACK_WHEN_RUN = {'ID': 'tCoPB053', 'text': 'Авария контактора насоса'}


def pump_strategy(pump):
    pump_id = pump['ID']
    ackn = pump['ackn']
    error = pump['error']
    feedback = pump['feedback']
    contactor_feedback = pump['contactor feedback']
    enabled = pump['enabled']
    enabled_for_watering = pump['enabled for watering']
    run_request = pump['run request']
    run_request_for_watering = pump['run request for watering']
    available = pump['available']
    available_for_watering = pump['available for watering']
    pump_on = pump['pump on']
    timer_init_time = pump['timer init time']
    curr_state = pump['curr state']
    prev_state = pump['prev state']
    state_entry_time = pump['state entry time']
    alarm_log_batch = []
    curr_error = None

    # Квитирование
    if ackn:
        if error:
            error = False
            ackn = False

    # Автомат
    while True:
        again = False

        if curr_state is PumpStates.PENDING:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                prev_state = curr_state

            # Переходы
            curr_state = PumpStates.CHECKING_AVAILABILITY
            again = True

        elif curr_state is PumpStates.CHECKING_AVAILABILITY:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                prev_state = curr_state

            if available:
                if not enabled:
                    available = False
            else:
                if enabled and not error:
                    available = True

            if available_for_watering:
                if not enabled_for_watering:
                    available_for_watering = False
            else:
                if enabled_for_watering and not error:
                    available_for_watering = True

            # Переходы
            if (available and run_request) or \
                    (available_for_watering and run_request_for_watering):
                curr_state = PumpStates.STARTUP
                again = True
            else:
                if (not run_request) and (not run_request_for_watering):
                    if feedback is not OnOffDevFeedbacks.STOP:
                        feedback = OnOffDevFeedbacks.STOP
                        # когда сигнал run_request пропал, то насос теперь с полным правом
                        # может выдавать OnOffDevFeedbacks.STOP
                curr_state = PumpStates.PENDING
                again = False  # (!!!!! обязательно, иначе бесконечный цикл)

        elif curr_state is PumpStates.STARTUP:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDate.currentDate(),
                                        'text': 'Запуск контактора насоса'})
                pump_on = True
                feedback = OnOffDevFeedbacks.PENDING
                state_entry_time = QTime.currentTime()
                timer_init_time = None
                prev_state = curr_state

            # Постоянные действия
            curr_time = QTime.currentTime()
            if not contactor_feedback:
                if not timer_init_time:
                    timer_init_time = curr_time
            else:
                if timer_init_time and timer_init_time.secsTo(curr_time) < SP_DELAY:
                    timer_init_time = None

            # Переходы
            if (not run_request) and (not run_request_for_watering):
                curr_state = PumpStates.SHUTDOWN
                again = True
            elif timer_init_time and timer_init_time.secsTo(curr_time) >= SP_DELAY:
                curr_error = PumpAlarmMessages.NO_FEEDBACK_WHEN_RUN
                curr_state = PumpStates.ERROR
                again = True
            elif contactor_feedback and \
                    state_entry_time.secsTo(QTime.currentTime()) > 2:
                # специальная задержка, чтобы побыть какое-то время в этом состоянии
                curr_state = PumpStates.RUN
                again = True

        elif curr_state is PumpStates.RUN:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDate.currentDate(),
                                        'text': 'Контактор насоса включен'})
                feedback = OnOffDevFeedbacks.RUN
                timer_init_time = None
                prev_state = curr_state

            # Постоянные действия
            curr_time = QTime.currentTime()
            if not contactor_feedback:
                if not timer_init_time:
                    timer_init_time = curr_time
            else:
                if timer_init_time and timer_init_time.secsTo(curr_time) < SP_DELAY:
                    timer_init_time = None

            # Переходы
            if (not run_request) and (not run_request_for_watering):
                curr_state = PumpStates.DONE
                again = True
            elif timer_init_time and timer_init_time.secsTo(curr_time) > SP_DELAY:
                curr_error = PumpAlarmMessages.NO_FEEDBACK_WHEN_RUN
                curr_state = PumpStates.ERROR
                again = True

        elif curr_state is PumpStates.ERROR:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogAlarmMessageTypes.ERROR_IN,
                                        'ID': pump_id + curr_error.value['ID'],
                                        'dt_stamp': QDate.currentDate(),
                                        'text': curr_error.value['text']})
                available = False
                available_for_watering = False
                error = True
                feedback = OnOffDevFeedbacks.NOT_RUN
                prev_state = curr_state

            # Переходы
            curr_state = PumpStates.SHUTDOWN
            again = True

        elif curr_state is PumpStates.DONE:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                feedback = OnOffDevFeedbacks.STOP  # Упрощенный вариант, без обработки невыключения
                prev_state = curr_state

            # Переходы
            curr_state = PumpStates.SHUTDOWN
            again = True

        elif curr_state is PumpStates.SHUTDOWN:
            # Единоразовые действия при входе в шаг
            if curr_state is not prev_state:
                alarm_log_batch.append({'type': LogInfoMessageTypes.COMMON_INFO,
                                        'dt_stamp': QDate.currentDate(),
                                        'text': 'Контактор насоса отключен'})
                pump_on = False
                prev_state = curr_state

            # Переходы
            curr_state = PumpStates.PENDING
            again = True

        if not again:
            break

    # обновляем выходы
    return {'ackn': ackn,
            'error': error,
            'feedback': feedback,
            'contactor feedback': contactor_feedback,
            'available': available,
            'available for watering': available_for_watering,
            'pump on': pump_on,
            'timer init time': timer_init_time,
            'curr state': curr_state,
            'prev state': prev_state,
            'state entry time': state_entry_time
            }, alarm_log_batch


if __name__ == '__main__':
    from ast import literal_eval
    pump = {'ID': '3265',
            'ackn': False,
            'error': False,
            'feedback': OnOffDevFeedbacks.STOP,
            'contactor feedback': False,
            'enabled': True,
            'enabled for watering': True,
            'run request': False,
            'run request for watering': False,
            'available': True,
            'available for watering': True,
            'pump on': False,
            'timer init time': None,
            'curr state': PumpStates.PENDING,
            'prev state': PumpStates.PENDING,
            'state entry time': None
            }
    while True:
        inp = input('enter a new chunk: ')
        if inp == 'q' or inp == 'Q':
            break
        try:

            chunk = literal_eval(inp)

            pump = {**pump, **chunk}
            new_state, batch = pump_strategy(pump)
            pump = {**pump, **new_state}
            print(f'Current state: {pump["curr state"]}')
            for item in batch:
                print(f'{item["dt_stamp"].toString("dd.MM.yy")} {item["text"]}')
        except Exception as e:
            print(f'Error: {e}\ntry again\n')
