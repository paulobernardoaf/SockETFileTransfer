import tkinter as tk
import socket

address = ("localhost", 20000)

# Create sockets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.close_and_quit)
        self.quit.pack(side="bottom")

    def say_hi(self):
        print("hi there, everyone!")

    def close_and_quit(self):
        print("exiting...")
        client_socket.close()
        self.master.destroy()




root = tk.Tk()
root.geometry("500x100")
app = Application(master=root)
app.mainloop()

client_socket.close()




