from src.finman.data_objects.transactions import TransDataObject


class BaseWidget:
    def __init__(self, data_object: TransDataObject):
        self.data_object = data_object
        self.data_object.register_observer(self)

    def update(self):
        pass

    def render(self):
        pass
