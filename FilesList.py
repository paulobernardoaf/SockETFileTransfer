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
        Color:
            rgba: rgba("#002140")
        Line:
            width: 1
            rectangle: self.x + 20, self.y, self.width - 50, 0
    label1_text: 'label 1 text'
    label2_text: 'label 2 text'
    label3_text: 'label 3 text'
    pos: self.pos
    size: self.size
    show_button: True
    Label:
        id: id_label1
        color: (0, 0, 0, .9)
        text: root.label1_text
        size_hint_x: None
        width: 850 if root.show_button else 1025
        text_size: (780, None)
        halign: 'left' if root.show_button else 'center'
    Button:
        id: id_label2
        text: 'Remove'
        size_hint: None, None
        width: 100 if root.show_button else 0
        height: 40
        background_color: (1, 77/255, 79/255, 1) if root.show_button else (0, 0, 0, 0)
        color: (1, 1, 1, 1) if root.show_button else (0, 0, 0, 0)
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
        padding: (-20, 0, 20, 0)
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
    row_force_default = True
    row_default_height = 50

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.label1_text = data['label2']['text']
        self.show_button = data['button']

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
            d = {'label2': {'text': x}, 'button': True}
            self.data.append(d)

        if len(self.data) == 0:
            self.data.append({'label2': {'text': 'No file selected'}, 'button': False})

        self.refresh_from_data()