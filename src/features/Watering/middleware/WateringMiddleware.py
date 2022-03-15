from PyQt5.QtWidgets import QMessageBox


def watering_action_dialogs_mw(store_):
    dispatch, get_state = store_['dispatch'], store_['get_state']

    def disp(next_):
        def act(action):
            if action['type'] == 'wateringzones/DELETE_ITEM' or action['type'] == 'wateringcycles/DELETE_ITEM':
                dlg = QMessageBox()
                title = ''
                if len(get_state()['watering']['zones']) < 2 and action['type'] == 'wateringzones/DELETE_ITEM':
                    dlg.setWindowTitle('Ошибка')
                    dlg.setText('Должна остаться хотя бы одна зона!')
                    dlg.setStandardButtons(QMessageBox.Ok)
                    dlg.setIcon(QMessageBox.Critical)
                    dlg.exec()
                    return
                if len(get_state()['watering']['cycles']) < 2 and action['type'] == 'wateringcycles/DELETE_ITEM':
                    dlg.setWindowTitle('Ошибка')
                    dlg.setText('Должен остаться хотя бы один цикл!')
                    dlg.setStandardButtons(QMessageBox.Ok)
                    dlg.setIcon(QMessageBox.Critical)
                    dlg.exec()
                    return

                title = 'Удалить зону?' if action['type'] == 'wateringzones/DELETE_ITEM' else 'Удалить цикл?'
                # dlg = QMessageBox()
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
            elif action['type'] == 'wateringcycles/ADD_ITEM':
                # print('add')
                dispatch({'type': 'wateringdurations/ADD_COLUMN',
                          'payload': {'index': action['payload']['index'],
                                      'cycle_ID': action['payload']['new_item']['ID']}})
            elif action['type'] == 'wateringcycles/DELETE_ITEM':
                # print('delete')
                dispatch({'type': 'wateringdurations/DELETE_COLUMN',
                          'payload': action['payload']})

        return act

    return disp
