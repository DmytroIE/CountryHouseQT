from collections import OrderedDict


def watering_cycles_reducer(state=None, action=None):
    if state is None:
        state = OrderedDict({})
    if action['type'] == 'wateringcycles/UPDATE_ITEM':
        new_state = state.copy()
        cycle_id = action['payload']['ID']
        new_state[cycle_id] = {**new_state[cycle_id], **(action['payload']['new_data'])}
        return new_state
    elif action['type'] == 'wateringcycles/ACKNOWLEDGEMENT':
        new_state = state.copy()
        for cycle_id, cycle in new_state:
            new_cycle = cycle.copy()
            new_cycle[cycle_id] = {**new_cycle, **({'ackn': True})}
        return new_state
    else:
        return state
