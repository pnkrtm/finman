from dash import dcc
import plotly.graph_objs as go

from src.finman.dashboards.widgets.base import BaseWidget


class WaterfallChartWidget(BaseWidget):
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
