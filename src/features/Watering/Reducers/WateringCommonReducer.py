from src.utils.WateringStatuses import *

watering_common_default = {
    'exec request': False,
    'abort': False,
    'feedback': ExecDevFeedbacks.DONE,
    'available': True,
    # 'status': OnOffDeviceStatuses.PENDING,
    'ackn': False,
    'ball valve on': False,
    'flowrate': 0.0,
    'progress': 0.0
}


def watering_common_reducer(state=None, action=None):
    if state is None:
        state = watering_common_default
    if action['type'] == 'wateringcommon/UPDATE':
        new_state = state.copy()
        new_state = {**new_state, **action['payload']}
        return new_state
