import socket
import threading
import os

class ChatClient:
    def __init__(self, host, port, nickname):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.nickname = nickname
        self.running = True
        self.buffer_size = 500  # Maximum message length

    def receive(self):
        while self.running:
            try:
                message = self.client.recv(1024)
                decoded_message = message.decode('utf-8')
                if decoded_message == 'NICK':
                    self.client.send(self.nickname.encode('utf-8'))
                elif decoded_message.startswith('FILE_AVAILABLE:'):
                    filename = decoded_message.split(':', 1)[1]
                    print(f"New file available: {filename} (type 'download {filename}' to get it)")
                elif message.startswith(b'FILE:'):
                    header, file_content = message.split(b':', 1)[1].split(b'|', 1)
                    filename = header.decode('utf-8')
                    with open(f"downloaded_{filename}", 'wb') as f:
                        f.write(file_content)
                    print(f"Downloaded file saved as: downloaded_{filename}")
                elif decoded_message.startswith('ERROR:'):
                    print(decoded_message)
                else:
                    print(decoded_message)
            except:
                print("An error occurred!")
                self.client.close()
                self.running = False
                break

    def write(self):
        print("Commands: 'upload <filename>' to send a file, 'download <filename>' to get a file, 'exit' to quit")
        while self.running:
            message = input('> ')
            if message.lower() == 'exit':
                self.running = False
                self.client.close()
                break
            elif message.startswith('upload '):
                filename = message.split(' ', 1)[1]
                if os.path.exists(filename):
                    with open(filename, 'rb') as f:
                        content = f.read()
                    self.client.send(f"FILE:{filename}|".encode('utf-8') + content)
                    print(f"Sent file: {filename}")
                else:
                    print("File not found!")
            elif message.startswith('download '):
                filename = message.split(' ', 1)[1]
                self.client.send(f"DOWNLOAD:{filename}".encode('utf-8'))
            else:
                if len(message) <= self.buffer_size:
                    self.client.send(f'{self.nickname}: {message}'.encode('utf-8'))
                else:
                    print(f"Message too long! Max length is {self.buffer_size} characters.")

    def run(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
        self.write()

if __name__ == "__main__":
    server_ip = input("Enter server IP: ")
    nickname = input("Choose a nickname: ")
    client = ChatClient(server_ip, 12345, nickname)
    client.run()
