watering_cycles_initial = [
    {'ID': 'CPyCGmQ0F', 'start': '06:00'},
    {'ID': 'Lcli4yFwL', 'start': '20:00'}
]


def watering_cycles_reducer(state=None, action=None):
    if state is None:
        state = watering_cycles_initial
    if action['type'] == 'wateringcycles/ADD_ITEM':
        new_state = state.copy()
        new_state.insert(action['payload']['index'], action['payload']['new_item'])
        return new_state
    elif action['type'] == 'wateringcycles/DELETE_ITEM':
        number_of_deleted_item = -1
        for ind, item in enumerate(state):
            if item['ID'] == action['payload']:
                number_of_deleted_item = ind
        if number_of_deleted_item > -1:
            new_state = state.copy()
            new_state.pop(number_of_deleted_item)
            return new_state
        else:
            return state
    elif action['type'] == 'wateringcycles/UPDATE_ITEM':
        number_of_updated_item = -1
        for ind, item in enumerate(state):
            if item['ID'] == action['payload']['ID']:
                number_of_updated_item = ind
        if number_of_updated_item > -1:
            new_state = state.copy()
            new_state[number_of_updated_item] = action['payload']['updated_item']
            # print(f'new_state = {new_state}')
            return new_state
        else:
            return state
    else:
        return state
