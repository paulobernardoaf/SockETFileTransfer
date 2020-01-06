import _thread
import os
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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
import ClientsList


address = ("localhost", 20000)

# Create sockets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)


Builder.load_file("kvFile.kv")


class Application(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clients_list = ClientsList.ClientsRecycleView()

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
        self.selected_file = open(self.file_path, 'rb').read()
        self.file_name = os.path.basename(os.path.normpath(self.file_path))
        info = {'name': self.file_name, 'file': self.selected_file, 'opcao': 'file'}
        print(info)
        client_socket.sendall(pickle.dumps(info))



app = Application()


############################################################
# VAMOS TER Q MUDAR ISSO POIS OS CLIENTES VAO TER Q RECEBER COISAS ALEM DA LISTA DE CLIENTES
# PROVAVELMENTE VAMOS TER QUE ENVIAR UMA LABEL INICIAL PARA DIFERENCIAR CADA TIPO DE MENSAGEM
# SE FOR A LISTA DE CLIENTES COMEÇA COM client_list, SE FOR ARQUIVO PARA SER RECEBIDO VAI SER new_file
# E ASSIM POR DIANTE
def clients_list():
    while True:
        try:
            ClientsList.clients = pickle.loads(client_socket.recv(1024))
        except ConnectionAbortedError:
            client_socket.close()
            return

        app.clients_list.build_client_list()


_thread.start_new_thread(clients_list, ())
###################a#########################################


app.run()
