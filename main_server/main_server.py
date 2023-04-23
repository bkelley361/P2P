import socket
import random
import os
import threading
import json

HOST = 'localhost'
PORT = 8695
BUFFER_SIZE = 1024

def delete_manifest(filename):
    manifest = filename
    root_dir = os.path.join(os.getcwd(), 'root')
    manifest = os.path.join(root_dir, manifest)
    if os.path.exists(manifest):
        os.remove(manifest)

def server_connect_to_data_connection(server_address):
    """Connect to the server at the given address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(server_address)
    return s

def find_keywords(data, connection):
    _, keyword = data.split()
    keyword = keyword.decode()
    data = connection.recv(BUFFER_SIZE)
    if not data:
        connection.sendall(b'ERROR')
    else:
        data = data.decode()
        ip_address, port = data.split(":")
        server_address = (ip_address, int(port))
        data_connection = server_connect_to_data_connection(server_address)
        root_dir = os.path.join(os.getcwd(), 'root')
        path = os.listdir(root_dir)
        send_data = ''
        for filename in path:
            count = 0
            if filename.endswith('.json'):
                print(f'File {filename} opened')
                print(f'keyword - {keyword}')
                file_path = os.path.join(root_dir, filename)
                with open(file_path, 'rb') as f:
                    print(f'keyword - {keyword}')
                    data_json = json.load(f)
                    server_address = data_json['server_address']
                    server_port = data_json['server_port']
                    for file_data in data_json['files']:
                        print(file_data['keywords'])
                        if keyword in file_data['keywords']:
                            filename = file_data['filename']
                            if count == 0:
                                send_data += "HOST ADDRESS: " + str(server_address) + '-:-'
                                send_data += "PORT NUMBER: " + str(server_port) + '-:-'
                                send_data += "FILENAME: " + str(filename) + '-:-'
                                count += 1
                            else:
                                send_data += "FILENAME: " + str(filename) + '-:-'
        if send_data == '':
            send_data = "NO FILE FOUND"
        send_data = send_data.encode()
        data_connection.sendall(send_data)
        data_connection.close()

def store_manifest(s, filename):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as data_socket:
        PORT = random.randint(8696, 9999)
        s.sendall(f'{HOST}:{PORT}'.encode())
        data_socket.bind((HOST, PORT))
        data_socket.listen()
        print(f'Data connection started at - {HOST}:{PORT}')
        while True:
            connection, addr = data_socket.accept()
            print(f'Connected to - {addr[0]}:{addr[1]}')
            try:
                if data.decode() == 'ERROR':
                    print('Error when retrieving file from server')
                    break
            except:
                print("Image recieved")
            root_dir = os.path.join(os.getcwd(), 'root')
            filename = os.path.join(root_dir, filename)
            with open(filename, 'wb') as f:
                while True:
                    data = connection.recv(BUFFER_SIZE)
                    if not data:
                        break
                    f.write(data)
            print(f'File {filename} received from server')
            data_socket.close()
            break

def start_main(connection, addr, s):
    print(f'Connected to - {addr[0]}:{addr[1]}')
    filename = f'manifest-{addr[0]}-{addr[1]}.json'
    while True:
        data = connection.recv(BUFFER_SIZE)
        if data == b'QUIT':
            delete_manifest(filename)
            connection.close()
            print(f'Connection closed by - {addr[0]}:{addr[1]}')
            break
        elif data.startswith(b'KEY'):
            find_keywords(data, connection)
        elif data.startswith(b'STOR'):
            store_manifest(connection, filename)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f'Server started at - {HOST}:{PORT}')
    while True:
        connection, addr = s.accept()
        t = threading.Thread(target=start_main, args=(connection, addr, s))
        t.start()