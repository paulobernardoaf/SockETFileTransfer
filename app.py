import _thread
import pickle
import socket

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView

address = ("localhost", 20000)

# Create sockets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)

clients = []


Builder.load_string('''
<ClientsRecycleView>:
    viewclass: 'Label'
    RecycleBoxLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
''')


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
        self.box.add_widget(self.quit_button)
        self.box.add_widget(self.clients_list)
        return self.box

    def close_and_quit(self, obj):
        print("exiting...")
        client_socket.send(b"exit")
        client_socket.close()
        App.get_running_app().stop()
        Window.close()




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
