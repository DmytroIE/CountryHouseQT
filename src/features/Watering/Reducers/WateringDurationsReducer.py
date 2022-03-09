# watering_durations_initial = {
#     ('CPyCGmQ0F', 'LZliGv4F'): {'ID': ('CPyCGmQ0F', 'LZliGv4F'), 'duration': 15},
#     ('CPyCGmQ0F', 'FclCGDyZx'): {'ID': ('CPyCGmQ0F', 'FclCGDyZx'), 'duration': 15},
#     ('CPyCGmQ0F', 'iPyLGSJbx'): {'ID': ('CPyCGmQ0F', 'iPyLGSJbx'), 'duration': 15},
#     ('CPyCGmQ0F', 'Fcyi4kPtV'): {'ID': ('CPyCGmQ0F', 'Fcyi4kPtV'), 'duration': 15},
#     ('CPyCGmQ0F', 'iBwi42jQ1'): {'ID': ('CPyCGmQ0F', 'iBwi42jQ1'), 'duration': 15},
#     ('Lcli4yFwL', 'LZliGv4F'): {'ID': ('Lcli4yFwL', 'LZliGv4F'), 'duration': 15},
#     ('Lcli4yFwL', 'FclCGDyZx'): {'ID': ('Lcli4yFwL', 'FclCGDyZx'), 'duration': 15},
#     ('Lcli4yFwL', 'iPyLGSJbx'): {'ID': ('Lcli4yFwL', 'iPyLGSJbx'), 'duration': 15},
#     ('Lcli4yFwL', 'Fcyi4kPtV'): {'ID': ('Lcli4yFwL', 'Fcyi4kPtV'), 'duration': 15},
#     ('Lcli4yFwL', 'iBwi42jQ1'): {'ID': ('Lcli4yFwL', 'iBwi42jQ1'), 'duration': 15}
# }


watering_durations_initial = [
        [{'ID': ('CPyCGmQ0F', 'LZliGv4F'), 'duration': 15},
         {'ID': ('CPyCGmQ0F', 'FclCGDyZx'), 'duration': 15},
         {'ID': ('CPyCGmQ0F', 'iPyLGSJbx'), 'duration': 15},
         {'ID': ('CPyCGmQ0F', 'Fcyi4kPtV'), 'duration': 15},
         {'ID': ('CPyCGmQ0F', 'iBwi42jQ1'), 'duration': 15}],
        [{'ID': ('Lcli4yFwL', 'LZliGv4F'), 'duration': 15},
         {'ID': ('Lcli4yFwL', 'FclCGDyZx'), 'duration': 15},
         {'ID': ('Lcli4yFwL', 'iPyLGSJbx'), 'duration': 15},
         {'ID': ('Lcli4yFwL', 'Fcyi4kPtV'), 'duration': 15},
         {'ID': ('Lcli4yFwL', 'iBwi42jQ1'), 'duration': 15}]
    ]

# watering_durations_initial = [
#         [15, 15, 15, 15, 15],
#         [15, 15, 15, 15, 15]
#     ]

DEFAULT_DURATION = 10


def watering_durations_reducer(state=None, action=None):
    if state is None:
        state = watering_durations_initial
    if action['type'] == 'wateringdurations/ADD_ROW':
        new_state = [item.copy() for item in state]

        for item in new_state:
            ID = (item[0]['ID'][0], action['payload']['zone_ID'])
            # print(ID)
            item.insert(action['payload']['index'],
                        {
                            'ID': ID,
                            'duration': DEFAULT_DURATION
                        })
        # print(f'new_state = {new_state}')
        return new_state
    elif action['type'] == 'wateringdurations/DELETE_ROW':
        print(f'wateringdurations/DELETE_ROW ID = {action["payload"]}')
        new_state = [[],[]]
        for ind_c, column in enumerate(state):
            for item in column:
                if item['ID'][1] != action["payload"]:
                    new_state[ind_c].append(item)
        # print(f'new_state = {new_state}')
        return new_state
    # elif action['type'] == 'wateringcycles/DELETE_ITEM':
    #     return state
    # elif action['type'] == 'wateringzones/ADD_ITEM':
    #     return state
    # elif action['type'] == 'wateringzones/DELETE_ITEM':
    #     return state
    else:
        return state
