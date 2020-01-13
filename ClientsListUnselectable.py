from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.lang import Builder

clients = []

Builder.load_string('''
<UnSelectableLabel>:
    # Draw a background to indicate selection
    canvas.before:
        Color:
            rgba: rgba("#1890ff") if self.selected else rgba("#001529")
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: rgba("#002140")
        Line:
            width: 1
            rectangle: self.x + 20, self.y, self.width - 50, 0

<UnClientsRecycleView>:
    viewclass: 'UnSelectableLabel'
    UnSelectableRecycleBoxLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        multiselect: True
        touch_multiselect: True

''')


class UnSelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''

class UnSelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(False)
    selected_items = []

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(UnSelectableLabel, self).refresh_view_attrs(rv, index, data)


class UnClientsRecycleView(RecycleView):
    global clients

    def build_client_list(self, sock):
        self.data = []
        self.data = [{'text': str(x[0]) + ':' + str(x[1])} for x in clients]
        self.refresh_from_data()