from collections import OrderedDict


def watering_zones_reducer(state=None, action=None):
    if state is None:
        state = OrderedDict({})
    if action['type'] == 'wateringzones/UPDATE_ITEM':
        new_state = state.copy()
        zone_id = action['payload']['ID']
        new_state[zone_id] = {**new_state[zone_id], **(action['payload']['new_data'])}
        return new_state
    elif action['type'] == 'wateringzones/ACKNOWLEDGEMENT':
        new_state = state.copy()
        for zone_id, zone in new_state:
            new_zone = zone.copy()
            new_zone[zone_id] = {**new_zone, **({'ackn': True})}
        return new_state
    else:
        return state

# def watering_zones_reducer(state=None, action=None):
#     if state is None:
#         state = OrderedDict({})
#     if action['type'] == 'wateringzones/ADD_ITEM':
#         new_state = state.copy()
#         new_state[action['payload']['ID']] = action['payload']['new_item']
#         return new_state
#     elif action['type'] == 'wateringzones/DELETE_ITEM':
#         new_state = state.copy()
#         del new_state[action['payload']['ID']]
#         return new_state
#     elif action['type'] == 'wateringzones/UPDATE_ITEM':
#         new_state = state.copy()
#         new_state[action['payload']['ID']] = {**new_state[action['payload']['ID']], **(action['payload']['new_data'])}
#         return new_state
#     else:
#         return state
