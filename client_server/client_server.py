import socket
import random
import os
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


HOST = 'localhost'
BUFFER_SIZE = 1024
PORT = 8696

NAP_SERVER = 'localhost'
NAP_PORT = 8695

NAP_CONNECTION = None

MANIFEST = 'manifest.json'

CLIENT_CONNECTION = None

def run_client():
    # Create the main window
    root = tk.Tk()
    root.title("GV NAP Server")

    # Create a tab control
    tab_control = ttk.Notebook(root)

    # Create the first tab
    tab1 = ttk.Frame(tab_control)
    tab_control.add(tab1, text="Client")

    def show_error():
        messagebox.showerror("Error", "Something went wrong!")

    # Add buttons and text boxes to tab1
    connect_button = ttk.Button(tab1, text="Connect")
    connect_button.place(relx=0.5, rely=0.8, anchor="center")
    ip_text = ttk.Entry(tab1)
    ip_text.place(relx=0.5, rely=0.4, anchor="center")
    ip_label = ttk.Label(tab1, text="IP Address")
    ip_label.place(relx=0.3, rely=0.4, anchor="center")
    port_text = ttk.Entry(tab1)
    port_text.place(relx=0.5, rely=0.6, anchor="center")
    port_label = ttk.Label(tab1, text="Port")
    port_label.place(relx=0.3, rely=0.6, anchor="center")
    list_button = ttk.Button(tab1, text="List Files")
    retr_button = ttk.Button(tab1, text="Retrieve File")
    send_button = ttk.Button(tab1, text="Send File")
    quit_button = ttk.Button(tab1, text="Quit")

    connected_label = ttk.Label(tab1, text="Not Connected", foreground="red")
    connected_label.place(relx=0.9, rely=0.05, anchor="center")

    filename_text = ttk.Entry(tab1)
    filename_label = ttk.Label(tab1, text="File name")

    view_box = tk.Listbox(tab1, width=50)

    connected_ip = ttk.Label(tab1, text="localhost")
    connected_port = ttk.Label(tab1, text="8695")

    def connect_client(ip, port):
        global CLIENT_CONNECTION
        try:
            server = (ip, int(port))
            CLIENT_CONNECTION = client_connect_to_server(server)
            connect(ip, port)
        except:
            show_error()

    def nap_connect(ip, port):
        global NAP_CONNECTION
        try:
            server = (ip, port)
            NAP_CONNECTION = client_connect_to_server(server)
            connect_nap()
            client_put_file(NAP_CONNECTION, "manifest.json")
        except:
            show_error()

    def connect(ip, port):
        # Remove the connect button and text boxes
        connect_button.place_forget()
        ip_text.delete(0, tk.END)
        ip_text.place_forget()
        ip_label.place_forget()
        port_text.delete(0, tk.END)
        port_text.place_forget()
        port_label.place_forget()

        # Add the other widgets to the left
        list_button.place(relx=0.3, rely=0.2, anchor="center")
        retr_button.place(relx=0.5, rely=0.2, anchor="center")
        send_button.place(relx=0.7, rely=0.2, anchor="center")
        quit_button.place(relx=0.9, rely=0.9, anchor="center")
        filename_text.place(relx=0.5, rely=0.3, anchor="center")
        filename_label.place(relx=0.5, rely=0.4, anchor="center")
        view_box.place(relx=0.5, rely=0.7, anchor="center")

        # Add a label that says "Connected"
        connected_label.config(text="Connected", foreground="green")
        connected_ip.place(relx=0.9, rely=0.1, anchor="center")
        connected_port.place(relx=0.9, rely=0.15, anchor="center")
        connected_ip.config(text=f'{ip}')
        connected_port.config(text=f'{port}')

    def disconnect():
        # Remove the other widgets
        list_button.place_forget()
        retr_button.place_forget()
        send_button.place_forget()
        quit_button.place_forget()
        filename_text.delete(0, tk.END)
        filename_text.place_forget()
        filename_label.place_forget()
        view_box.delete(0, tk.END)
        view_box.place_forget()
        connected_ip.place_forget()
        connected_port.place_forget()

        # Add the connect button and text boxes
        connect_button.place(relx=0.5, rely=0.8, anchor="center")
        ip_text.place(relx=0.5, rely=0.4, anchor="center")
        ip_label.place(relx=0.3, rely=0.4, anchor="center")
        port_text.place(relx=0.5, rely=0.6, anchor="center")
        port_label.place(relx=0.3, rely=0.6, anchor="center")

        # Add a label that says "Not Connected"
        connected_label.config(text="Not Connected", foreground="red")

    connect_button.config(command=lambda: show_error() if ip_text.get() == '' or port_text.get() == '' else connect_client(ip_text.get(), port_text.get()))
    quit_button.config(command=lambda: client_quit(CLIENT_CONNECTION, False))

    list_button.config(command=lambda: client_list_files(CLIENT_CONNECTION, 'LIST'))
    retr_button.config(command=lambda: show_error() if filename_text.get() == '' else client_get_file(CLIENT_CONNECTION, filename_text.get(), 'RETR ' + filename_text.get()))
    send_button.config(command=lambda: show_error() if filename_text.get() == '' else client_put_file(CLIENT_CONNECTION, filename_text.get()))

    # Create the second tab
    tab2 = ttk.Frame(tab_control)
    tab_control.add(tab2, text="NAP Server")

    # Add text box, buttons, and label to tab2
    keyword_text = ttk.Entry(tab2)
    keyword_text.place(relx=0.5, rely=0.3, anchor="center")
    keyword_label = ttk.Label(tab2, text="Keyword")
    keyword_label.place(relx=0.5, rely=0.2, anchor="center")

    search_button = ttk.Button(tab2, text="Search")
    search_button.place(relx=0.5, rely=0.4, anchor="center")

    list_box = tk.Listbox(tab2, width=50)
    list_box.place(relx=0.5, rely=0.6, anchor="center")

    quit_nap_button = ttk.Button(tab2, text="Quit")
    quit_nap_button.place(relx=0.9, rely=0.9, anchor="center")

    connect_nap_button = ttk.Button(tab2, text="Connect")

    def quit_nap():
        keyword_text.place_forget()
        keyword_label.place_forget()
        search_button.place_forget()
        list_box.delete(0, tk.END)
        list_box.place_forget()
        quit_nap_button.place_forget()

        connect_nap_button.place(relx=0.5, rely=0.5, anchor="center")

    def connect_nap():
        connect_nap_button.place_forget()

        keyword_text.place(relx=0.5, rely=0.3, anchor="center")
        keyword_label.place(relx=0.5, rely=0.2, anchor="center")
        search_button.place(relx=0.5, rely=0.4, anchor="center")
        list_box.place(relx=0.5, rely=0.6, anchor="center")
        quit_nap_button.place(relx=0.9, rely=0.9, anchor="center")
        list_box.delete(0, tk.END)

    connect_nap_button.config(command=lambda: nap_connect(NAP_SERVER, NAP_PORT))
    quit_nap_button.config(command=lambda: client_quit(NAP_CONNECTION, True))

    search_button.config(command=lambda: show_error() if keyword_text.get() == '' else search_keyword(NAP_CONNECTION, keyword_text.get()))

    # Pack the tab control and start the GUI
    tab_control.pack(expand=1, fill="both")

    def client_connect_to_server(server_address):
        """Connect to the server at the given address"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(server_address)
        return s

    def client_list_files(s, command):
        """List files in the server's current directory"""
        view_box.delete(0, tk.END)
        s.sendall(b'LIST')
        client_data_connection(s, command)

    def client_get_file(s, filename, command):
        """Get a file from the server"""
        view_box.delete(0, tk.END)
        s.sendall(('RETR ' + filename).encode())
        client_data_connection(s, command)

    def client_put_file(s, filename):
        """Send a file to the server"""
        s.sendall(('STOR ' + filename).encode())
        client_join_data_connection(filename, s)


    def client_quit(s, nap):
        """Terminate the connection to the server"""
        s.sendall(b'QUIT')
        print("Sent QUIT command to server")
        s.close()
        if nap:
            quit_nap()
        else:
            disconnect()

    def client_join_data_connection(filename, connection):
        data = connection.recv(BUFFER_SIZE)
        if not data:
            connection.sendall(b'ERROR')
        data = data.decode()
        ip_address, port = data.split(":")
        server_address = (ip_address, int(port))
        data_connection = client_connect_to_data_connection(server_address)
        root_dir = os.path.join(os.getcwd(), 'root')
        filename = os.path.join(root_dir, filename)
        if not os.path.exists(filename):
            print(f'File {filename} does not exist')
            data_connection.sendall(b'ERROR')
            data_connection.close()
        try:
            with open(filename, 'rb') as f:
                while True:
                    data = f.read(BUFFER_SIZE)
                    if not data:
                        break
                    data_connection.sendall(data)
                data_connection.close()
        except:
            data_connection.sendall(b'ERROR')
            data_connection.close()

    def client_connect_to_data_connection(server_address):
        """Connect to the server at the given address"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(server_address)
        return s

    def client_data_connection(s, command):
        """Create a data connection to the server"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as data_socket:
            PORT = random.randint(8696, 9999)
            s.sendall(f'{HOST}:{PORT}'.encode())
            data_socket.bind((HOST, PORT))
            data_socket.listen()
            print(f'Data connection started at - {HOST}:{PORT}')
            while True:
                connection, addr = data_socket.accept()
                print(f'Data Connection connected to - {addr[0]}:{addr[1]}')
                if command == 'LIST':
                    data = connection.recv(BUFFER_SIZE)
                    print("Received data from server")
                    print(data)
                    if data.decode() == 'ERROR':
                        view_box.insert(tk.END, 'Error when retrieving file from server')
                        break
                    data = data.decode()
                    data = data.split("-:-")
                    for item in data:
                        view_box.insert(tk.END, item)
                elif command.startswith('RETR'):
                    try:
                        if data.decode() == 'ERROR':
                            view_box.insert(tk.END, 'Error when retrieving file from server')
                            break
                    except:
                        print("Image received from server")
                    _, filename = command.split()
                    root_dir = os.path.join(os.getcwd(), 'root')
                    filename = os.path.join(root_dir, filename)
                    with open(filename, 'wb') as f:
                        while True:
                            data = connection.recv(BUFFER_SIZE)
                            if not data:
                                break
                            f.write(data)
                    view_box.insert(tk.END, f'File {filename} received from server')
                data_socket.close()                
                break

    def search_keyword(s, keyword):
        list_box.delete(0, tk.END)
        s.sendall(('KEY ' + keyword).encode())
        print_keyword(s)

    def print_keyword(s):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as data_socket:
            PORT = random.randint(8696, 9999)
            s.sendall(f'{HOST}:{PORT}'.encode())
            data_socket.bind((HOST, PORT))
            data_socket.listen()
            while True:
                connection, addr = data_socket.accept()
                data = connection.recv(BUFFER_SIZE)
                print("Received data from server")
                print(data)
                if data.decode() == 'NO FILE FOUND':
                    list_box.insert(tk.END, 'No files found')
                    break
                else:
                    data = data.decode()
                    data = data.split("-:-")
                    for item in data:
                        list_box.insert(tk.END, item)
                    data_socket.close()
                    break

    nap_connect(NAP_SERVER, NAP_PORT)
    client_put_file(NAP_CONNECTION, "manifest.json")

    root.mainloop()

#################### SERVER CODE ####################
#################### SERVER CODE ####################
#################### SERVER CODE ####################
#################### SERVER CODE ####################

def server_get_files():
    cwd = os.getcwd()
    new_cwd = os.path.join(cwd, 'root')
    files = []
    for filename in os.listdir(new_cwd):
        if filename != 'manifest.json':
            files.append(filename)
    file_str = "-:-".join(files).encode()
    return file_str

def server_create_data_connection(s, filename):
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
            if os.path.exists(filename):
                filename = filename + '_copy'
            with open(filename, 'wb') as f:
                while True:
                    data = connection.recv(BUFFER_SIZE)
                    if not data:
                        break
                    f.write(data)
            print(f'File {filename} received from server')
            data_socket.close()
            break

def server_join_data_connection(command, connection):
    data = connection.recv(BUFFER_SIZE)
    if not data:
        connection.sendall(b'ERROR')
    else:
        data = data.decode()
        ip_address, port = data.split(":")
        server_address = (ip_address, int(port))
        data_connection = server_connect_to_data_connection(server_address)
        if command == b'LIST':
            try:
                data = server_get_files()
                data_connection.sendall(data)
                data_connection.close()
            except:
                data_connection.sendall(b'ERROR')
                data_connection.close()
        elif command.startswith(b'RETR'):
            _, filename = command.split()
            filename = filename.decode()
            root_dir = os.path.join(os.getcwd(), 'root')
            filename = os.path.join(root_dir, filename)
            if not os.path.exists(filename):
                print(f'File {filename} does not exist')
                data_connection.sendall(b'ERROR')
                data_connection.close()
            try:
                with open(filename, 'rb') as f:
                    while True:
                        data = f.read(BUFFER_SIZE)
                        if not data:
                            break
                        data_connection.sendall(data)
                data_connection.close()
            except:
                data_connection.sendall(b'ERROR')
                data_connection.close()
        

def server_connect_to_data_connection(server_address):
    """Connect to the server at the given address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(server_address)
    return s

def server_handle_client(connection, addr, s):
    print(f'Connected to - {addr[0]}:{addr[1]}')
    while True:
        data = connection.recv(BUFFER_SIZE)
        if data == b'LIST':
            server_join_data_connection(data, connection)
            print("Sent all files in CWD to client")
        elif data.startswith(b'RETR'):
            server_join_data_connection(data, connection)
        elif data.startswith(b'STOR'):
            _, filename = data.split()
            server_create_data_connection(connection, filename.decode())
            print(f'File {filename} received from client')
        elif data == b'QUIT':
            print(f'Client {addr[0]}:{addr[1]} disconnected')
            connection.close()
            break
        else:
            s.sendall(b'ERROR')
            print('Invalid command')

def server_main():
    print('Server started')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f'Server started at - {HOST}:{PORT}')
        while True:
            connection, addr = s.accept()
            t = threading.Thread(target=server_handle_client, args=(connection, addr, s))
            t.start()

if __name__ == '__main__':
    t1=threading.Thread(target=server_main)
    t2=threading.Thread(target=run_client)

    t1.start()
    t2.start()
