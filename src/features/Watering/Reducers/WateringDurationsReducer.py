from collections import OrderedDict


def watering_durations_reducer(state=None, action=None):
    if state is None:
        state = OrderedDict({})
    if action['type'] == 'wateringdurations/UPDATE_ITEM':
        new_state = state.copy()
        cycle_id = action['payload']['cycle_id']
        new_state[cycle_id] = state[cycle_id].copy()
        zone_id = action['payload']['zone_id']
        new_state[cycle_id][zone_id] = {**new_state[cycle_id][zone_id], **action['payload']['new_data']}
        return new_state
    else:
        return state
