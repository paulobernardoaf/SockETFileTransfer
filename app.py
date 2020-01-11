import _thread
import os
import pickle
import socket
import time

from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '720')

from kivy.core.window import Window
from kivy.utils import get_color_from_hex

Window.clearcolor = get_color_from_hex("#F2F2F2")

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
import ClientsList
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup

address = ("localhost", 20000)

# Create sockets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)

Builder.load_file("kvFile.kv")


class P(FloatLayout):

    def build(self):
        self.main_box = BoxLayout(orientation='vertical', spacing=10)
        self.files_box = BoxLayout(orientation='horizontal', spacing=20)
        self.button_box = BoxLayout(orientation='horizontal', spacing=20)

        filechooser = FileChooserListView()
        filechooser.bind(on_selection=lambda x: self.selected(filechooser.selection))

        open_btn = Button(text='open', size_hint=(1, .2))
        open_btn.bind(on_release=lambda x: self.open(filechooser.path, filechooser.selection))

        self.main_box.add_widget(filechooser)
        self.main_box.add_widget(open_btn)
        return self.main_box

    def selected(self, filename):
        print("selected: %s" % filename[0])

    def open(self, path, filename):

        self.file_path = filename[0]
        self.selected_file = open(self.file_path, 'rb')

        self.file_name = os.path.basename(os.path.normpath(self.file_path))

        selected_destinations = ""
        for x in Application.clients_list.viewclass.selected_items:
            selected_destinations += x['text'] + ";"
        selected_destinations = selected_destinations[0:-1]

        print(selected_destinations)

        # move to end of file
        self.selected_file.seek(0, 2)
        # get current position
        self.file_size = self.selected_file.tell()
        # go back to start of file
        self.selected_file.seek(0, 0)

        pre_info = {'file_size': self.file_size, 'file_name': self.file_name, 'destinations': selected_destinations}
        client_socket.send(pickle.dumps(pre_info))

        sent = 0
        while True:
            if self.file_size - sent > 65536:
                buf = self.selected_file.read(65536)
            else:
                buf = self.selected_file.read(self.file_size - sent)
            if buf:
                client_socket.send(buf)
                sent += len(buf)
            else:
                break

        print("file sent")


class CustomLayout(BoxLayout):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(CustomLayout, self).__init__(**kwargs)

        with self.canvas.before:
            Color(0, 0.08, 0.16, 1)  # green; colors range from 0-1 instead of 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class Application(App):
    clients_list = ClientsList.ClientsRecycleView()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clients_list = ClientsList.ClientsRecycleView()

    def build(self):
        self.box = BoxLayout(orientation='horizontal', spacing=50)
        self.left_box = CustomLayout(orientation='vertical', spacing=10, size_hint_x=None, width=250)
        self.right_box = BoxLayout(orientation='vertical', spacing=10)

        self.selected_files = GridLayout(cols=3, row_force_default=True, row_default_height=50)

        self.client_list_label = Label(text="[color=#F2F2F2]Dashy[/color]", font_size="25sp",
                                       size_hint=(1, None), height=50, markup=True)

        self.quit_button = Button(text="Quit", on_press=self.close_and_quit, size_hint=(1, .1),
                                   color=get_color_from_hex("#F2F2F2"), background_color=get_color_from_hex("#002140"), background_normal='')
        self.file_selector_button = Button(text="Add File", on_release=self.show_popup, size_hint=(.5, .1),
                                           pos_hint={'right': .75})

        self.left_box.add_widget(self.client_list_label)
        self.left_box.add_widget(self.clients_list)
        self.left_box.add_widget(self.quit_button)

        self.right_box.add_widget(self.selected_files)
        self.right_box.add_widget(self.file_selector_button)

        self.box.add_widget(self.left_box)
        self.box.add_widget(self.right_box)

        return self.box

    def show_popup(self, obj):
        show = P().build()

        popup_window = Popup(title="JANELINHA", content=show, size_hint=(None, None), size=(400, 400))

        popup_window.open()

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
        if not self.file_path:
            return


app = Application()


def percentage(part, whole):
    return 100 * float(part) / float(whole)


def handle_file(sock, file_size, file_name):
    st = time.time()
    data = bytearray()
    dest = '{}'.format(file_name)
    received = 0
    with open(dest, 'ab+') as f:
        while received < file_size:
            if file_size - received >= 65536:
                packet = sock.recv(65536)
            else:
                packet = sock.recv(file_size - received)
            if not packet:
                return None
            pack_received = len(packet)
            received += pack_received
            print("received =>", pack_received)
            data.extend(packet)
            f.write(data)
            data = bytearray()
            if time.time() - st >= 1:  # opcional, informacao sobre o total ja carregado
                print('bytes downloaded:', percentage(received, file_size))
                st = time.time()
    print('success on receiving and saving {} for {}'.format(file_name, sock.getpeername()))
    return


def clients_list():
    while True:
        try:
            response = client_socket.recv(2048)

            print(response)

            response = pickle.loads(response)

            if 'clients' in response:
                print(response['clients'])
                ClientsList.clients = response['clients']

            if 'file_size' in response:
                print(response['file_size'], response['file_name'])
                print(response)
                handle_file(client_socket, response['file_size'], response['file_name'])


        except ConnectionAbortedError:
            client_socket.close()
            return
        except EOFError:
            continue

        app.clients_list.build_client_list(client_socket.getsockname())


_thread.start_new_thread(clients_list, ())

app.run()