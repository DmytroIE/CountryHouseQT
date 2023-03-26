from src.utils.WateringStatuses import *

socket_default = {
    'run request': False,
    'req conf': OnOffDevConfirmations.STOP,
    'available': True,
    'status': OnOffDeviceStatuses.PENDING,
    'enabled': True,
    'ackn': False
}


def contactor_light_reducer(state=None, action=None):
    if state is None:
        state = socket_default
    if action['type'] == 'socket/UPDATE':
        new_state = state.copy()
        new_state = {**new_state, **action['payload']}
        return new_state

