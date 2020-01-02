#!/usr/bin/python                                                                                                                                                                              

import socket
import _thread

clients = []


def on_new_client(server_input, addr):
    print("Connected clients:", clients)
    while True:
        response = server_input.recv(1024)
        response = response.decode()
        if not response:
            print(f'{addr} DISCONNECTED')
            clients.remove(addr)
            print("Connected clients:", clients)
            break
        print(f'{addr} => {response}')
    server_input.close()
    return


address = ("localhost", 20000)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(address)
server_socket.listen(10)

print('Servidor iniciado')
print('Esperando clientes...')

while True:
    server_input, addr = server_socket.accept()
    print(f'Nova conexao recebida de {addr}')
    clients.append(addr)
    _thread.start_new_thread(on_new_client, (server_input, addr))


