from collections import OrderedDict


def contactors_reducer(state=None, action=None):
    if state is None:
        state = OrderedDict({})
    if action['type'] == 'contactors/UPDATE_ITEM':
        cont_id = action['payload']['ID']
        changed = False
        for key in action['payload']['new_data']:
            if state[cont_id][key] != action['payload']['new_data'][key]:
                changed = True
                break
        # set_of_differences = action['payload']['new_data'].items() - state[cont_id]
        if changed:
            new_state = state.copy()
            new_state[cont_id] = {**new_state[cont_id], **(action['payload']['new_data'])}
            return new_state
        else:
            return state
    elif action['type'] == 'contactors/ACKNOWLEDGEMENT':
        new_state = state.copy()
        for cont_id, cont in new_state.items():
            new_cont = cont.copy()
            new_state[cont_id] = {**new_cont, **({'ackn': True})}
        return new_state
    else:
        return state
