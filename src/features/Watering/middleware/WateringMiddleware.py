from PyQt5.QtWidgets import QMessageBox


def check_flowrate_limits_mw(store_):
    dispatch, get_state = store_['dispatch'], store_['get_state']

    def disp(next_):
        def act(action):
            wrong_data_lo_lim = False
            wrong_data_hi_lim = False
            prev_lo_lim_flowrate = 0.0
            prev_hi_lim_flowrate = 0.0
            zone_id = None
            if action['type'] == 'wateringzones/UPDATE_ITEM':
                zone_id = action['payload']['ID']
                if 'hi lim flowrate' in action['payload']['new_data']:
                    if action['payload']['new_data']['hi lim flowrate'] < \
                            get_state()['watering']['zones'][zone_id]['lo lim flowrate'] + 0.01:
                        prev_hi_lim_flowrate = get_state()['watering']['zones'][zone_id]['hi lim flowrate']
                        wrong_data_hi_lim = True
                elif 'lo lim flowrate' in action['payload']['new_data']:

                    if action['payload']['new_data']['lo lim flowrate'] > \
                            get_state()['watering']['zones'][zone_id]['hi lim flowrate'] - 0.01:
                        prev_lo_lim_flowrate = get_state()['watering']['zones'][zone_id]['lo lim flowrate']
                        wrong_data_lo_lim = True
            next_(action)

            if wrong_data_lo_lim or wrong_data_hi_lim:
                dlg = QMessageBox()
                dlg.setWindowTitle('Ошибка')
                dlg.setText('Лимиты настроены неверно!')
                dlg.setStandardButtons(QMessageBox.Ok)
                dlg.setIcon(QMessageBox.Critical)
                dlg.exec()
                if wrong_data_lo_lim:
                    dispatch({'type': 'wateringzones/UPDATE_ITEM',
                              'payload': {'ID': zone_id,
                                          'new_data': {'lo lim flowrate': prev_lo_lim_flowrate}}})
                elif wrong_data_hi_lim:
                    dispatch({'type': 'wateringzones/UPDATE_ITEM',
                              'payload': {'ID': zone_id,
                                          'new_data': {'hi lim flowrate': prev_hi_lim_flowrate}}})

        return act

    return disp
