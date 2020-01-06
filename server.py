#!/usr/bin/python
import socket
import _thread
import pickle
import time

clients = []

def clients_list():
    list = []
    for client in clients:
        list.append(client[1])

    print(clients)
    for client in clients:
        client[0].sendto(pickle.dumps(list), client[1])

def on_new_client(server_input, addr):
    # print("Connected clients:", clients)
    info_bin = b''
    st = time.time()
    while True:
        try:
            response = server_input.recv(2048)
            # response = pickle.loads(response)
            if not response:
                print("NULL RESPONSE")
                break
            print("resp:", response)
            if response == "exit":
                print(f'{addr} DISCONNECTED')
                clients.remove((server_input, addr))
            info_bin += response
            if time.time() - st >= 2:  # opcional, informacao sobre o total ja carregado
                print('bytes downloaded:', len(info_bin))
                st = time.time()
            print(f'{addr} => {response}')
        except ConnectionResetError:
            clients.remove((server_input, addr))
            print(f'{addr} SUDDENLY DISCONNECTED')
        finally:
            clients_list()
            break
    print(info_bin)
    info = pickle.loads(info_bin)
    print("INFO: ", info)
    if info['file']:
        dest = '{}'.format(info['name'])
        with open(dest, 'wb') as f:
            f.write(info['file'])
        print('success on receiving and saving {} for {}'.format(info['name'], server_input.getpeername()))
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
    clients.append((server_input, addr))

    clients_list()

    _thread.start_new_thread(on_new_client, (server_input, addr))