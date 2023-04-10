from collections import OrderedDict


def watering_zones_reducer(state=None, action=None):
    if state is None:
        state = OrderedDict({})
    if action['type'] == 'wateringzones/UPDATE_ITEM':
        zone_id = action['payload']['ID']
        changed = False
        for key in action['payload']['new_data']:
            if state[zone_id][key] != action['payload']['new_data'][key]:
                changed = True
                break
        if changed or \
                'hi lim flowrate' in action['payload']['new_data'].values() or \
                'lo lim flowrate' in action['payload']['new_data'].values():
            new_state = state.copy()
            new_state[zone_id] = {**new_state[zone_id], **(action['payload']['new_data'])}
            return new_state
        else:
            return state
    elif action['type'] == 'wateringzones/ACKNOWLEDGEMENT':
        new_state = state.copy()
        for zone_id, zone in new_state:
            new_zone = zone.copy()
            new_state[zone_id] = {**new_zone, **({'ackn': True})}
        return new_state
    else:
        return state

