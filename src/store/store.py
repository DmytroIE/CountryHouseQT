import pydux
from shortid import ShortId

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


def mw(store_):
    dispatch, get_state = store_['dispatch'], store_['get_state']

    def disp(next_):
        def act(action):
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


mw_stack = pydux.apply_middleware(mw)  # , thunk_middleware)

store = pydux.create_store(root_reducer, None, mw_stack)


class ConnectedToStoreComponent(ConnectedComponent):
    def __init__(self):
        ConnectedComponent.__init__(self, store)
