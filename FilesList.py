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
from hurry.filesize import size, alternative

files = []

Builder.load_string('''
<FilesLabel>:
    label1_text: 'label 1 text'
    label2_text: 'label 2 text'
    label3_text: 'label 3 text'
    file_size: '-1'
    pos: self.pos
    size: self.size
    remove_button: True
    add_button: False
    add_func: print('')

    canvas.before:
        Color:
            rgba: (242/255, 242/255, 242/255, .9)
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: rgba("#002140") if not root.add_button else (0, 0, 0, 0)
        Line:
            width: 1
            rectangle: self.x + 20, self.y, self.width - 50, 0
    
    BoxLayout:
        size_hint_x: None
        width: 48 if root.remove_button else 0
        Image:
            source: 'resources/file_icon.png' if root.remove_button else 'resources/blank-icon.png'
            size_hint_x: None
            pos_hint: {'center_x': .5}
    Label:
        id: id_label1
        color: (0, 0, 0, .9)
        text: root.label1_text
        size_hint_x: None
        width: 653 if root.remove_button else 1025 if not root.add_button else 850
        text_size: (580, None)
        halign: 'left' if root.remove_button else 'center'
    BoxLayout:
        size_hint_x: None
        width: 178 if root.remove_button else 0
        Label:
            id: id_file_size
            text: root.file_size if root.remove_button else ''
            color: (0, 0, 0, .9)
            size_hint_x: None
            pos_hint: {'center': .5}
            text_size: (100, None)
            halign: 'center'
    BoxLayout:
        size_hint_x: None
        width: 70 if root.remove_button else 0
        Button:
            id: id_label2
            text: 'Remove'
            size_hint: None, None
            size: (70, 30) if root.remove_button else (0, 0)
            background_color: (0, 0, 0, 0)
            color: (1, 1, 1, 1) if root.remove_button else (0, 0, 0, 0)
            background_normal: ''
            on_press: root.removeFile(id_label1.text, root.file_size)
            pos_hint: {'center_x': .5, 'center_y': .45}
            canvas.before:
                Color:
                    rgba: (1, 77/255, 79/255, 1) if root.remove_button else (0, 0, 0, 0)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [5, 5, 5, 5]
    Button:
        text: 'Add File'
        size_hint: None, None
        width: 100 if root.add_button else 0
        height: 40
        background_color: (0, 0, 0, 0)
        color: (1, 1, 1, 1) if root.add_button else (0, 0, 0, 0)
        background_normal: ''
        on_press: root.add_func()
        font_size: 16
        canvas.before:
            Color:
                rgba: rgba("#1890ff") if root.add_button else (0, 0, 0, 1)
            RoundedRectangle:
                size: self.size
                pos: self.pos
                radius: [5, 5, 5, 5]


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
    cols = 5
    row_force_default = True
    row_default_height = 50

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.label1_text = data['label2']['text']
        self.remove_button = data['button']

        root = App.get_running_app()
        self.add_func = root.show_popup

        return super(FilesLabel, self).refresh_view_attrs(
            rv, index, data)

    def removeFile(self, name, file_size):
        global files
        files.remove((name, file_size))
        root = App.get_running_app()
        root.files_list.build_files_list()


class FilesRecycleView(RecycleView):
    global files

    def build_files_list(self):
        self.data = []
        for x in files:
            d = {'label2': {'text': x[0]}, 'file_size': x[1], 'button': True, 'add_button': False}
            self.data.append(d)

        if len(self.data) == 0:
            self.data.append({'label2': {'text': 'No file selected'}, 'button': False, 'add_button': False})

        self.data.append({'label2': {'text': ''}, 'button': False, 'add_button': True})

        self.refresh_from_data()