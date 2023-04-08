def alarm_log_middleware(store):
    dispatch, get_state = store['dispatch'], store['get_state']
    print('alarm_log_middleware')

    def disp(next_):
        def act(action):
            next_(action)
            if action['type'] == 'alarmlog/ACKNOWLEDGEMENT':
                dispatch({'type': 'wateringzones/ACKNOWLEDGEMENT'})

        return act

    return disp