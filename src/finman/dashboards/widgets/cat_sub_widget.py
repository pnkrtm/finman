from dash import html, dcc

from src.finman.data_objects.transactions import TransDataObject
from src.finman.dashboards.widgets.base import BaseWidget


class CatSubWidget(BaseWidget):
    def __init__(self, data_object: TransDataObject):
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
        """Рендерит выпадающие списки для каждой категории."""
        dropdowns = []
        for category, subcategories in self.categories.items():
            dropdowns.append(
                html.Div([
                    html.Label(category),
                    dcc.Dropdown(
                        options=[{'label': subcat, 'value': subcat} for subcat in subcategories],
                        value=subcategories,  # по умолчанию выбраны все подкатегории
                        multi=True,
                        id={'type': 'subcategory-dropdown', 'category': category}
                    )
                ], style={'margin-bottom': '10px'})
            )
        return html.Div(dropdowns, id='hierarchy-dropdown')