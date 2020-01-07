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
            received += len(packet)
            data.extend(packet)
            f.write(data)
            data = bytearray()
            if time.time() - st >= 1:  # opcional, informacao sobre o total ja carregado
                print('bytes downloaded:', percentage(received, file_size))
                st = time.time()
    print('success on receiving and saving {} for {}'.format(file_name, server_input.getpeername()))
    return


def handle_response(server_input, response):
    print(response)
    resp = pickle.loads(response)
    if resp['file_size']:
        print("Will receive a file with: ", resp['file_size'])
        handle_file(server_input, resp['file_size'], resp['file_name'])
    else:
        print(resp)


def on_new_client(server_input, addr):
    # print("Connected clients:", clients)
    while True:
        try:
            response = server_input.recv(2048)
            # response = pickle.loads(response)
            if not response:
                print("NULL RESPONSE")
                break
            if response == b"exit":
                print(f'{addr} DISCONNECTED')
                clients.remove((server_input, addr))
                clients_list()
                break
            handle_response(server_input, response)

            print(f'{addr} => {response}')
        except ConnectionResetError:
            clients.remove((server_input, addr))
            print(f'{addr} SUDDENLY DISCONNECTED')
            clients_list()
            break

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
