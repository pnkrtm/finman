from dash import dcc
import plotly.graph_objs as go

from src.finman.dashboards.widgets.base import BaseWidget


class WeeklySpendingChartWidget(BaseWidget):
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
