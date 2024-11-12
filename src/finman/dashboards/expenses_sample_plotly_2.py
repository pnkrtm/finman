import pandas as pd
from dash import Dash, html, dcc, Input, Output
from dash import dash_table
import plotly.graph_objs as go
import datetime as dt
from typing import List


class DataObject:
    def __init__(self, data: pd.DataFrame):
        self._data = data
        self._selected_status = pd.Series([True] * self.length, index=self._data.index)
        self._observers = []

    @property
    def data(self):
        return self._data

    @property
    def selected_data(self):
        # todo
        # _selected_status должен учитывать изменение порядка/сортировку транзакций
        return self._data.loc[self._selected_status]

    @property
    def selected_idx(self):
        return [i for i, value in enumerate(self._selected_status) if value]

    def set_selected_idx(self, selected_idx: List[int]):
        # self._selected_idx = selected_idx
        self._selected_status = pd.Series([False] * self.length, index=self._data.index)
        self._selected_status.iloc[selected_idx] = True

    @property
    def length(self):
        return self._data.shape[0]

    def register_observer(self, observer):
        """Регистрирует виджет для отслеживания изменений."""
        self._observers.append(observer)

    def notify_observers(self):
        """Оповещает все виджеты об изменении данных."""
        for observer in self._observers:
            observer.update()

    def update_data(self, new_data: pd.DataFrame):
        """Обновляет данные и оповещает виджеты."""
        self._data = new_data
        self.notify_observers()

    def modify_data(self, func):
        """Применяет функцию модификации данных."""
        self._data = func(self._data)
        self.notify_observers()


class Widget:
    def __init__(self, data_object: DataObject):
        self.data_object = data_object
        self.data_object.register_observer(self)

    def update(self):
        pass

    def render(self):
        pass


class TableWidget(Widget):
    def __init__(self, data_object: DataObject):
        super().__init__(data_object)

    def update(self):
        self.render()

    def render(self):
        data = self.data_object.data
        # data['checked'] = False  # начальное значение чекбоксов по умолчанию вкл.
        # data.loc[data.index.isin(self.data_object.selected_idx), 'checked'] = True
        return dash_table.DataTable(
            id='transaction_table',
            columns=[
                {"name": "id", "id": "id"},
                {"name": "Дата/время", "id": "date"},
                {"name": "Описание", "id": "description"},
                {"name": "Сумма", "id": "amount"},
                {"name": "Категория", "id": "category"},
                {"name": "Подкатегория", "id": "subcategory"},
            ],
            data=data.to_dict('records'),
            row_selectable='multi',
            selected_rows=self.data_object.selected_idx,
            editable=True
        )


class HierarchyCheckboxWidget(Widget):
    def __init__(self, data_object: DataObject):
        super().__init__(data_object)
        self.categories = self.build_hierarchy()

    def build_hierarchy(self):
        """Создает иерархическую структуру категорий и подкатегорий."""
        categories = {}
        for _, row in self.data_object.data.iterrows():
            category = row['category']
            subcategory = row['subcategory']
            if category not in categories:
                categories[category] = []
            if subcategory not in categories[category]:
                categories[category].append(subcategory)
        return categories

    def render(self):
        """Рендерит иерархические чекбоксы."""
        checkboxes = []
        for category, subcategories in self.categories.items():
            subcategory_checks = [
                dcc.Checklist(
                    options=[{'label': subcategory, 'value': subcategory}],
                    value=[],
                    id={'type': 'subcategory-checkbox', 'category': category, 'subcategory': subcategory}
                )
                for subcategory in subcategories
            ]
            checkboxes.append(
                html.Div([
                    dcc.Checklist(
                        options=[{'label': category, 'value': category}],
                        value=[],
                        id={'type': 'category-checkbox', 'category': category}
                    ),
                    html.Div(subcategory_checks, style={'margin-left': '20px'})
                ])
            )
        return html.Div(checkboxes, id='hierarchy-checkbox')

class WaterfallChartWidget(Widget):
    def update(self):
        self.render()

    def render(self):
        waterfall_data = self.data_object.selected_data.groupby('subcategory')['amount'].sum()
        fig = go.Figure(go.Waterfall(
            x=waterfall_data.index,
            y=waterfall_data.values
        ))
        fig.update_layout(title="Диаграмма водопада по подкатегориям")
        return dcc.Graph(id='waterfall_chart', figure=fig)


class WeeklySpendingChartWidget(Widget):
    def update(self):
        self.render()

    def render(self):
        filtered_data = self.data_object.selected_data.copy()
        filtered_data['week'] = filtered_data['date'].dt.to_period("W")
        weekly_data = filtered_data.groupby('week')['amount'].sum()

        fig = go.Figure(go.Bar(
            x=weekly_data.index.astype(str),
            y=weekly_data.values
        ))
        fig.update_layout(title="Понедельные траты")
        return dcc.Graph(id='weekly_spending_chart', figure=fig)


class AppManager:
    def __init__(self, data: pd.DataFrame):
        self.data_object = DataObject(data)

        # Инициализация виджетов
        self.table_widget = TableWidget(self.data_object)
        self.waterfall_chart_widget = WaterfallChartWidget(self.data_object)
        self.weekly_spending_chart_widget = WeeklySpendingChartWidget(self.data_object)
        self.hierarchy_checkbox_widget = HierarchyCheckboxWidget(self.data_object)

        # Настройка приложения Dash
        self.app = Dash(__name__)
        self.app.layout = html.Div([
            html.Div([
                self.table_widget.render(),
            ], style={'grid-area': '1 / 1'}),
            html.Div([
                self.waterfall_chart_widget.render(),
            ], style={'grid-area': '1 / 2'}),
            html.Div([
                self.weekly_spending_chart_widget.render(),
            ], style={'grid-area': '2 / 2'}),
            html.Div([
                self.hierarchy_checkbox_widget.render(),
            ], style={'grid-area': '2 / 1'})
        ], style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'grid-template-rows': '1fr 1fr',
            'gap': '10px'
        })

        # Настройка колбэков
        self.setup_callbacks()

    def setup_callbacks(self):
        @self.app.callback(
            Output('waterfall_chart', 'figure'),
            Output('weekly_spending_chart', 'figure'),
            Input('transaction_table', 'selected_rows')
        )
        def update_charts(selected_rows):
            if not selected_rows:
                selected_rows = list(range(self.data_object.length))

            self.data_object.set_selected_idx(selected_rows)

            waterfall_fig = self.waterfall_chart_widget.render().figure
            weekly_spending_fig = self.weekly_spending_chart_widget.render().figure

            return waterfall_fig, weekly_spending_fig

    def run(self):
        self.app.run_server(debug=True)


if __name__ == '__main__':
    # Пример данных
    initial_data = pd.DataFrame({
        'date': [dt.datetime.now() - dt.timedelta(days=i) for i in range(10)],
        'description': [f"Transaction {i}" for i in range(10)],
        'amount': [100 * (i % 5 + 1) for i in range(10)],
        'category': ["Food", "Transport", "Utilities", "Entertainment", "Other"] * 2,
        'subcategory': ["Groceries", "Fuel", "Electricity", "Cinema", "Misc"] * 2
    })
    app_manager = AppManager(initial_data)
    app_manager.run()
