watering_durations_initial = {
    ('CPyCGmQ0F', 'LZliGv4F'):{'ID': ('CPyCGmQ0F', 'LZliGv4F'), 'duration': 15}
}


def watering_durations_reducer(state=None, action=None):
    if state is None:
        state = watering_durations_initial
    if action['type'] == 'UPDATE_ITEM':
        new_state = {**state, **action['payload']}
        return new_state
    else:
        return state
