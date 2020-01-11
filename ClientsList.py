from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior


clients = []


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''

class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    selected_items = []

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
            self.selected_items.append(rv.data[index])
        else:
            print("selection removed for {0}".format(rv.data[index]))
            if self.selected_items.__contains__(rv.data[index]):
                self.selected_items.remove(rv.data[index])


class ClientsRecycleView(RecycleView):
    global clients

    def build_client_list(self, sock):
        print("antes de criar a listbox", clients)
        # self.data = []
        # for x in clients:
        #     if x != sock:
        #         self.data.append({'text': str(x[0]) + ':' + str(x[1])})
        self.data = [{'text': str(x[0]) + ':' + str(x[1])} for x in clients]
        self.refresh_from_data()
        print(self.data)