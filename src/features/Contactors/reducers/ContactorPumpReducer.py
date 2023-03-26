from src.utils.WateringStatuses import *

pump_default = {
    'run request': False,
    'req conf': OnOffDevConfs.CONF_STOP,
    'available': AvailabilityStatuses.YES,
    'on': False,
    'status': OnOffDeviceStatuses.OK
}


def light_reducer(state=None, action=None):
    if state is None:
        state = pump_default
    if action['type'] == 'pump/RUN_REQ':
        new_state = state.copy()
        new_state = {**new_state, **{'run request': action['payload']}}
        return new_state
    if action['type'] == 'pump/CHANGE_CONF':
        new_state = state.copy()
        new_state = {**new_state, **{'req conf': action['payload']}}
        return new_state
    if action['type'] == 'pump/CHANGE_AVAIL':
        new_state = state.copy()
        new_state = {**new_state, **{'available': action['payload']}}
        return new_state
    if action['type'] == 'pump/ENABLE':
        new_state = state.copy()
        new_state = {**new_state, **{'enabled': action['payload']}}
        return new_state
