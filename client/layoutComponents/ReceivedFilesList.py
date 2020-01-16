import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

files = []

Builder.load_file("./KvFiles/ReceivedFilesList.kv")


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass


class ReceivedFilesLabel(RecycleDataViewBehavior, GridLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(False)
    cols = 4
    row_force_default = True
    row_default_height = 50

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.label1_text = data['label2']['text']
        self.remove_button = data['button']

        root = App.get_running_app()
        self.add_func = root.show_popup

        return super(ReceivedFilesLabel, self).refresh_view_attrs(
            rv, index, data)

    def removeFile(self, name, file_size):
        global files
        files.remove((name, file_size))
        root = App.get_running_app()
        path = os.path.join("received_files", root.login_text_input.text, name)
        if os.path.exists(path):
            os.remove(path)
        root.received_files_list.build_files_list()


class ReceivedFilesRecycleView(RecycleView):
    global files

    def build_files_list(self):
        self.data = []
        for x in files:
            d = {'label2': {'text': x[0]}, 'file_size': x[1], 'button': True}
            self.data.append(d)

        if len(self.data) == 0:
            self.data.append({'label2': {'text': 'No file received'}, 'button': False})

        self.refresh_from_data()