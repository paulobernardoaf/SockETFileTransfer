#!/usr/bin/python

import socket

address = ("localhost", 20000)

# Create sockets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)

# Echo
while True:
    text = input("Informe texto ou digite 'sair' para desconectar: ")
    client_socket.send(text.encode())
    if text == "sair" or text == "close server":
        client_socket.close()
        break
