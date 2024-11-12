from dash import dash_table

from src.finman.dashboards.widgets.base import BaseWidget


class TableWidget(BaseWidget):

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
