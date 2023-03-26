from src.utils.WateringStatuses import *


watering_zones_initial = [
    {'ID': 'LZliGv4F', 'typ_flow': 1.2, 'deviation': 25, 'gpio_num': 13, 'enabled': True, 'valve on': False,
     'status': WateringZoneStatuses.PENDING, 'progress': 0.0},
    {'ID': 'FclCGDyZx', 'typ_flow': 1.2, 'deviation': 25,  'gpio_num': 14, 'enabled': True, 'valve on': False,
     'status': WateringZoneStatuses.PENDING, 'progress': 0.0},
    {'ID': 'iPyLGSJbx', 'typ_flow': 1.2, 'deviation': 25,  'gpio_num': 15, 'enabled': True, 'valve on': False,
     'status': WateringZoneStatuses.PENDING, 'progress': 0.0},
    {'ID': 'Fcyi4kPtV', 'typ_flow': 1.2, 'deviation': 25,  'gpio_num': 16, 'enabled': True, 'valve on': False,
     'status': WateringZoneStatuses.PENDING, 'progress': 0.0},
    {'ID': 'iBwi42jQ1', 'typ_flow': 1.2, 'deviation': 25,  'gpio_num': 17, 'enabled': True, 'valve on': False,
     'status': WateringZoneStatuses.PENDING, 'progress': 0.0}
]


def watering_zones_reducer(state=None, action=None):
    if state is None:
        state = watering_zones_initial
    if action['type'] == 'wateringzones/ADD_ITEM':
        new_state = state.copy()
        new_state.insert(action['payload']['index'], action['payload']['new_item'])
        return new_state
    elif action['type'] == 'wateringzones/DELETE_ITEM':
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
    elif action['type'] == 'wateringzones/UPDATE_ITEM':
        number_of_updated_item = -1
        # print('up')
        for ind, item in enumerate(state):
            if item['ID'] == action['payload']['ID']:
                number_of_updated_item = ind
        if number_of_updated_item > -1:
            new_state = state.copy()
            item_state = state[number_of_updated_item].copy()
            new_state[number_of_updated_item] = {**item_state, **(action['payload']['new_data'])}
            # print(new_state)
            return new_state
        else:
            return state
    else:
        return state
