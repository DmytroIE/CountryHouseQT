from PyQt5.QtWidgets import QMessageBox


def watering_action_dialogs_mw(store_):
    # dispatch, get_state = store_['dispatch'], store_['get_state']
    def disp(next_):
        def act(action):
            # print("on_delete_dialog_mw")
            if action['type'] == 'wateringzones/DELETE_ITEM' or action['type'] == 'wateringcycles/DELETE_ITEM':
                title = 'Удалить зону?' if action['type'] == 'wateringzones/DELETE_ITEM' else 'Удалить цикл?'
                dlg = QMessageBox()
                dlg.setWindowTitle('Удаление')
                dlg.setText(title)
                dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                dlg.setIcon(QMessageBox.Warning)
                button = dlg.exec()

                if button == QMessageBox.Yes:
                    next_(action)

            else:
                next_(action)
        return act
    return disp


def durations_table_mw(store_):
    dispatch, get_state = store_['dispatch'], store_['get_state']

    def disp(next_):
        def act(action):
            # print("durations_table_mw")
            next_(action)
            if action['type'] == 'wateringzones/ADD_ITEM':
                # print(get_state())
                dispatch({'type': 'wateringdurations/ADD_ROW',
                          'payload': {'index': action['payload']['index'],
                                      'zone_ID': action['payload']['new_item']['ID']}})
            elif action['type'] == 'wateringzones/DELETE_ITEM':
                dispatch({'type': 'wateringdurations/DELETE_ROW',
                          'payload': action['payload']})
        return act
    return disp
