import pydux

from src.features.Watering.middleware.WateringMiddleware import watering_action_dialogs_mw, durations_table_mw
from src.store.ConnectedComponent import ConnectedComponent

from src.features.Watering.Reducers.WateringReducer import watering_reducer

root_reducer = pydux.combine_reducers({'watering': watering_reducer
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


mw_stack = pydux.apply_middleware(watering_action_dialogs_mw, durations_table_mw)

store = pydux.create_store(root_reducer, None, mw_stack)


class ConnectedToStoreComponent(ConnectedComponent):
    def __init__(self):
        ConnectedComponent.__init__(self, store)
