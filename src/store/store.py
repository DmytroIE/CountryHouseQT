import pydux
from PyQt5.QtCore import QTime
from collections import OrderedDict

from src.features.Watering.middleware.WateringMiddleware import check_flowrate_limits_mw
from src.features.AlarmLog.middleware.AlarmLogMiddleware import alarm_log_middleware
from src.store.ConnectedComponent import ConnectedComponent
from src.utils.WateringStatuses import *

from src.features.Watering.Reducers.WateringReducer import watering_reducer
from src.features.Contactors.reducers.ContactorsReducer import contactors_reducer

watering_durations_initial = OrderedDict({
    'CPyCGmQ0F': OrderedDict({'LZliGv4F': {'cycle_id': 'CPyCGmQ0F', 'zone_id': 'LZliGv4F', 'duration': 15},
                              'FclCGDyZx': {'cycle_id': 'CPyCGmQ0F', 'zone_id': 'FclCGDyZx', 'duration': 15},
                              'iPyLGSJbx': {'cycle_id': 'CPyCGmQ0F', 'zone_id': 'iPyLGSJbx', 'duration': 15},
                              'Fcyi4kPtV': {'cycle_id': 'CPyCGmQ0F', 'zone_id': 'Fcyi4kPtV', 'duration': 15},
                              'iBwi42jQ1': {'cycle_id': 'CPyCGmQ0F', 'zone_id': 'iBwi42jQ1', 'duration': 15}}),
    'Lcli4yFwL': OrderedDict({'LZliGv4F': {'cycle_id': 'Lcli4yFwL', 'zone_id': 'LZliGv4F', 'duration': 15},
                              'FclCGDyZx': {'cycle_id': 'Lcli4yFwL', 'zone_id': 'FclCGDyZx', 'duration': 15},
                              'iPyLGSJbx': {'cycle_id': 'Lcli4yFwL', 'zone_id': 'iPyLGSJbx', 'duration': 15},
                              'Fcyi4kPtV': {'cycle_id': 'Lcli4yFwL', 'zone_id': 'Fcyi4kPtV', 'duration': 15},
                              'iBwi42jQ1': {'cycle_id': 'Lcli4yFwL', 'zone_id': 'iBwi42jQ1', 'duration': 15}})
})
watering_zones_initial = OrderedDict({
    'LZliGv4F': {'ID': 'LZliGv4F',
                 'gpio_num': 13,
                 'name': 'Зона 1',
                 'ackn': False,
                 'error': False,
                 'feedback': ExecDevFeedbacks.FINISHED,
                 'feedback temp': ExecDevFeedbacks.FINISHED,
                 'enabled': True,
                 'exec request': False,
                 'available': True,
                 'valve on': False,
                 'curr flowrate': 0.0,
                 'hi lim flowrate': 1.6,
                 'lo lim flowrate': 0.4,
                 'duration': 1,
                 'progress': 0.0,
                 'flowrate hi timer': None,
                 'flowrate lo timer': None,
                 'curr state': ZoneStates.CHECK_AVAILABILITY,
                 'prev state': ZoneStates.STANDBY,
                 'state entry time': None,
                 'raised errors': {ZoneErrorMessages.HIGH_FLOWRATE: False},
                 'raised warnings': {ZoneWarningMessages.LOW_FLOWRATE: False},
                 'status': OnOffDeviceStatuses.STANDBY
                 },
    'FclCGDyZx': {'ID': 'FclCGDyZx',
                  'gpio_num': 14,
                  'name': 'Зона 2',
                  'ackn': False,
                  'error': False,
                  'feedback': ExecDevFeedbacks.FINISHED,
                  'feedback temp': ExecDevFeedbacks.FINISHED,
                  'enabled': True,
                  'exec request': False,
                  'available': True,
                  'valve on': False,
                  'curr flowrate': 0.0,
                  'hi lim flowrate': 1.6,
                  'lo lim flowrate': 0.4,
                  'duration': 1,
                  'progress': 0.0,
                  'flowrate hi timer': None,
                  'flowrate lo timer': None,
                  'curr state': ZoneStates.CHECK_AVAILABILITY,
                  'prev state': ZoneStates.STANDBY,
                  'state entry time': None,
                  'raised errors': {ZoneErrorMessages.HIGH_FLOWRATE: False},
                  'raised warnings': {ZoneWarningMessages.LOW_FLOWRATE: False},
                  'status': OnOffDeviceStatuses.STANDBY
                  },
    'iPyLGSJbx': {'ID': 'iPyLGSJbx',
                  'gpio_num': 15,
                  'name': 'Зона 3',
                  'ackn': False,
                  'error': False,
                  'feedback': ExecDevFeedbacks.FINISHED,
                  'feedback temp': ExecDevFeedbacks.FINISHED,
                  'enabled': True,
                  'exec request': False,
                  'available': True,
                  'valve on': False,
                  'curr flowrate': 0.0,
                  'hi lim flowrate': 1.6,
                  'lo lim flowrate': 0.4,
                  'duration': 1,
                  'progress': 0.0,
                  'flowrate hi timer': None,
                  'flowrate lo timer': None,
                  'curr state': ZoneStates.CHECK_AVAILABILITY,
                  'prev state': ZoneStates.STANDBY,
                  'state entry time': None,
                  'raised errors': {ZoneErrorMessages.HIGH_FLOWRATE: False},
                  'raised warnings': {ZoneWarningMessages.LOW_FLOWRATE: False},
                  'status': OnOffDeviceStatuses.STANDBY
                  },
    'Fcyi4kPtV': {'ID': 'Fcyi4kPtV',
                  'gpio_num': 16,
                  'name': 'Зона 4',
                  'ackn': False,
                  'error': False,
                  'feedback': ExecDevFeedbacks.FINISHED,
                  'feedback temp': ExecDevFeedbacks.FINISHED,
                  'enabled': True,
                  'exec request': False,
                  'available': True,
                  'valve on': False,
                  'curr flowrate': 0.0,
                  'hi lim flowrate': 1.6,
                  'lo lim flowrate': 0.4,
                  'duration': 1,
                  'progress': 0.0,
                  'flowrate hi timer': None,
                  'flowrate lo timer': None,
                  'curr state': ZoneStates.CHECK_AVAILABILITY,
                  'prev state': ZoneStates.STANDBY,
                  'state entry time': None,
                  'raised errors': {ZoneErrorMessages.HIGH_FLOWRATE: False},
                  'raised warnings': {ZoneWarningMessages.LOW_FLOWRATE: False},
                  'status': OnOffDeviceStatuses.STANDBY
                  },
    'iBwi42jQ1': {'ID': 'iBwi42jQ1',
                  'gpio_num': 17,
                  'name': 'Палисадник',
                  'ackn': False,
                  'error': False,
                  'feedback': ExecDevFeedbacks.FINISHED,
                  'feedback temp': ExecDevFeedbacks.FINISHED,
                  'enabled': True,
                  'exec request': False,
                  'available': True,
                  'valve on': False,
                  'curr flowrate': 0.0,
                  'hi lim flowrate': 1.6,
                  'lo lim flowrate': 0.4,
                  'duration': 1,
                  'progress': 0.0,
                  'flowrate hi timer': None,
                  'flowrate lo timer': None,
                  'curr state': ZoneStates.CHECK_AVAILABILITY,
                  'prev state': ZoneStates.STANDBY,
                  'state entry time': None,
                  'raised errors': {ZoneErrorMessages.HIGH_FLOWRATE: False},
                  'raised warnings': {ZoneWarningMessages.LOW_FLOWRATE: False},
                  'status': OnOffDeviceStatuses.STANDBY
                  }
})
watering_cycles_initial = OrderedDict({
    'CPyCGmQ0F': {'ID': 'CPyCGmQ0F',
                  'ackn': False,
                  'enabled': True,
                  'active': False,
                  'hour': 6,
                  'minute': 0,
                  'curr state': CycleStates.STANDBY,
                  'prev state': CycleStates.STANDBY,
                  'prev time': None,
                  'status': OnOffDeviceStatuses.STANDBY},
    'Lcli4yFwL': {'ID': 'Lcli4yFwL',
                  'ackn': False,
                  'enabled': True,
                  'active': False,
                  'hour': 20,
                  'minute': 0,
                  'curr state': CycleStates.STANDBY,
                  'prev state': CycleStates.STANDBY,
                  'prev time': None,
                  'status': OnOffDeviceStatuses.STANDBY}
})
watering_process_initial = {
    'ID': 'uII5ip6W',
    'ackn': False,
    'error': False,
    'feedback': ExecDevFeedbacks.FINISHED,
    'feedback temp': ExecDevFeedbacks.FINISHED,
    'available': True,
    'ball valve on': False,
    'act cycle ID': None,
    'pump id': 'vv3GJie1',
    'active zone id': None,
    'curr flowrate': 0.0,
    'curr state': WateringProcessStates.CHECK_AVAILABILITY,
    'prev state': WateringProcessStates.STANDBY,
    'state entry time': None,
    'raised errors': {WateringProcessErrorMessages.PUMP_NOT_RUNNING: False},
    'raised warnings': {},
    'status': OnOffDeviceStatuses.STANDBY
}
contactors_initial = OrderedDict({
    '3RR2fg65': {'ID': '3RR2fg65',
                 'name': 'Свет',
                 'ackn': False,
                 'error': False,
                 'feedback': EnableDevFeedbacks.STOP,
                 'contactor feedback': False,
                 'enabled': True,
                 'run request': False,
                 'available': True,
                 'cont on': False,
                 'cont no fdbk timer': None,
                 'cont fdbk not off timer': None,
                 'curr state': ContactorStates.CHECK_AVAILABILITY,
                 'prev state': ContactorStates.STANDBY,
                 'state entry time': None,
                 'raised errors': {ContactorErrorMessages.NO_FEEDBACK_WHEN_RUN: False},
                 'raised warnings': {ContactorWarningMessages.CANT_STOP_CONTACTOR: False},
                 'status': OnOffDeviceStatuses.STANDBY
                 },
    'vv3GJie1': {'ID': 'vv3GJie1',
                 'name': 'Насос',
                 'ackn': False,
                 'error': False,
                 'feedback for watering': EnableDevFeedbacks.STOP,
                 'feedback': EnableDevFeedbacks.STOP,
                 'contactor feedback': False,
                 'enabled for watering': True,
                 'enabled': True,
                 'run req from watering': False,
                 'run request': False,
                 'available': True,
                 'cont on': False,
                 'cont no fdbk timer': None,
                 'cont fdbk not off timer': None,
                 'curr state': ContactorStates.CHECK_AVAILABILITY,
                 'prev state': ContactorStates.STANDBY,
                 'state entry time': None,
                 'raised errors': {ContactorErrorMessages.NO_FEEDBACK_WHEN_RUN: False},
                 'raised warnings': {ContactorWarningMessages.CANT_STOP_CONTACTOR: False},
                 'status': OnOffDeviceStatuses.STANDBY
                 },
    'kuPP4Kwq': {'ID': 'kuPP4Kwq',
                 'name': 'Свет',
                 'ackn': False,
                 'error': False,
                 'feedback': EnableDevFeedbacks.STOP,
                 'contactor feedback': False,
                 'enabled': True,
                 'run request': False,
                 'available': True,
                 'cont on': False,
                 'cont no fdbk timer': None,
                 'cont fdbk not off timer': None,
                 'curr state': ContactorStates.CHECK_AVAILABILITY,
                 'prev state': ContactorStates.STANDBY,
                 'state entry time': None,
                 'raised errors': {ContactorErrorMessages.NO_FEEDBACK_WHEN_RUN: False},
                 'raised warnings': {ContactorWarningMessages.CANT_STOP_CONTACTOR: False},
                 'status': OnOffDeviceStatuses.STANDBY
                 },

})

initial_state = {
    'watering': {'zones': watering_zones_initial,
                 'cycles': watering_cycles_initial,
                 'durations': watering_durations_initial,
                 'process': watering_process_initial},
    'contactors': contactors_initial
}

root_reducer = pydux.combine_reducers({'watering': watering_reducer,
                                       'contactors': contactors_reducer
                                       })

# def thunk_middleware(store):
#     dispatch, get_state = store['dispatch'], store['get_state']
#     print('thunk')
#     def wrapper(next_):
#         def thunk_dispatch(action):
#             if hasattr(action, '__call__'):
#                 return action(dispatch, get_state)
#             return next_(action)
#         return thunk_dispatch
#     return wrapper


mw_stack = pydux.apply_middleware(check_flowrate_limits_mw,
                                  alarm_log_middleware)

store = pydux.create_store(root_reducer, initial_state, mw_stack)


class ConnectedToStoreComponent(ConnectedComponent):
    def __init__(self):
        ConnectedComponent.__init__(self, store)
