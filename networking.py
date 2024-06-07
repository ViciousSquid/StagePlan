import socket
import threading

class NetworkManager:
    def __init__(self, app):
        self.app = app
        self.host = ''
        self.port = 55555
        self.socket = None
        self.server_thread = None
        self.client_thread = None

    def start_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.server_thread = threading.Thread(target=self.accept_clients)
        self.server_thread.start()

    def accept_clients(self):
        while True:
            client_socket, address = self.socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        # Send the current state of the number boxes to the client
        for num_box in self.app.numbers:
            data = f"create_number_box:{num_box.cget('text')}:{num_box.winfo_x()}:{num_box.winfo_y()}"
            client_socket.send(data.encode('utf-8'))
            data = f"update_label:{self.app.numbers.index(num_box)}:{num_box.description.cget('text')}"
            client_socket.send(data.encode('utf-8'))

        # Send the initial window size to the client
        data = f"window_size:{self.app.winfo_width()}:{self.app.winfo_height()}"
        client_socket.send(data.encode('utf-8'))

        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                self.handle_data(data)
            except ConnectionResetError:
                break
        client_socket.close()

    def connect_to_server(self, server_ip):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server_ip, self.port))
        self.client_thread = threading.Thread(target=self.receive_data)
        self.client_thread.start()

    def receive_data(self):
        while True:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                self.handle_data(data)
            except ConnectionResetError:
                break
        self.socket.close()

    def send_data(self, data):
        if self.socket:
            self.socket.send(data.encode('utf-8'))

    def handle_data(self, data):
        parts = data.split(':')
        if parts[0] == 'create_number_box':
            number = parts[1]
            x = int(parts[2])
            y = int(parts[3])
            self.app.create_new_number_box(number=number, position=(x, y))
        elif parts[0] == 'update_number_box':
            index = int(parts[1])
            x = int(parts[2])
            y = int(parts[3])
            self.app.update_number_box_position(index, x, y)
        elif parts[0] == 'window_size':
            width = int(parts[1])
            height = int(parts[2])
            self.app.update_window_size(width, height)
        elif parts[0] == 'update_label':
            index = int(parts[1])
            label = parts[2]
            self.app.update_label(index, label)

    def send_window_size(self, width, height):
        data = f"window_size:{width}:{height}"
        self.send_data(data)

    def send_label(self, index, label):
        data = f"update_label:{index}:{label}"
        self.send_data(data)