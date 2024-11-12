import pandas as pd
from dash import Dash, html, Input, Output

from src.finman.dashboards.widgets.table_widget import TableWidget
from src.finman.dashboards.widgets.cat_sub_widget import CatSubWidget
from src.finman.dashboards.widgets.weekly_spending import WeeklySpendingChartWidget
from src.finman.dashboards.widgets.waterfall import WaterfallChartWidget
from src.finman.data_objects.transactions import TransDataObject


class AppManager:
    def __init__(self, data: pd.DataFrame):
        self.data_object = TransDataObject(data)

        # Инициализация виджетов
        self.table_widget = TableWidget(self.data_object)
        self.waterfall_chart_widget = WaterfallChartWidget(self.data_object)
        self.weekly_spending_chart_widget = WeeklySpendingChartWidget(self.data_object)
        self.cat_sub_widget = CatSubWidget(self.data_object)

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
                self.cat_sub_widget.render(),
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