from PyQt5.QtWidgets import QApplication
import pickle
import pydux


class ConnectedToStoreApplication(QApplication):
    def __init__(self, reducer, default_state, mw_stack=None, args=[]):
        QApplication.__init__(self, args)
        print('Application created')
        self.store = None
        try:
            with open('store.dat', 'rb') as f:
                state = pickle.load(f)
                self.store = pydux.create_store(reducer, state, mw_stack)
        except Exception as e:
            print(f'Could not open dat file, default settings are loaded\nError: {e}')
            self.store = pydux.create_store(reducer, default_state, mw_stack)

    def save_store_on_exit(self):
        try:
            with open('store.dat', 'wb') as f:
                pickle.dump(self.store.get_state(), f, pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print(f'Could not save store\nError: {e}')
