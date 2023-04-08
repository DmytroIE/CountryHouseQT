from collections import OrderedDict


class ConnectedComponent:
    """
    V.1.0.1. Component that is connected to the pydux store.
    Can be used as a mixin to any other class that is to be connected to the store.
    """

    def __init__(self, store):
        """
        Note:
        """

        self._get_store_state = store.get_state
        self._dispatch = store.dispatch
        self._cached = None

        self._unsubscribe = store.subscribe(self._updater)

    def __del__(self):
        if self._unsubscribe and hasattr(self._unsubscribe, '__call__'):
            self._unsubscribe()

    def _updater(self):
        """
        Функция для ленивых, кто хочет использовать уже готовый код вместо того, чтобы писать _updater
        с нуля. Эта функция реализует случаи, когда локальный state - это примитив, или же одномерный
        list или dict (именно одномерный, когда элементы именно на первом уровне вложенности заменяются новыми),
        (т.е. 99% всех возможных случаев). Правда, придется определить свои функции внутри класса-наследника, такие, как
        _on_state_update и _get_own_state, но их объем будет намного меньше, чем писать каждый раз Update для каждого
        компонента с нуля. Желательно вызвать эту функцию в конструкторе,
        потом уже _updater будет вызываться по подписке внутри store. Если такой подход не нравится,
        можно определить свою функцию _updater, тогда она будет вызываться в store.
        """
        # print('updater')
        # если в классе-наследнике определены такие функции, то можно использовать код ниже
        if hasattr(self, '_get_own_state') and hasattr(self, '_on_state_update'):

            print('мы в _updater')
            # этот кусок кода для тех, кто решил использовать функцию _updater в базовом классе
            # иначе нужно переопределить эту функцию в наследнике,
            # и тогда вся вот этот код ниже вообще не будет вызываться

            new_state = self._get_own_state()  # эта функция должна быть в классе-наследнике, типа селектора
            # print(f'self._cached id={id(self._cached)}, new_state id={id(new_state)}')
            if self._cached is not new_state:
                # --------------------------Primitive---------------
                if isinstance(new_state, (int, float, str, bool)):
                    self._on_state_update(new_state)  # эта функция должна быть в классе-наследнике, который юзает
                    # стейт, состоящий из примитива, и который хочет использовать уже предопределенную
                    # функцию _updater в баз. классе (то есть ту, в который мы сейчас и находимся), а не создавать свою
                    # --------------------------Ordered Dict---------------
                elif isinstance(new_state, OrderedDict):
                    # для упорядоченного словаря алгоритм похож на применяемый для list
                    # здесь три варианта - добавился элемент в словарь, удалился из словаря и изменился существующий

                    if self._cached is None:
                        self._cached = OrderedDict({})

                    diff_add = new_state.keys() - self._cached.keys()  # это set
                    diff_delete = self._cached.keys() - new_state.keys()  # и это тоже set

                    # print('мы в _updater в части для словарей, diff_add = {diff_add}')
                    if diff_delete:  # если стало меньше записей
                        diff_list = [key for key in self._cached.keys() if key not in new_state.keys()]
                        self._on_state_update(new_state, diff_list, action='DELETE')

                    elif diff_add:  # если стало больше записей
                        diff_list = [key for key in new_state.keys() if key not in self._cached.keys()]
                        self._on_state_update(new_state, diff_list, action='ADD')

                    else:  # значит, изменился существующий элемент словаря или порядок элементов,
                        # но количество элементов не поменялось
                        updated_keys_list = []
                        for key, _ in new_state.items():
                            if self._cached[key] is not new_state[key]\
                                    or self._cached[key] != new_state[key]:
                                updated_keys_list.append(key)
                        # print(f'updated keys list = \n{updated_keys_list}')
                        if len(updated_keys_list):  # значит, поменялся хотя бы один элемент
                            self._on_state_update(new_state, updated_keys_list, action='UPDATE')
                        else:  # значит, изменился порядок элементов в Ordered List
                            self._on_state_update(new_state, updated_keys_list, action='ITEMS_ORDER_CHANGED')
                # --------------------------Dict---------------
                elif isinstance(new_state, dict):  # для плоского словаря, где используются только ключи верхнего уровня
                    # здесь три варианта - добавился элемент в словарь, удалился из словаря и изменился существующий

                    if self._cached is None:
                        self._cached = {}

                    diff_add = new_state - self._cached.keys()  # это set
                    diff_delete = self._cached.keys() - new_state  # и это тоже set

                    # print('мы в _updater в части для словарей, diff_add = {diff_add}')
                    if diff_delete:  # если стало меньше записей
                        self._on_state_update(new_state, list(diff_delete), action='DELETE')

                    elif diff_add:  # если стало больше записей
                        self._on_state_update(new_state, list(diff_add), action='ADD')

                    else:  # значит, изменился существующий элемент словаря, но количество элементов не поменялось
                        updated_keys_list = []
                        for key, _ in new_state.items():
                            if self._cached[key] != new_state[key] or\
                                    self._cached[key] is not new_state[key]:
                                updated_keys_list.append(key)
                        self._on_state_update(new_state, updated_keys_list, action='UPDATE')
                # --------------------------List---------------
                elif isinstance(new_state, list):  # для однородного массива
                    # здесь также три варианта - добавился элемент в массив,
                    # удалился из массива и изменился существующий
                    if self._cached is None:
                        self._cached = []

                    diff = len(new_state) - len(self._cached)

                    if diff < 0:  # если стало меньше записей
                        list_of_indexes_of_deleted_items = []
                        for ind, item in enumerate(self._cached):
                            try:
                                index_in_new_state = new_state.index(item)
                            except ValueError:
                                list_of_indexes_of_deleted_items.append(ind)

                        self._on_state_update(new_state, list_of_indexes_of_deleted_items, action='DELETE')

                    elif diff > 0:  # если стало больше записей
                        list_of_new_items = []
                        for ind, item in enumerate(new_state):
                            try:
                                index_in_prev_state = self._cached.index(item)
                                list_of_new_items.append(
                                    index_in_prev_state)  # для существующих - индекс в старом состоянии
                            except ValueError:
                                list_of_new_items.append({'index_of_new_item': ind})  # для новых сущностей - объект
                                # с индексом в новом состоянии
                        self._on_state_update(new_state, list_of_new_items, action='ADD')

                    else:  # значит, изменился существующий элемент массива, но количество элементов не поменялось
                        list_of_indexes_of_updated_items = []
                        for ind, new_state_item in enumerate(new_state):
                            if self._cached[ind] != new_state[ind] or\
                                    self._cached[ind] is not new_state[ind]:
                                list_of_indexes_of_updated_items.append(ind)
                        if len(list_of_indexes_of_updated_items):
                            self._on_state_update(new_state, list_of_indexes_of_updated_items, action='UPDATE')

                # в конце - перезапись кешированных свойств
                self._cached = new_state
        else:
            print(self)
            raise NotImplementedError()  # Защита от дурака
