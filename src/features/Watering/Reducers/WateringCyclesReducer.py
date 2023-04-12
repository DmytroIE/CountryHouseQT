from collections import OrderedDict


def watering_cycles_reducer(state=None, action=None):
    if state is None:
        state = OrderedDict({})
    if action['type'] == 'wateringcycles/UPDATE_ITEM':
        cycle_id = action['payload']['ID']
        changed = False
        for key in action['payload']['new_data']:
            if state[cycle_id][key] != action['payload']['new_data'][key]:
                changed = True
                break
        if changed:
            new_state = state.copy()
            new_state[cycle_id] = {**new_state[cycle_id], **(action['payload']['new_data'])}
            return new_state
        else:
            return state
    elif action['type'] == 'wateringcycles/ACKNOWLEDGEMENT':
        new_state = state.copy()
        for cycle_id, cycle in new_state.items():
            new_cycle = cycle.copy()
            new_state[cycle_id] = {**new_cycle, **({'ackn': True})}
        return new_state
    else:
        return state
