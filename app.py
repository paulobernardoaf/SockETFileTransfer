import _thread
import tkinter as tk
from tkinter import tix
import socket
import pickle
from tkinter.filedialog import askopenfilename

address = ("localhost", 20000)

# Create sockets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)

clients = []


def OpenFile():
    name = askopenfilename(initialdir="C:/Users/Batman/Documents/Programming/tkinter/",
                           filetypes =(("Text File", "*.txt"),("All Files","*.*")),
                           title = "Choose a file."
                           )
    print (name)
    #Using try in case user types in unknown file or closes without choosing a file.
    try:
        with open(name,'r') as UseFile:
            print(UseFile.read())
    except:
        print("No file exists")

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.client_list()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.close_and_quit)
        self.quit.pack(side="bottom")

        self.clients_list = tk.tix.Listbox()

        self.button_list_selected = tk.Button(self, text="PRINT SELECTED", command=self.list_selected)
        self.button_list_selected.pack(side="right")

        self.button_select_file = tk.Button(self, text="Select file", command=OpenFile).pack(side="bottom")

    def client_list(self):
        print("antes de criar a listbox", clients)
        self.clients_list.destroy()
        self.clients_list = tk.tix.Listbox(selectmode=tk.MULTIPLE)

        for index, client in enumerate(clients):
            self.clients_list.insert(index, client)

        self.clients_list.update()
        self.clients_list.pack(side="left")

    def list_selected(self):
        items = map(int, self.clients_list.curselection())
        for x in items:
            print(x)

    def say_hi(self):
        print("hi there, everyone!")

    def close_and_quit(self):
        print("exiting...")
        client_socket.send(b"exit")
        client_socket.close()
        self.master.destroy()


root = tk.Tk()
root.geometry("800x500")
# root.resizable(0,0)
app = Application(master=root)




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

        app.client_list()


_thread.start_new_thread(clients_list, ())
############################################################

root.mainloop()
