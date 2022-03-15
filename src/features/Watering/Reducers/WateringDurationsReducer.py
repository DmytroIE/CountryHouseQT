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
        # обязательно скопировать и вложенные массивы, иначе ссылки на них в self._cached останутся те же
        # и последующая вставка затронет и self._cached
        new_state = [item.copy() for item in state]

        # item[0] - как минимум одна строка должна быть (потому нельзя последнюю зону удалять)
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
        # print(f'wateringdurations/DELETE_ROW ID = {action["payload"]}')
        new_state = []
        for column in state:
            new_column = []
            for item in column:
                if item['ID'][1] != action["payload"]:
                    new_column.append(item)
            new_state.append(new_column)
        # print(f'new_state = {new_state}')
        return new_state
    elif action['type'] == 'wateringdurations/ADD_COLUMN':
        new_state = state.copy()
        new_column = []
        for item in new_state[0]:  # опять, предполагаем, что хотя бы один столбец у нас есть
            ID = (action['payload']['cycle_ID'], item['ID'][1])
            new_column.append({'ID': ID, 'duration': DEFAULT_DURATION})
        new_state.insert(action['payload']['index'], new_column)
        # print(f'new_state = {new_state}')
        return new_state
    elif action['type'] == 'wateringdurations/DELETE_COLUMN':
        new_state = []
        for item in state:
            if item[0]['ID'][0] != action['payload']:
                new_state.append(item)
        # print(f'new_state = {new_state}')
        return new_state
    elif action['type'] == 'wateringdurations/UPDATE_ITEM':
        # print('up')
        new_state = state.copy()
        for ind_c, item_c in enumerate(new_state):
            for ind_z, item_z in enumerate(item_c):
                if item_z['ID'] == action['payload']['ID']:
                    new_state[ind_c][ind_z] = {**item_z, **action['payload']['new_data']}
        # print(f'new state = {new_state}')
        return new_state
    else:
        return state
