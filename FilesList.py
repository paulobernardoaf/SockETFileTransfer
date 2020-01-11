from kivy.app import App
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

files = []

Builder.load_string('''
<FilesLabel>:
    canvas.before:
        Color:
            rgba: (242/255, 242/255, 242/255, .9)
        Rectangle:
            pos: self.pos
            size: self.size
    label1_text: 'label 1 text'
    label2_text: 'label 2 text'
    label3_text: 'label 3 text'
    pos: self.pos
    size: self.size
    Label:
        id: id_label1
        color: (0, 0, 0, .9)
        text: root.label1_text
    Button:
        id: id_label2
        text: 'Remove'
        size_hint_x: None
        width: 100
        background_color: (1, 0, 1, 1)
        background_normal: ''
        on_press: root.removeFile(id_label1.text)
        

<FilesRecycleView>:
    viewclass: 'FilesLabel'
    SelectableRecycleBoxLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        multiselect: True
        touch_multiselect: True
''')


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class FilesLabel(RecycleDataViewBehavior, GridLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(False)
    cols = 2

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.label1_text = data['label2']['text']
        return super(FilesLabel, self).refresh_view_attrs(
            rv, index, data)

    def removeFile(self, name):
        global files
        files.remove(name)
        root = App.get_running_app()
        root.files_list.build_files_list()

class FilesRecycleView(RecycleView):
    global files

    def build_files_list(self):
        self.data = []
        for x in files:
            d = {'label2': {'text': x}}
            self.data.append(d)
        self.refresh_from_data()