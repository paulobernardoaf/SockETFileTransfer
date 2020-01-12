import _thread
import os
import pickle
import socket
import time

from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget

Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '720')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

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
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
import ClientsList
import FilesList



address = ("localhost", 20000)

# Create sockets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)

Builder.load_file("kvFile.kv")


class DestinationsPopup(FloatLayout):
    destinations_list = ClientsList.ClientsRecycleView()

    def build(self):
        self.main_box = BoxLayout(orientation='vertical', spacing=10, padding=(0,10,0,0))
        self.destinations_list = ClientsList.ClientsRecycleView()
        self.destinations_list.build_client_list(client_socket.getsockname())

        self.send_button = Button(text="Send Files", size_hint=(None, None), size=(120, 50),
                                               pos_hint={'center_x': .5}, color=get_color_from_hex("#F2F2F2"),
                                               background_color=get_color_from_hex("#1890ff"), font_size=18,
                                               on_release=self.send_files)


        self.main_box.add_widget(self.destinations_list)
        self.main_box.add_widget(self.send_button)
        return self.main_box

    def send_files(self, obj):
        selected_destinations = ""
        for x in self.destinations_list.viewclass.selected_items:
            selected_destinations += x['text'] + ";"
        selected_destinations = selected_destinations[0:-1]
        print(selected_destinations)

        if len(selected_destinations) == 0:
            print("Select at least 1 destination")
            return

        files_sizes = []
        files_names = []
        for file_path in FilesList.files:
            file = open(file_path, 'rb')

            name = os.path.basename(os.path.normpath(file_path))

            # move to end of file
            file.seek(0, 2)
            # get current position
            size = file.tell()
            # go back to start of file
            file.seek(0, 0)

            files_sizes.append(size)
            files_names.append(name)

        pre_info = {'files_sizes': files_sizes, 'files_names': files_names,
                    'destinations': selected_destinations}
        print(pre_info)
        client_socket.send(pickle.dumps(pre_info))

        for file_path in FilesList.files:

            selected_file = open(file_path, 'rb')

            file_name = os.path.basename(os.path.normpath(file_path))

            # move to end of file
            selected_file.seek(0, 2)
            # get current position
            file_size = selected_file.tell()
            # go back to start of file
            selected_file.seek(0, 0)

            sent = 0
            while True:
                if file_size - sent > 65536:
                    buf = selected_file.read(65536)
                else:
                    buf = selected_file.read(file_size - sent)
                if buf:
                    client_socket.send(buf)
                    sent += len(buf)
                else:
                    break

            print("File sent: ", file_name, " Total of: ", sent, " bytes")
        app.destinations_popup.dismiss()


class P(FloatLayout):

    def build(self):
        self.main_box = BoxLayout(orientation='vertical', spacing=10)
        self.files_box = BoxLayout(orientation='horizontal', spacing=20)
        self.button_box = BoxLayout(orientation='horizontal', spacing=20)

        filechooser = FileChooserListView(filters=[lambda folder, filename: not filename.endswith('.sys')])
        filechooser.bind(on_selection=lambda x: self.selected(filechooser.selection))

        open_btn = Button(text='open', size_hint=(1, .2))
        open_btn.bind(on_release=lambda x: self.open(filechooser.selection))

        self.main_box.add_widget(filechooser)
        self.main_box.add_widget(open_btn)
        return self.main_box

    def selected(self, filename):
        print("selected: %s" % filename[0])

    def open(self, filename):
        if filename:
            FilesList.files.append(filename[0])

            app.files_list.build_files_list()
            app.popup_window.dismiss()


class CustomLayout(BoxLayout):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(CustomLayout, self).__init__(**kwargs)

        with self.canvas.before:
            Color(0, 0.08, 0.16, 1)  # colors range from 0-1 instead of 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class BorderBox(BoxLayout):

    def __init__(self, orientation='', spacing=0, size_hint=(None, None), padding=(0, 0, 0, 0)):
        super().__init__()
        self.orientation = orientation
        self.spacing = spacing
        self.size_hint = size_hint
        self.padding = padding

    def build(self):
        return self


class RoundedButton(Button):

    def __init__(self, text="", on_release=None, size_hint=(None, None), size=(None, None), pos_hint={'center_x': .5},
                 color=(1, 1, 1, 1), background_color=(0, 0, 0, 1), font_size=12):
        super().__init__()
        self.text = text
        self.on_release = on_release
        self.size_hint = size_hint
        self.size = size
        self.pos_hint = pos_hint
        self.color = color
        self.back_color = background_color
        self.font_size = font_size

    def build(self):
        return self


class Application(App):
    clients_list = ClientsList.ClientsRecycleView()
    clients_list_for_popup = ClientsList.ClientsRecycleView()
    files_list = FilesList.FilesRecycleView()
    popup_window = Popup()
    destinations_popup = Popup()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clients_list = ClientsList.ClientsRecycleView()
        self.files_list   = FilesList.FilesRecycleView()

        if len(self.files_list.data) == 0:
            self.files_list.data.append({'label2': {'text': 'No file selected'}, 'button': False, 'add_button': False})
        self.files_list.data.append({'label2': {'text': ''}, 'button': False, 'add_button': True})

    def build(self):
        self.box = BoxLayout(orientation='horizontal', spacing=0)
        self.left_box = CustomLayout(orientation='vertical', spacing=10, size_hint_x=None, width=250)
        self.right_box = BoxLayout(orientation='vertical', spacing=10, padding=(20, -15, 10, 20))
        self.name_logo_box = BoxLayout(orientation='horizontal', spacing=60, size_hint=(None, None), height=110)


        self.title_box = BorderBox(orientation='horizontal', spacing=50, size_hint=(1, None),
                                   padding=(10, 0, 0, 0)).build()

        self.app_logo = Image(source='resources/logo.png', size_hint=(None, None), size=(100, 100))

        self.client_list_label = Label(text="[color=#F2F2F2]Files[b]Transfer[/b][/color]", font_size="25sp",
                                       size_hint=(1, None), height=90, markup=True)

        self.files_list_label = Label(text="[color=#1890ff]Selected files[/color]", font_size="18sp",
                                      size_hint=(None, None), halign='right', height=50, markup=True)

        self.quit_button = Button(text="Quit", on_press=self.close_and_quit, size_hint=(1, .1),
                                  color=get_color_from_hex("#F2F2F2"), background_color=get_color_from_hex("#002140"),
                                  background_normal='')

        self.send_files_button = RoundedButton(text="Select destinations", size_hint=(None, None), size=(170, 50),
                                               pos_hint={'right': .96}, color=get_color_from_hex("#F2F2F2"),
                                               background_color=get_color_from_hex("#1890ff"), font_size=18,
                                               on_release=self.show_destinations_popup).build()

        self.name_logo_box.add_widget(self.app_logo)
        self.name_logo_box.add_widget(self.client_list_label)
        self.left_box.add_widget(self.name_logo_box)
        self.left_box.add_widget(self.clients_list)
        self.left_box.add_widget(self.quit_button)

        self.title_box.add_widget(self.files_list_label)

        self.right_box.add_widget(self.title_box)
        self.right_box.add_widget(self.files_list)
        self.right_box.add_widget(self.send_files_button)

        self.box.add_widget(self.left_box)
        self.box.add_widget(self.right_box)

        return self.box

    def show_popup(self):
        show = P().build()

        self.popup_window = Popup(title="Select a file", content=show, size_hint=(None, None), size=(400, 400))

        self.popup_window.open()

    def show_destinations_popup(self):
        show = DestinationsPopup().build()

        self.destinations_popup = Popup(title="Select the destinations", title_size=18, title_align='center', content=show,
                                        size_hint=(None, None), size=(400, 400), separator_color=get_color_from_hex("#1890ff"),
                                        background='resources/branco.jpg', background_color=get_color_from_hex("#001529"))

        self.destinations_popup.open()

    def close_and_quit(self, obj):
        print("exiting...")
        client_socket.send(b"exit")
        client_socket.close()
        App.get_running_app().stop()
        Window.close()

    def print_selected(self, obj):
        print(self.clients_list.viewclass.selected_items)

    def send_files(self):

        selected_destinations = ""
        for x in Application.clients_list.viewclass.selected_items:
            selected_destinations += x['text'] + ";"
        selected_destinations = selected_destinations[0:-1]
        print(selected_destinations)

        if len(selected_destinations) == 0:
            print("Te peguei")
            return

        self.files_sizes = []
        self.files_names = []
        for file_path in FilesList.files:

            file = open(file_path, 'rb')

            name = os.path.basename(os.path.normpath(file_path))

            # move to end of file
            file.seek(0, 2)
            # get current position
            size = file.tell()
            # go back to start of file
            file.seek(0, 0)

            self.files_sizes.append(size)
            self.files_names.append(name)

        pre_info = {'files_sizes': self.files_sizes, 'files_names': self.files_names, 'destinations': selected_destinations}
        print(pre_info)
        client_socket.send(pickle.dumps(pre_info))

        for file_path in FilesList.files:

            self.selected_file = open(file_path, 'rb')

            self.file_name = os.path.basename(os.path.normpath(file_path))

            # move to end of file
            self.selected_file.seek(0, 2)
            # get current position
            self.file_size = self.selected_file.tell()
            # go back to start of file
            self.selected_file.seek(0, 0)

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

            print("File sent: ", self.file_name, " Total of: ", sent, " bytes")


app = Application()


def percentage(part, whole):
    return 100 * float(part) / float(whole)


def handle_files(sock, files_sizes, files_names, quantity):
    for i in range(quantity):
        st = time.time()
        data = bytearray()
        dest = '{}'.format(files_names[i])
        received = 0
        print("Need to receive: ", files_sizes[i], " bytes")
        with open(dest, 'ab+') as f:
            while received < files_sizes[i]:
                if files_sizes[i] - received >= 65536:
                    packet = sock.recv(65536)
                else:
                    packet = sock.recv(files_sizes[i] - received)
                if not packet:
                    return None
                pack_received = len(packet)
                received += pack_received
                print("received =>", pack_received)
                data.extend(packet)
                f.write(data)
                data = bytearray()
                if time.time() - st >= 1:  # opcional, informacao sobre o total ja carregado
                    print('bytes downloaded:', percentage(received, files_sizes[i]))
                    st = time.time()
        print('success on receiving and saving {} with {} bytes'.format(files_names[i], received))
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

            if 'files_sizes' in response:
                handle_files(client_socket, response['files_sizes'], response['files_names'], len(response['files_sizes']))
        except ConnectionAbortedError:
            client_socket.close()
            return
        except EOFError:
            continue

        app.clients_list.build_client_list(client_socket.getsockname())
        app.clients_list_for_popup.build_client_list(client_socket.getsockname())


_thread.start_new_thread(clients_list, ())

app.run()
