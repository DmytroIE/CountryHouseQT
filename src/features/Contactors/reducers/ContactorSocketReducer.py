from src.utils.WateringStatuses import *

socket_default = {
    'run request': False,
    'req conf': OnOffDevConfs.CONF_STOP,
    'available': AvailabilityStatuses.YES,
    'on': False,
    'status': OnOffDeviceStatuses.OK
}


def light_reducer(state=None, action=None):
    if state is None:
        state = socket_default
    if action['type'] == 'socket/RUN_REQ':
        new_state = state.copy()
        new_state = {**new_state, **{'run request': action['payload']}}
        return new_state
    if action['type'] == 'socket/CHANGE_CONF':
        new_state = state.copy()
        new_state = {**new_state, **{'req conf': action['payload']}}
        return new_state
    if action['type'] == 'socket/CHANGE_AVAIL':
        new_state = state.copy()
        new_state = {**new_state, **{'available': action['payload']}}
        return new_state
    if action['type'] == 'socket/ENABLE':
        new_state = state.copy()
        new_state = {**new_state, **{'enabled': action['payload']}}
        return new_state
