def alarm_log_middleware(store):
    dispatch, get_state = store['dispatch'], store['get_state']

    def disp(next_):
        def act(action):
            if action['type'] == 'alarmlog/ACKNOWLEDGEMENT':
                dispatch({'type': 'wateringzones/ACKNOWLEDGEMENT'})
                dispatch({'type': 'wateringcycles/ACKNOWLEDGEMENT'})
                dispatch({'type': 'wateringprocess/ACKNOWLEDGEMENT'})
                dispatch({'type': 'contactors/ACKNOWLEDGEMENT'})
            next_(action)

        return act

    return disp
