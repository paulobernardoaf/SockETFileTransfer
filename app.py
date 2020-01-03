import _thread
import tkinter as tk
from tkinter import tix
import socket
import pickle

address = ("localhost", 20000)

# Create sockets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)

clients = []

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
        self.clients_list = tk.tix.Listbox(listvariable=clients)

    def client_list(self):
        print("antes de criar a listbox", clients)
        self.clients_list.destroy()
        self.clients_list = tk.tix.Listbox(listvariable=clients)

        for index, client in enumerate(clients):
            self.clients_list.insert(index, client)

        self.clients_list.update()
        self.clients_list.pack(side="left")

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
def clients_list():
    global clients
    while True:
        clients = pickle.loads(client_socket.recv(1024))
        print(clients)

        app.client_list()

_thread.start_new_thread(clients_list, ())
############################################################

root.mainloop()

client_socket.close()