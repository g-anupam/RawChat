#server
import socket
import threading

class ChatServer:
    def __init__(self,host = '0.0.0.0', port = 12345):
        '''
        Initialises the server.
        '''
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create a TCP socket using IPv4
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Allows the socket to reuse the port in case the serevr restarts
        self.server.bind((host,port))
        self.server.listen()
        self.clients = []
        self.names = []
        self.files = {} # {filename : content}
        print(f"Serevr running on {host}:{port}")

    def broadcast(self,message, exclude = None):
        '''
        Sends a message to all connected clients except excluded ones
        '''
        for client in self.clients:
            if client != exclude:
                try:
                    client.send(message)
                except:
                    self.remove_client(client)

    def handle_client(self,client):
        '''
        Handles communication with a single client. Can process incoming messages and files.
        '''
        while True:
            try:
                message = client.recv(1024) #Maximum 1024 bytes can be received from the client.
                if not message:
                    self.remove_client(client)
                    break
                elif message.startswith(b'FILE:'):
                    self.handle_upload(client, message)
                elif message.startswith(b'DOWNLOAD:'):
                    self.handle_download(client,message)
                else:
                    self.broadcast(message,exclude = client) #TODO: Try and remove the exclude and see if the UI gets better!



