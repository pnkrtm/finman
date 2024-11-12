import pandas as pd
from typing import List


class TransDataObject:
    def __init__(self, transactions_data: pd.DataFrame, categories_data: pd.DataFrame):
        self._transactions_data = transactions_data
        self._categories_data = categories_data
        self._selected_status = pd.Series([True] * self.length, index=self._transactions_data.index)
        self._observers = []

    @property
    def data(self):
        return self._transactions_data

    @property
    def selected_data(self):
        # todo
        # _selected_status должен учитывать изменение порядка/сортировку транзакций
        return self._transactions_data.loc[self._selected_status]

    @property
    def selected_idx(self):
        return [i for i, value in enumerate(self._selected_status) if value]

    def set_selected_idx(self, selected_idx: List[int]):
        # self._selected_idx = selected_idx
        self._selected_status = pd.Series([False] * self.length, index=self._transactions_data.index)
        self._selected_status.iloc[selected_idx] = True

    @property
    def length(self):
        return self._transactions_data.shape[0]

    def register_observer(self, observer):
        """Регистрирует виджет для отслеживания изменений."""
        self._observers.append(observer)

    def notify_observers(self):
        """Оповещает все виджеты об изменении данных."""
        for observer in self._observers:
            observer.update()

    # def update_data(self, new_data: pd.DataFrame):
    #     """Обновляет данные и оповещает виджеты."""
    #     self._data = new_data
    #     self.notify_observers()

    def modify_data(self, func):
        """Применяет функцию модификации данных."""
        self._data = func(self._data)
        self.notify_observers()
