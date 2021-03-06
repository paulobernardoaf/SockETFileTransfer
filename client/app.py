import _thread
import os
import pickle
import socket
import time

from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput

Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '720')
Config.set('input', 'mouse', 'mouse, multitouch_on_demand')

from kivy.core.window import Window
from kivy.utils import get_color_from_hex

Window.clearcolor = get_color_from_hex("#F2F2F2")

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from hurry.filesize import size, alternative
from layoutComponents import BorderBox, CustomLayout, RoundedButton, CustomTextInput
from layoutComponents import ClientsListUnselectable, ClientsList, FilesList, ReceivedFilesList

from kivy.uix.screenmanager import ScreenManager, Screen

sm = ScreenManager()

address = ("localhost", 20000)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)

Builder.load_file("./KvFiles/app.kv")


class DestinationsPopup(FloatLayout):
    destinations_list = ClientsList.ClientsRecycleView()

    def build(self):
        self.main_box = BoxLayout(orientation='vertical', spacing=10, padding=(0, 10, 0, 0))
        self.destinations_list = ClientsList.ClientsRecycleView()
        self.destinations_list.build_client_list(app.sockName)

        self.send_button = Button(text="Send Files", size_hint=(1, None), height=50,
                                  color=get_color_from_hex("#F2F2F2"), background_normal='',
                                  background_color=get_color_from_hex("#1890ff"), font_size=18,
                                  on_press=self.send_files)

        self.no_clients_label = Label(text="No clients connected", font_size=16, size_hint=(1, None),
                                      pos_hint={'top': 1})

        if len(self.destinations_list.data) == 0:
            self.main_box.add_widget(self.no_clients_label)

        self.main_box.add_widget(self.destinations_list)
        self.main_box.add_widget(self.send_button)
        return self.main_box

    def popup_dismiss(self, instance):
        time.sleep(2)
        instance.dismiss()

    def send_files(self, obj):
        selected_destinations = ""
        for x in self.destinations_list.viewclass.selected_items:
            selected_destinations += x['text'].split(" - (")[1].replace(')', '') + ";"
        selected_destinations = selected_destinations[0:-1]

        if len(selected_destinations) == 0:
            show = Popup(title="Error", title_size=18, title_align='center',
                         content=Label(text="Select at least 1 destination", font_size=16),
                         size_hint=(None, None), size=(250, 150), separator_color=get_color_from_hex("#1890ff"),
                         background='resources/background.jpg')

            show.open()
            return

        files_sizes = []
        files_names = []
        for file_info in FilesList.files:
            file_path = file_info[0]
            file = open(file_path, 'rb')

            name = os.path.basename(os.path.normpath(file_path))

            file.seek(0, 2)
            size = file.tell()
            file.seek(0, 0)

            files_sizes.append(size)
            files_names.append(name)

        pre_info = {'files_sizes': files_sizes, 'files_names': files_names,
                    'destinations': selected_destinations}

        client_socket.send(pickle.dumps(pre_info))

        for file_info in FilesList.files:
            file_path = file_info[0]
            selected_file = open(file_path, 'rb')

            selected_file.seek(0, 2)
            file_size = selected_file.tell()
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

        app.destinations_popup.dismiss()

        file_sent_popup = Popup(title='Uploaded File(s)', title_size=16, title_align='center', size_hint=(None, None),
                                size=(600, 50), pos_hint={'center_x': .5, 'center_y': .04},
                                separator_color=(0, 0, 0, .8), background='resources/background2.jpg',
                                on_open=self.popup_dismiss)

        file_sent_popup.open()


class P(FloatLayout):

    def build(self):
        self.main_box = BoxLayout(orientation='vertical', spacing=10)
        self.files_box = BoxLayout(orientation='horizontal', spacing=20)
        self.button_box = BoxLayout(orientation='horizontal', spacing=20)

        filechooser = FileChooserIconView(filters=[lambda folder, filename: not filename.endswith('.sys')])
        filechooser.bind(on_selection=lambda x: self.selected(filechooser.selection))

        open_btn = Button(text='Open', size_hint=(1, .2), background_color=get_color_from_hex("#1890ff"),
                          background_normal='', color=get_color_from_hex("#F2F2F2"))
        open_btn.bind(on_release=lambda x: self.open(filechooser.selection))

        self.main_box.add_widget(filechooser)
        self.main_box.add_widget(open_btn)
        return self.main_box

    def open(self, filename):
        if filename:
            with open(filename[0]) as fn:
                fn.seek(0, 2)
                file_size = size(int(fn.tell()), system=alternative)
                fn.seek(0, 0)

            FilesList.files.append((filename[0], file_size))

            app.files_list.build_files_list()
            app.popup_window.dismiss()
        else:
            show = Popup(title="Error", title_size=18, title_align='center',
                         content=Label(text="Select a File", font_size=16),
                         size_hint=(None, None), size=(250, 150), separator_color=get_color_from_hex("#1890ff"),
                         background='resources/background.jpg')

            show.open()


class Main_GUI(Screen):

    def build(self, content):
        self.add_widget(content)


class Login_GUI(Screen):

    def build(self, content):
        self.add_widget(content)


class Application(App):
    clients_list_unselectable = ClientsListUnselectable.UnClientsRecycleView()
    clients_list_for_popup = ClientsList.ClientsRecycleView()
    files_list = FilesList.FilesRecycleView()
    received_files_list = ReceivedFilesList.ReceivedFilesRecycleView()
    popup_window = Popup()
    destinations_popup = Popup()
    login_popup = Popup()
    error_popup = Popup()
    username = ''
    title = 'SockETFileTransfer'
    icon = 'resources/icon.png'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clients_list_unselectable = ClientsListUnselectable.UnClientsRecycleView()
        self.sockName = client_socket.getsockname()
        self.clients_list_unselectable.build_client_list(self.sockName)
        self.files_list = FilesList.FilesRecycleView()
        self.received_files_list = ReceivedFilesList.ReceivedFilesRecycleView()
        self.received_files_list.build_files_list()
        self.right_page = 'selected_files'

        if len(self.files_list.data) == 0:
            self.files_list.data.append({'label2': {'text': 'No file selected'}, 'button': False, 'add_button': False})
        self.files_list.data.append({'label2': {'text': ''}, 'button': False, 'add_button': True})

    def select_right_page(self, instance, value):
        if value == 'received_files':
            ReceivedFilesList.files = []
            path = os.path.join("received_files", self.login_text_input.text)
            for subdir, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(path, file)
                    with open(file_path) as fn:
                        fn.seek(0, 2)
                        file_size = size(int(fn.tell()), system=alternative)
                        fn.seek(0, 0)

                    ReceivedFilesList.files.append((file, file_size))
            self.received_files_list.build_files_list()

        self.right_page = value
        self.box.remove_widget(self.right_box)
        self.right_box.clear_widgets()
        self.right_box = BoxLayout(orientation='vertical', spacing=10, padding=(20, -15, 10, 20))
        self.build_right_box()
        self.box.add_widget(self.right_box)

    def build_right_box(self):
        self.title_box = BoxLayout(orientation='horizontal', spacing=50, size_hint=(1, None),
                                   padding=(77, 0, 0, 0))

        if self.right_page == 'selected_files':
            first_title = 'Selected files'
            first_ref = 'selected_files'
            second_title = 'Received Files'
            second_ref = 'received_files'

            self.send_files_button = RoundedButton.RoundedButton(text="Select destinations", size_hint=(None, None),
                                                                 size=(170, 50),
                                                                 pos_hint={'right': .96},
                                                                 color=get_color_from_hex("#F2F2F2"),
                                                                 background_color=get_color_from_hex("#1890ff"),
                                                                 font_size=18, border_radius=[5,5,5,5],
                                                                 on_release=self.show_destinations_popup).build()

            self.connected_clients_label_box = BorderBox.BorderBox(orientation='horizontal', size_hint=(1, .1),
                                                                   padding=(20, 5, 5, 10), final_x=5,
                                                                   line_width=1.3).build()

        else:
            first_title = 'Received files'
            first_ref = 'received_files'
            second_title = 'Selected Files'
            second_ref = 'selected_files'

        self.files_list_label = Label(text="[u][b]" + first_title + "[/b][/u]", font_size=42, size_hint=(None, None),
                                      height=50, color=(0, 33 / 255, 64 / 255 / 1), markup=True)
        self.received_list_label = Label(text="[ref=" + second_ref + "]" + second_title + "[/ref]", font_size=42,
                                         size_hint=(None, None),
                                         width=1200, height=50, color=(0, 33 / 255, 64 / 255, .5), markup=True)
        self.received_list_label.bind(on_ref_press=self.select_right_page)

        self.header_box = BorderBox.BorderBox(orientation="horizontal", spacing=0, size_hint=(1, None),
                                              padding=(15, 0, 0, 0)).build()
        self.header_box.height = 30

        self.file_name_label = Label(text="Name", font_size=18, size_hint=(None, None), width=662,
                                     height=30, text_size=(662, None), halign='left', color=(0, 0, 0, .75))
        self.file_size_label = Label(text="Size", font_size=18, size_hint=(None, None), width=170,
                                     height=30, text_size=(100, None), halign='left', color=(0, 0, 0, .75))
        self.action_label = Label(text="Action", font_size=18, size_hint=(None, None), width=100,
                                  height=30, text_size=(100, None), halign='center', color=(0, 0, 0, .75))

        self.title_box.add_widget(self.files_list_label)
        self.title_box.add_widget(self.received_list_label)

        self.header_box.add_widget(self.file_name_label)
        self.header_box.add_widget(self.file_size_label)
        self.header_box.add_widget(self.action_label)

        self.right_box.add_widget(self.title_box)
        self.right_box.add_widget(self.header_box)

        if self.right_page == 'selected_files':
            self.right_box.add_widget(self.files_list)
            self.right_box.add_widget(self.send_files_button)
        else:
            self.right_box.add_widget(self.received_files_list)

    def build(self):
        self.box = BoxLayout(orientation='horizontal', spacing=0)
        self.left_box = CustomLayout.CustomLayout(orientation='vertical', spacing=10, size_hint_x=None, width=250)
        self.right_box = BoxLayout(orientation='vertical', spacing=10, padding=(20, -15, 10, 20))
        self.name_logo_box = BoxLayout(orientation='horizontal', spacing=60, size_hint=(None, None), height=110)

        self.app_logo = Image(source='resources/logo.png', size_hint=(None, None), size=(100, 100))

        self.client_list_label = Label(text="[color=#F2F2F2]File[b]Transfer[/b][/color]", font_size="25sp",
                                       size_hint=(1, None), height=90, markup=True)

        self.quit_button = Button(text="Quit", on_press=self.close_and_quit, size_hint=(1, .1),
                                  color=get_color_from_hex("#F2F2F2"), background_color=get_color_from_hex("#002140"),
                                  background_normal='')

        self.connected_clients_label = Label(text="Connected clients:", font_size="18sp",
                                             size_hint=(1, None), text_size=(250, 30), height=30, markup=True,
                                             halign='left')

        self.build_right_box()

        self.name_logo_box.add_widget(self.app_logo)
        self.name_logo_box.add_widget(self.client_list_label)
        self.connected_clients_label_box.add_widget(self.connected_clients_label)
        self.left_box.add_widget(self.name_logo_box)
        self.left_box.add_widget(self.connected_clients_label_box)
        self.left_box.add_widget(self.clients_list_unselectable)
        self.left_box.add_widget(self.quit_button)

        self.box.add_widget(self.left_box)
        self.box.add_widget(self.right_box)

        main_gui = Main_GUI(name="main")
        main_gui.build(self.box)

        self.login_box = CustomLayout.CustomLayout(orientation='vertical', spacing=50, padding=(0,0,0,180))
        self.login_items_box = BoxLayout(orientation='vertical', spacing=10, size_hint=(1,.3))

        self.login_logo_box = BoxLayout(orientation="horizontal", spacing=0, size_hint=(1,None))
        self.login_app_logo_box = BoxLayout(size_hint=(.55, None), padding=(450,0,0,0))

        self.login_app_logo = Image(source='resources/logo.png', size_hint=(None, None), height=150)

        self.login_app_logo_label = Label(text="[color=#F2F2F2]File[b]Transfer[/b][/color]", font_size="40sp",
                                          size_hint=(1, None), text_size=(640,150), valign='middle', markup=True)

        self.login_app_logo_box.add_widget(self.login_app_logo)
        self.login_logo_box.add_widget(self.login_app_logo_box)
        self.login_logo_box.add_widget(self.login_app_logo_label)

        self.login_welcome = Label(text="Welcome", font_size="28sp",
                                   size_hint=(1, None), markup=True)

        self.login_text_input = CustomTextInput.CustomTextInput(on_text_validate=self.login, size=(500,50),
                                                                background_color=get_color_from_hex("#F2F2F2"),
                                                                hint_text="Please insert an username (max of 14 characters long)",
                                                                font_size='18dp')

        self.login_button = RoundedButton.RoundedButton(text="Login", size=(300,60), font_size=18, on_release=self.login,
                                                        color=get_color_from_hex("#F2F2F2"), border_radius=[30,30,30,30],
                                                        background_color=get_color_from_hex("#1890ff"))

        self.login_items_box.add_widget(self.login_logo_box)
        self.login_items_box.add_widget(self.login_welcome)
        self.login_items_box.add_widget(self.login_text_input)
        self.login_box.add_widget(self.login_items_box)
        self.login_box.add_widget(self.login_button)

        login_gui = Login_GUI(name="login")
        login_gui.build(self.login_box)

        sm.add_widget(login_gui)
        sm.add_widget(main_gui)

        return sm

    def close_error_popup(self, obj):
        self.error_popup.dismiss()

    def login(self):

        long_username_error = Label(text="Username exceed the 14 characters limit.", font_size="16sp",
                                    size_hint=(1, None), height=90, markup=True)
        short_username_error = Label(text="Username can't be blank.", font_size="16sp",
                                     size_hint=(1, None), height=90, markup=True)

        close_button = Button(text="Ok", on_press=self.close_error_popup, size_hint=(1, .1),
                              color=get_color_from_hex("#F2F2F2"), background_color=get_color_from_hex("#002140"),
                              background_normal='')

        long_box = BoxLayout(orientation="vertical", spacing=10)
        long_box.add_widget(long_username_error)

        short_box = BoxLayout(orientation="vertical", spacing=10)
        short_box.add_widget(short_username_error)

        if len(self.login_text_input.text) == 0:
            short_box.add_widget(close_button)
            self.error_popup = Popup(title="Error", title_size=18, title_align='center', content=short_box,
                                     size_hint=(None, None), size=(350, 200),
                                     separator_color=get_color_from_hex("#1890ff"),
                                     background='resources/background.jpg', auto_dismiss=False)
            self.error_popup.open()
            return

        if len(self.login_text_input.text) > 14:
            long_box.add_widget(close_button)
            self.error_popup = Popup(title="Error", title_size=18, title_align='center',
                                     content=long_box,
                                     size_hint=(None, None), size=(350, 200),
                                     separator_color=get_color_from_hex("#1890ff"),
                                     background='resources/background.jpg', auto_dismiss=False)
            self.error_popup.open()
            return

        client_socket.send(bytes(self.login_text_input.text, "utf-8"))

        sm.current = "main"



    def show_popup(self):
        show = P().build()

        self.popup_window = Popup(title="Select a file", title_size=18, title_align='center', content=show,
                                  size_hint=(None, None), size=(600, 400),
                                  separator_color=get_color_from_hex("#1890ff"),
                                  background='resources/background.jpg')

        self.popup_window.open()

    def show_destinations_popup(self):

        if len(FilesList.files) > 0:
            show = DestinationsPopup().build()
            title = "Select the destinations"
            size = (400, 400)
        else:
            show = Label(text="You need to have at least 1 file")
            title = "Error"
            size = (250, 150)

        self.destinations_popup = Popup(title=title, title_size=18, title_align='center', content=show,
                                        size_hint=(None, None), size=size,
                                        separator_color=get_color_from_hex("#1890ff"),
                                        background='resources/background.jpg')
        self.destinations_popup.open()

    def close_and_quit(self, obj):
        print("exiting...")
        client_socket.send(b"exit")
        client_socket.close()
        App.get_running_app().stop()
        Window.close()


app = Application()


def percentage(part, whole):
    return 100 * float(part) / float(whole)


def handle_files(sock, files_sizes, files_names, quantity):

    if not os.path.isdir("received_files"):
        os.mkdir("received_files")
    path = os.path.join("received_files", app.login_text_input.text)

    if not os.path.isdir(path):
        os.mkdir(path)

    for i in range(quantity):
        data = bytearray()
        path = os.path.join("received_files", app.login_text_input.text, files_names[i])
        received = 0
        if os.path.isfile(path):
            os.remove(path)

        with open(path, 'ab+') as f:
            while received < files_sizes[i]:
                if files_sizes[i] - received >= 65536:
                    packet = sock.recv(65536)
                else:
                    packet = sock.recv(files_sizes[i] - received)
                if not packet:
                    return None
                pack_received = len(packet)
                received += pack_received
                data.extend(packet)
                f.write(data)
                data = bytearray()
    return


def clients_list():
    global flag
    while True:
        try:
            response = client_socket.recv(2048)

            response = pickle.loads(response)

            if 'clients' in response:
                ClientsList.clients = response['clients']
                ClientsListUnselectable.clients = response['clients']

            if 'files_sizes' in response:
                handle_files(client_socket, response['files_sizes'], response['files_names'],
                             len(response['files_sizes']))

        except ConnectionAbortedError:
            client_socket.close()
            return
        except EOFError:
            continue

        app.clients_list_unselectable.build_client_list(app.sockName)
        app.clients_list_for_popup.build_client_list(app.sockName)


_thread.start_new_thread(clients_list, ())

app.run()
