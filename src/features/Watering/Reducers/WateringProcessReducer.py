def watering_process_reducer(state=None, action=None):
    if state is None:
        state = {}
    if action['type'] == 'wateringprocess/UPDATE':
        new_state = state.copy()
        new_state = {**new_state, **action['payload']}
        return new_state
