# network_manager.py
import socket
import threading

class NetworkManager:
    def __init__(self, parent):
        self.parent = parent
        self.server_socket = None
        self.client_socket = None
        self.server_thread = None
        self.client_thread = None

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('', 8000)
        self.server_socket.bind(server_address)
        self.server_socket.listen(1)

        self.server_thread = threading.Thread(target=self.server_loop)
        self.server_thread.start()

    def server_loop(self):
        print('Waiting for a connection...')
        self.client_socket, client_address = self.server_socket.accept()

        print(f'Connection from {client_address}')

        self.receive_data()

    def connect_to_server(self, server_ip):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (server_ip, 8000)
        self.client_socket.connect(server_address)

        self.client_thread = threading.Thread(target=self.receive_data)
        self.client_thread.start()

    def send_data(self, data):
        if self.client_socket:
            self.client_socket.sendall(data.encode())
        elif self.server_socket:
            self.client_socket.sendall(data.encode())

    def send_label(self, index, label, color):
        data = f"update_label:{index}:{label}:{color}"
        self.send_data(data)

    def send_number_box(self, index, x, y, color):
        data = f"update_number_box:{index}:{x}:{y}:{color}"
        self.send_data(data)

    def receive_data(self):
        while True:
            if self.client_socket:
                data = self.client_socket.recv(1024).decode()
            elif self.server_socket:
                data = self.client_socket.recv(1024).decode()

            if not data:
                break

            parts = data.split(':')
            command = parts[0]

            if command == "update_number_box":
                index, x, y, color = int(parts[1]), int(parts[2]), int(parts[3]), parts[4]
                self.parent.update_number_box(index, x, y, color)

            elif command == "update_label":
                index, label, color = int(parts[1]), ':'.join(parts[2:-1]), parts[-1]
                self.parent.update_label(index, label, color)

            elif command == "drawing":
                drawing_type, x1, y1, x2, y2, color = parts[1], int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5]), parts[6]
                self.parent.update_drawing(drawing_type, x1, y1, x2, y2, color)

        if self.client_socket:
            self.client_socket.close()
        elif self.server_socket:
            self.server_socket.close()
