import pydux

from src.store.ConnectedComponent import ConnectedComponent

from src.features.Watering.Reducers.WateringReducer import watering_reducer

root_reducer = pydux.combine_reducers({'watering': watering_reducer
                                       })

store = pydux.create_store(root_reducer)


class ConnectedWithStoreComponent(ConnectedComponent):
    def __init__(self):
        ConnectedComponent.__init__(self, store)

# class ConnectedComponent:
#     """
#     V.1.0.0. Component that is connected to the pydux store.
#     Can be used as a mixin to any other class that is to be connected to the store.
#     """
#
#     def __init__(self):
#         """
#         Note:
#         """
#
#         self._get_store_state = store.get_state
#         self._dispatch = store.dispatch
#         self._cached = None
#
#         self._unsubscribe = store.subscribe(self._updater)
#
#     def __del__(self):
#         if self._unsubscribe and hasattr(self._unsubscribe, '__call__'):
#             self._unsubscribe()
#
#     def _updater(self):
#         """
#         Функция для ленивых, кто хочет использовать уже готовый код вместо того, чтобы писать _updater
#         с нуля. Эта функция реализует случаи, когда локальный state - это примитив, list или dict (т.е. 99%
#         всех возможных случаев. Правда, придется определить свои функции внутри класса-наследника, такие, как
#         _on_state_update и _get_own_state, но их объем будет намного меньше, чем писать каждый раз Update для каждого
#         компонента с нуля. Потом уже _updater будет вызываться по подписке внутри store. Если такой подход не нравится,
#         можно определить свою функцию _updater, тогда она будет вызываться в store.
#         """
#         print('updater')
#         # если в классе-наследнике определены такие функции, то можно использовать код ниже
#         if hasattr(self, '_get_own_state') and hasattr(self, '_on_state_update'):
#
#             # print('мы в _updater')
#             # этот кусок кода для тех, кто решил использовать функцию _updater в базовом классе
#             # иначе нужно переопределить эту функцию в наследнике,
#             # и тогда вся вот эта функция вообще не будет вызываться
#
#             new_state = self._get_own_state()  # эта функция должна быть в классе-наследнике, типа селектора
#             if self._cached != new_state:
#                 # --------------------------Primitive---------------
#                 if isinstance(new_state, (int, float, str, bool)):
#                     self._on_state_update(new_state)  # эта функция должна быть в классе-наследнике, который юзает
#                     # стейт, состоящий из примитива, и который хочет использовать уже предопределенную
#                     # функцию _updater в баз. классе (то есть ту, в который мы сейчас и находимся), а не создавать свою
#                 # --------------------------Dict---------------
#                 elif isinstance(new_state, dict):  # для плоского словаря, где используются только ключи верхнего уровня
#                     # здесь три варианта - добавился элемент в словарь, удалился из словаря и изменился существующий
#
#                     if self._cached is None:
#                         self._cached = {}
#
#                     diff_add = new_state - self._cached.keys()  # это set
#                     diff_delete = self._cached.keys() - new_state  # и это тоже set
#
#                     # print('мы в _updater в части для словарей, diff_add = {diff_add}')
#                     if diff_delete:  # если стало меньше записей
#                         for key in diff_delete:
#                             self._on_state_update(new_state, key, action='DELETE')
#
#                     elif diff_add:  # если стало больше записей
#                         for key in diff_add:
#                             self._on_state_update(new_state, key, action='ADD')
#
#                     else:  # значит, изменился существующий элемент словаря, но количество элементов не поменялось
#                         for key, _ in new_state.items():
#                             if self._cached[key] != new_state[key]:
#                                 self._on_state_update(new_state, key, action='UPDATE')
#                 # --------------------------List---------------
#                 elif isinstance(new_state, list):  # для однородного массива
#                     # здесь также три варианта - добавился элемент в массив,
#                     # удалился из массива и изменился существующий
#                     if self._cached is None:
#                         self._cached = []
#
#                     diff = len(new_state) - len(self._cached)
#
#                     if diff < 0:  # если стало меньше записей
#                         list_of_indexes_of_deleted_items = []
#                         for ind, item in enumerate(self._cached):
#                             try:
#                                 index_in_new_state = new_state.index(item)
#                             except ValueError:
#                                 list_of_indexes_of_deleted_items.append(ind)
#
#                         self._on_state_update(new_state, list_of_indexes_of_deleted_items, action='DELETE')
#
#                     elif diff > 0:  # если стало больше записей
#                         list_of_new_items = []
#                         for ind, item in enumerate(new_state):
#                             try:
#                                 index_in_prev_state = self._cached.index(item)
#                                 list_of_new_items.append(
#                                     index_in_prev_state)  # для существующих - индекс в старом состоянии
#                             except ValueError:
#                                 list_of_new_items.append({'index_of_new_item': ind})  # для новых сущностей - объект
#
#                         self._on_state_update(new_state, list_of_new_items, action='ADD')
#
#                     else:  # значит, изменился существующий элемент массива, но количество элементов не поменялось
#                         list_of_updated_items = []
#                         for ind, new_state_item in enumerate(new_state):
#                             if self._cached[ind] != new_state_item:
#                                 list_of_updated_items.append(new_state_item)
#                             else:
#                                 list_of_updated_items.append(None)
#                         self._on_state_update(new_state, list_of_updated_items, action='UPDATE')
#
#                 # в конце - перезапись кешированных свойств
#                 self._cached = new_state
#         else:
#             raise NotImplementedError()  # Защита от дурака
