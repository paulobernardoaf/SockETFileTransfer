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

    info = {'clients': list}

    print(info)
    for client in clients:
        client[0].sendto(pickle.dumps(info), client[1])


def percentage(part, whole):
    return 100 * float(part) / float(whole)

def search_server_input(tuple):
    for x in clients:
        if x[1] == tuple:
            return x[0]

    print("NO SERVER_INPUTS FOUND")
    return None


def server_handle_files(sock, files_sizes, files_names, destinations, sender, files_quantity):


    for client in destinations:
        client = client.split(':')
        info = {'files_sizes': files_sizes, 'files_names': files_names}
        destination = (client[0], int(client[1]))
        # print("DESTINATION AND SENDER", destination, sender)
        if destination != sender:
            client_sock = search_server_input(destination)
            if client_sock:
                client_sock.sendto(pickle.dumps(info), destination)

    for i in range(files_quantity):
        received = 0
        while received < files_sizes[i]:
            if files_sizes[i] - received >= 65536:
                packet = sock.recv(65536)
            else:
                packet = sock.recv(files_sizes[i] - received)
            if not packet:
                return None

            pack_length = len(packet)

            received += pack_length

            for client in destinations:# TODO NOT WORKING PROBABLY
                client = client.split(':')
                destination = (client[0], int(client[1]))
                if destination != sender:
                    client_sock = search_server_input(destination)
                    if client_sock:
                        # print("sending to => ", destination, "   bytes => ", pack_length)
                        client_sock.sendto(packet, destination)
            # print("")
        print('success on receiving and saving {} for {}'.format(files_names[i], server_input.getpeername()))
        print('received a total of: ', received)
    return


def handle_response(server_input, addr, response):
    print(response)
    resp = pickle.loads(response)
    if 'files_sizes' in resp:
        if len(resp['destinations']) > 0:
            print("Will receive ", len(resp['files_sizes']), " files")
            destinations = resp['destinations'].split(";")
            destinations = list(dict.fromkeys(destinations))    # removes duplicates

            server_handle_files(server_input, resp['files_sizes'], resp['files_names'], destinations, addr, len(resp['files_sizes']))
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
                clients.remove((server_input, addr))
                clients_list()
                break
            if response == b"exit":
                print(f'{addr} DISCONNECTED')
                clients.remove((server_input, addr))
                clients_list()
                break
            handle_response(server_input, addr, response)

            # print(f'{addr} => {response}')
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
