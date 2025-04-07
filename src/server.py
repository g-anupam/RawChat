import socket
import threading
import os

class ChatServer:
    def __init__(self, host='0.0.0.0', port=12345):  # Changed to 0.0.0.0
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Avoid "Address already in use"
        self.server.bind((host, port))
        self.server.listen()
        self.clients = []
        self.nicknames = []
        self.files = {}  # Store files: {filename: content}
        print(f"Server running on {host}:{port} (listening on all interfaces)")

    def broadcast(self, message, exclude=None):
        for client in self.clients:
            if client != exclude:
                try:
                    client.send(message)
                except:
                    self.remove_client(client)

    def handle_client(self, client):
        while True:
            try:
                message = self.client.recv(1024)
                if message.startswith(b'FILE:'):
                    self.handle_file_transfer(client, message)
                elif message.startswith(b'DOWNLOAD:'):
                    self.handle_file_download(client, message)
                else:
                    self.broadcast(message, client)
            except:
                self.remove_client(client)
                break

    def handle_file_transfer(self, client, message):
        header, file_content = message.split(b':', 1)[1].split(b'|', 1)
        filename = header.decode('utf-8')
        self.files[filename] = file_content
        self.broadcast(f"FILE_AVAILABLE:{filename}".encode('utf-8'))
        print(f"Received file: {filename}")

    def handle_file_download(self, client, message):
        filename = message.split(b':', 1)[1].decode('utf-8')
        if filename in self.files:
            client.send(b'FILE:' + filename.encode('utf-8') + b'|' + self.files[filename])
            print(f"Sent file {filename} to a client")
        else:
            client.send(f"ERROR: File {filename} not found".encode('utf-8'))

    def remove_client(self, client):
        if client in self.clients:
            index = self.clients.index(client)
            self.clients.remove(client)
            nickname = self.nicknames[index]
            self.nicknames.remove(nickname)
            client.close()
            self.broadcast(f'{nickname} left the chat!'.encode('utf-8'))
            print(f'{nickname} disconnected')

    def run(self):
        while True:
            client, address = self.server.accept()
            print(f"Connected with {address}")

            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            self.nicknames.append(nickname)
            self.clients.append(client)

            print(f'Nickname of the client is {nickname}')
            self.broadcast(f'{nickname} joined the chat!'.encode('utf-8'))
            client.send('Connected to the server!'.encode('utf-8'))

            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()

if __name__ == "__main__":
    server = ChatServer()
    server.run()
