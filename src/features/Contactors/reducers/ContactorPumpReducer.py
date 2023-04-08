from src.utils.WateringStatuses import *

pump_default = {
    'run request': False,
    'run request for watering': False,
    'feedback': EnableDevFeedbacks.STOP,
    'available': True,
    'available for watering': True,
    'status': OnOffDeviceStatuses.PENDING,
    'enabled': True,
    'ackn': False,
    'pump on': False
}


def contactor_pump_reducer(state=None, action=None):
    if state is None:
        state = pump_default
    if action['type'] == 'pump/UPDATE':
        new_state = state.copy()
        new_state = {**new_state, **action['payload']}
        return new_state

