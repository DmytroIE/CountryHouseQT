def watering_process_reducer(state=None, action=None):
    if state is None:
        state = {}
    if action['type'] == 'wateringprocess/UPDATE':
        changed = False
        for key in action['payload']['new_data']:
            if state[key] != action['payload']['new_data'][key]:
                changed = True
                break
        if changed:
            new_state = state.copy()
            new_state = {**new_state, **(action['payload']['new_data'])}
            return new_state
        else:
            return state
    elif action['type'] == 'wateringprocess/ACKNOWLEDGEMENT':
        new_state = {**state, **({'ackn': True})}
        return new_state
    else:
        return state
