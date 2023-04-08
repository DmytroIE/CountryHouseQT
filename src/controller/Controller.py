from PyQt5.QtCore import QTimer
from itertools import cycle

from src.store.store import ConnectedToStoreComponent
from src.controller.ContactorStrategy import contactor_strategy
from src.controller.UnivPumpContactorStrategy import univ_pump_cont_strategy
from src.controller.WateringProcessStrategy import watering_process_strategy
from src.controller.WateringZoneStrategy import watering_zone_strategy
from src.controller.WateringCycleStrategy import watering_cycle_strategy


class Controller(ConnectedToStoreComponent):
    def __init__(self):
        ConnectedToStoreComponent.__init__(self)

        self._cyclic_list_of_strategies = cycle([self._run_cycles,
                                                 self._run_process,
                                                 self._run_zones,
                                                 self._run_contactors])

        self._one_second_timer = QTimer()
        self._one_second_timer.timeout.connect(self._on_timer_tick)
        self._one_second_timer.start(250)

    def _on_timer_tick(self):
        try:
            next(self._cyclic_list_of_strategies)()
        except Exception as e:
            print(f'Ошибка выполнения, {e}')

    def _run_zones(self):
        zones = self._get_store_state()['watering']['zones']
        process = self._get_store_state()['watering']['process']
        for zone_id, zone in zones:
            updated_zone_outputs, alarm_log_batch = watering_zone_strategy(zones, process)
            self._dispatch({'type': 'wateringzones/UPDATE', 'payload': {'ID': zone_id,
                                                                        'new_data': updated_zone_outputs}})
            for item in alarm_log_batch:
                print(f'{item["dt_stamp"].toString("dd.MM.yy mm:ss")} {item["text"]}')

    def _run_cycles(self):
        cycles = self._get_store_state()['watering']['cycles']
        process = self._get_store_state()['watering']['process']
        for cycle_id, cycle in cycles:
            updated_cycle_outputs, \
                updated_process_outputs, \
                alarm_log_batch = watering_cycle_strategy(cycle, cycles, process)
            self._dispatch({'type': 'wateringcycles/UPDATE', 'payload': {'ID': cycle_id,
                                                                         'new_data': updated_cycle_outputs}})
            self._dispatch({'type': 'wateringprocess/UPDATE', 'payload': updated_process_outputs})  # не очень хорошо!!!
            for item in alarm_log_batch:
                print(f'{item["dt_stamp"].toString("dd.MM.yy mm:ss")} {item["text"]}')

    def _run_process(self):
        process = self._get_store_state()['watering']['process']
        zones = self._get_store_state()['watering']['zones']
        pump_id = process['pump id']
        pump = self._get_store_state()['el_facilities']['contactors'][pump_id]

        updated_process_outputs, \
            updated_zones_outputs, \
            updated_pump_outputs, \
            alarm_log_batch = watering_process_strategy(process, zones, pump)
        self._dispatch({'type': 'wateringprocess/UPDATE', 'payload': updated_zones_outputs})
        for zone_id, zone_outputs in updated_zones_outputs:
            self._dispatch({'type': 'wateringzones/UPDATE', 'payload': {'ID': zone_id,
                                                                        'new_data': zone_outputs}})
        self._dispatch({'type': 'contactors/UPDATE', 'payload': {'ID': pump_id,
                                                                 'new_data': updated_pump_outputs}})
        for item in alarm_log_batch:
            print(f'{item["dt_stamp"].toString("dd.MM.yy mm:ss")} {item["text"]}')

    def _run_contactors(self):
        contactors = self._get_store_state()['el_facilities']['contactors']
        for contactor_id, contactor in contactors:
            updated_cont_outputs, alarm_log_batch = None, None
            if 'run req for watering' in contactor:
                updated_cont_outputs, alarm_log_batch = univ_pump_cont_strategy(contactor)
            else:
                updated_cont_outputs, alarm_log_batch = contactor_strategy(contactor)
            self._dispatch({'type': 'contactors/UPDATE', 'payload': {'ID': contactor_id,
                                                                        'new_data': updated_cont_outputs}})
            for item in alarm_log_batch:
                print(f'{item["dt_stamp"].toString("dd.MM.yy mm:ss")} {item["text"]}')

    def _updater(self):
        pass
