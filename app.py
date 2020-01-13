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
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileSystemAbstract
from hurry.filesize import size, alternative
import ClientsList
import ClientsListUnselectable
import FilesList
import ReceivedFilesList


address = ("localhost", 20000)

# Create sockets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)

Builder.load_file("kvFile.kv")

flag = 0

class DestinationsPopup(FloatLayout):
    destinations_list = ClientsList.ClientsRecycleView()

    def build(self):
        self.main_box = BoxLayout(orientation='vertical', spacing=10, padding=(0,10,0,0))
        self.destinations_list = ClientsList.ClientsRecycleView()
        self.destinations_list.build_client_list(client_socket.getsockname())

        self.send_button = Button(text="Send Files", size_hint=(1, None), height=50,
                                               color=get_color_from_hex("#F2F2F2"), background_normal='',
                                               background_color=get_color_from_hex("#1890ff"), font_size=18,
                                               on_release=self.send_files)

        self.no_clients_label = Label(text="No clients connected", font_size=16, size_hint=(1, None), pos_hint={'top': 1})

        if len(self.destinations_list.data) == 0:
            self.main_box.add_widget(self.no_clients_label)

        self.main_box.add_widget(self.destinations_list)
        self.main_box.add_widget(self.send_button)
        return self.main_box

    def send_files(self, obj):
        selected_destinations = ""
        for x in self.destinations_list.viewclass.selected_items:
            selected_destinations += x['text'] + ";"
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

        client_socket.send(pickle.dumps(pre_info))

        for file_info in FilesList.files:
            file_path = file_info[0]
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

        app.destinations_popup.dismiss()


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

class ReceiveConfirmationPopup(FloatLayout):

    selection = ''
    files_names = []
    files_sizes = []

    def build(self, files, files_sizes):
        self.files_names = files
        self.files_sizes = files_sizes

        self.main_box = BoxLayout(orientation='vertical', spacing=10)
        self.text_box = BoxLayout(orientation='horizontal', spacing=20)
        self.button_box = BoxLayout(orientation='horizontal', spacing=20)

        label_text = "Do you want receive " + str(len(files)) + " files?"

        label = Label(text=label_text, size_hint=(None, 1))

        yes_button = Button(text="Yes", background_color=get_color_from_hex("#1890ff"),
                            background_normal='', color=get_color_from_hex("#F2F2F2"), on_release=lambda x:self.f_yes_button)
        no_button = Button(text="No", background_color=get_color_from_hex("#ed484c"),
                            background_normal='', color=get_color_from_hex("#F2F2F2"), on_release=lambda x:self.f_no_button)

        self.text_box.add_widget(label)
        self.button_box.add_widget(yes_button)
        self.button_box.add_widget(no_button)

        self.main_box.add_widget(self.text_box)
        self.main_box.add_widget(self.button_box)

        return self.main_box

    def f_yes_button(self, obj):
        print("to printaksdlnkas")
        self.selection = 'yes'
        app.receive_popup.dismiss()
        
    
    def f_no_button(self, obj):
        self.selection = 'no'
        app.receive_popup.dismiss()
    
    def reset_selection(self):
        self.selection = ''

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

    def __init__(self, orientation='', spacing=0, size_hint=(None, None), padding=(0, 0, 0, 0), final_x=50, line_width=1):
        super().__init__()
        self.orientation = orientation
        self.spacing     = spacing
        self.size_hint   = size_hint
        self.padding     = padding
        self.final_x     = final_x
        self.line_width  = line_width

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
    clients_list_unselectable = ClientsListUnselectable.UnClientsRecycleView()
    clients_list_for_popup = ClientsList.ClientsRecycleView()
    files_list = FilesList.FilesRecycleView()
    received_files_list = ReceivedFilesList.ReceivedFilesRecycleView()
    popup_window = Popup()
    destinations_popup = Popup()
    receive_popup = Popup(title="Incoming Files:", title_size=18, title_align='center',
                        content=Label(text="", font_size=16),
                        size_hint=(None, None), size=(250, 150), separator_color=get_color_from_hex("#1890ff"),
                        background='resources/background.jpg')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clients_list_unselectable = ClientsListUnselectable.UnClientsRecycleView()
        self.clients_list_unselectable.build_client_list(client_socket.getsockname())
        self.files_list   = FilesList.FilesRecycleView()
        self.received_files_list = ReceivedFilesList.ReceivedFilesRecycleView()
        self.received_files_list.build_files_list()
        self.right_page = 'selected_files'

        if len(self.files_list.data) == 0:
            self.files_list.data.append({'label2': {'text': 'No file selected'}, 'button': False, 'add_button': False})
        self.files_list.data.append({'label2': {'text': ''}, 'button': False, 'add_button': True})

    def select_right_page(self, instance, value):
        if value == 'received_files':
            ReceivedFilesList.files = []
            for subdir, dirs, files in os.walk('./received_files'):
                for file in files:
                    print(file)
                    with open('./received_files/'+file) as fn:
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

    def show_confirmation_popup(self, response):
        self.receive_popup.content = ReceiveConfirmationPopup().build(response['files_names'], response['files_sizes'])
        self.receive_popup.open()
        self.receive_popup.bind(on_dismiss=waiting_for_answer)

    def build_right_box(self):
        self.title_box = BoxLayout(orientation='horizontal', spacing=50, size_hint=(1, None),
                                   padding=(77, 0, 0, 0))

        if self.right_page == 'selected_files':
            first_title  = 'Selected files'
            first_ref    = 'selected_files'
            second_title = 'Received Files'
            second_ref  = 'received_files'

            self.send_files_button = RoundedButton(text="Select destinations", size_hint=(None, None), size=(170, 50),
                                               pos_hint={'right': .96}, color=get_color_from_hex("#F2F2F2"),
                                               background_color=get_color_from_hex("#1890ff"), font_size=18,
                                               on_release=self.show_destinations_popup).build()

            self.connected_clients_label_box = BorderBox(orientation='horizontal', size_hint=(1, .1),
                                    padding=(20, 5, 5, 10), final_x=5, line_width=1.3).build()

        else:
            first_title  = 'Received files'
            first_ref    = 'received_files'
            second_title = 'Selected Files'
            second_ref  = 'selected_files'
                       
        self.files_list_label = Label(text="[u][b]" + first_title + "[/b][/u]",font_size=42, size_hint=(None, None),
                                    height=50, color=(0, 33/255, 64/255/ 1), markup=True)
        self.received_list_label = Label(text="[ref="+ second_ref +"]"+ second_title +"[/ref]", font_size=42, size_hint=(None, None),
                                    width=1200, height=50, color=(0, 33/255, 64/255, .5), markup=True)
        self.received_list_label.bind(on_ref_press=self.select_right_page)

        self.header_box = BorderBox(orientation="horizontal", spacing=0, size_hint=(1, None),
                                    padding=(15, 0, 0, 0)).build()
        self.header_box.height = 30

        self.file_name_label = Label(text="Name", font_size=18, size_hint=(None, None), width=662,
                                     height=30, text_size=(662,None), halign='left', color=(0, 0, 0, .75))
        self.file_size_label = Label(text="Size", font_size=18, size_hint=(None, None), width=170,
                                     height=30, text_size=(100,None), halign='left', color=(0, 0, 0, .75))
        self.action_label    = Label(text="Action", font_size=18, size_hint=(None, None), width=100,
                                     height=30, text_size=(100,None), halign='center', color=(0, 0, 0, .75))


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
        self.left_box = CustomLayout(orientation='vertical', spacing=10, size_hint_x=None, width=250)
        self.right_box = BoxLayout(orientation='vertical', spacing=10, padding=(20, -15, 10, 20))
        self.name_logo_box = BoxLayout(orientation='horizontal', spacing=60, size_hint=(None, None), height=110)


        self.app_logo = Image(source='resources/logo.png', size_hint=(None, None), size=(100, 100))

        self.client_list_label = Label(text="[color=#F2F2F2]Files[b]Transfer[/b][/color]", font_size="25sp",
                                       size_hint=(1, None), height=90, markup=True)

        self.quit_button = Button(text="Quit", on_press=self.close_and_quit, size_hint=(1, .1),
                                  color=get_color_from_hex("#F2F2F2"), background_color=get_color_from_hex("#002140"),
                                  background_normal='')

        self.connected_clients_label = Label(text="Connected clients:", font_size="18sp",
                                       size_hint=(1, None), text_size=(250,30), height=30, markup=True, halign='left')


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

        return self.box

    def show_popup(self):
        show = P().build()

        self.popup_window = Popup(title="Select a file", title_size=18, title_align='center', content=show,
                                size_hint=(None, None), size=(600, 400), separator_color=get_color_from_hex("#1890ff"),
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
            size = (250,150)

        self.destinations_popup = Popup(title=title, title_size=18, title_align='center', content=show,
                                        size_hint=(None, None), size=size, separator_color=get_color_from_hex("#1890ff"),
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
    for i in range(quantity):
        st = time.time()
        data = bytearray()
        dest = 'received_files/{}'.format(files_names[i])
        received = 0
        # print("Need to receive: ", files_sizes[i], " bytes")
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
                # print("received =>", pack_received)
                data.extend(packet)
                f.write(data)
                data = bytearray()
                # if time.time() - st >= 1:  # opcional, informacao sobre o total ja carregado
                    # print('bytes downloaded:', percentage(received, files_sizes[i]))
                #     st = time.time()
        # print('success on receiving and saving {} with {} bytes'.format(files_names[i], received))
    return


def waiting_for_answer(obj):
    global flag
    if ReceiveConfirmationPopup.selection == 'yes':
        print("ies")
        # handle_files(client_socket, response['files_sizes'], response['files_names'], len(response['files_sizes']))
    else:
        print("no")
        # handle_files(client_socket, response['files_sizes'], response['files_names'], len(response['files_sizes']))

    ReceiveConfirmationPopup().reset_selection()
    flag = 0


def clients_list():
    global flag
    while True:
        try:
            response = ''
            if flag == 0:
                response = client_socket.recv(2048)

                response = pickle.loads(response)

            if 'clients' in response:
                ClientsList.clients = response['clients']
                ClientsListUnselectable.clients = response['clients']

            if 'files_sizes' in response:
                flag = 1
                app.show_confirmation_popup(response)


        except ConnectionAbortedError:
            client_socket.close()
            return
        except EOFError:
            continue

        app.clients_list_unselectable.build_client_list(client_socket.getsockname())
        app.clients_list_for_popup.build_client_list(client_socket.getsockname())


_thread.start_new_thread(clients_list, ())

app.run()
