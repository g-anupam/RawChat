#server
import socket
import threading

def getIpAddress():
    '''
    This is a function not related to the server class. All it does is obtain the ip address of the server.
    '''
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8',80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

class ChatServer:
    def __init__(self,host = getIpAddress(), port = 12345):
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
            except:
                self.remove_client(client)
                break

    def handle_upload(self,client, message):
        '''
        Takes a message in the form of a file, stores it in the files list, and bradcasts the availability
        of this file to all the clients so that any user in the chat room can downlaod it. 
        Normal print statements here log to the server, and braodcast is a message received by each client 
        which is sent through client.send method
        '''
        try:
            header, file_content = message.split(b':',1)[1].split(b'|',1)
            filename = header.decode('utf-8')
            self.files[filename] = file_content #Adding the file to the files list
            self.broadcast(f"New File Avialable to upload -> {filename}".encode('utf-8'))
            print(f"Received file : {filename}") #This prints to the server logs
        except Exception as e:
            print(f"File Transfer error: {e}") #Logs the error in the server console

    def handle_download(self,client, message):
        filename = message.split(b':', 1)[1].decode('utf-8')
        if filename in self.files:
            try:
                client.send(b'FILE:' + filename.encode('utf-8') + b'|' + self.files[filename])
                print(f"File {filename} sent to {self.names[client]}") #TODO: If there is an error in this line then remove client name.
            except:
                print(f"Failed to send file -> {filename}")
        else:
            client.send(f"ERROR: File {filename} not found!".encode('utf-8'))

    def remove_client(self, client):
        if client in self.clients:
            index = self.clients.index(client)
            name = self.names[index]
            self.clients.remove(client)
            self.names.remove(name)
            client.close()
            self.broadcast(f'{name} left the chat!'.encode('utf-8'))
            print(f"{name} disconnected from the server")

    def run(self):
        while True:
            client, address = self.server.accept()
            # client.send('NAME'.encode('utf-8'))
            name = client.recv(1024).decode('utf-8')
            self.names.append(name)
            self.clients.append(client)
            print(f"{name} connected with the server through IP Address and port : {address}")
            self.broadcast(f"{name} joined the chat!\n".encode('utf-8'))
            client.send('Connected to the server!'.encode('utf-8')) #TODO: Observe this line too!
            thread = threading.Thread(target = self.handle_client, args = (client,))
            thread.start()

if __name__ == "__main__":
    server = ChatServer()
    server.run()


