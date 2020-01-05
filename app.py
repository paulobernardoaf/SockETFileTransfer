import _thread
import pickle
import socket
from subprocess import Popen, PIPE

from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '720')

import tkinter as tk
from tkinter import filedialog

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from  kivy.uix.filechooser import FileChooser



address = ("localhost", 20000)

# Create sockets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)

clients = []


Builder.load_string('''
<SelectableLabel>:
    # Draw a background to indicate selection
    canvas.before:
        Color:
            rgba: (.0, 0.9, .1, .3) if self.selected else (0, 0, 0, 1)
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: (255, 0, 255, 1)
        Line:
            width: 2
            rectangle: self.x, self.y, self.width, self.height
<ClientsRecycleView>:
    viewclass: 'SelectableLabel'
    SelectableRecycleBoxLayout:        
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        multiselect: True
        touch_multiselect: True
<Filechooser>: 
      
    label: label 
  
    # Providing the orentation 
    orientation: 'vertical'
  
    # Creating the File list / icon view 
      
    BoxLayout: 
  
        # Creating list view one side 
        FileChooserListView: 
            canvas.before: 
                Color: 
                    rgb: .4, .5, .5
                Rectangle: 
                    pos: self.pos 
                    size: self.size 
            on_selection: root.select(*args) 
  
        # Creating Icon view other side 
        FileChooserIconView: 
            canvas.before: 
                Color: 
                    rgb: .5, .4, .5
                Rectangle: 
                    pos: self.pos 
                    size: self.size 
            on_selection: root.select(*args) 
  
    # Adding label 
    Label: 
        id: label 
        size_hint_y: .1
        canvas.before: 
            Color: 
                rgb: .5, .5, .4
            Rectangle: 
                pos: self.pos 
                size: self.size
''')


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

    def build_client_list(self):
        print("antes de criar a listbox", clients)
        self.data = [{'text': str(x[0]) + ':' + str(x[1])} for x in clients]
        self.refresh_from_data()
        print(self.data)



class Application(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clients_list = ClientsRecycleView()

    def build(self):
        self.box = BoxLayout(orientation='horizontal', spacing=20)
        self.quit_button = Button(text="Quit", on_press=self.close_and_quit, size_hint=(.1, .1))
        self.print_selected_button = Button(text="Print", on_press=self.print_selected, size_hint=(.1, .1))
        self.box.add_widget(self.quit_button)
        self.box.add_widget(self.clients_list)
        self.box.add_widget(self.print_selected_button)
        self.file_selector_button = Button(text="Select File", on_press=self.open_file_selector, size_hint=(.1, .1))
        self.box.add_widget(self.file_selector_button)
        return self.box

    def close_and_quit(self, obj):
        print("exiting...")
        client_socket.send(b"exit")
        client_socket.close()
        App.get_running_app().stop()
        Window.close()

    def print_selected(self, obj):
        print(self.clients_list.viewclass.selected_items)

    def open_file_selector(self, obj):
        root = tk.Tk()
        root.withdraw()

        self.file_path = filedialog.askopenfilename()
        print(self.file_path)




app = Application()


############################################################
# VAMOS TER Q MUDAR ISSO POIS OS CLIENTES VAO TER Q RECEBER COISAS ALEM DA LISTA DE CLIENTES
# PROVAVELMENTE VAMOS TER QUE ENVIAR UMA LABEL INICIAL PARA DIFERENCIAR CADA TIPO DE MENSAGEM
# SE FOR A LISTA DE CLIENTES COMEÇA COM client_list, SE FOR ARQUIVO PARA SER RECEBIDO VAI SER new_file
# E ASSIM POR DIANTE
def clients_list():
    global clients
    while True:
        try:
            clients = pickle.loads(client_socket.recv(1024))
        except ConnectionAbortedError:
            client_socket.close()
            return

        app.clients_list.build_client_list()


_thread.start_new_thread(clients_list, ())
###################a#########################################


app.run()
