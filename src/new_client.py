import socket
import threading
import os
import time

class ChatClient:
    def __init__(self, host, port, nickname):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.nickname = nickname
        self.running = True
        self.buffer_size = 500
        self.receive_thread = None  # Store the receive thread

    def receive(self):
        while self.running:
            try:
                message = self.client.recv(1024)
                if not message:
                    break
                if message == b'NAME':  # Updated to match server
                    self.client.send(self.nickname.encode('utf-8'))
                elif message.startswith(b'FILE:'):
                    try:
                        header, file_content = message.split(b':', 1)[1].split(b'|', 1)
                        filename = header.decode('utf-8')
                        with open(f"downloaded_{filename}", 'wb') as f:
                            f.write(file_content)
                        print(f"\nDownloaded file saved as: downloaded_{filename}")
                    except Exception as e:
                        print(f"\nFile download error: {e}")
                else:
                    print(f"\n{message.decode('utf-8')}")
            except Exception as e:
                if self.running:  # Only print error if client is still running
                    print(f"\nConnection error: {e}")
                break

    def write(self):
        print("\nWelcome to the chat!")
        print("Commands: 'upload <filename>', 'download <filename>', 'exit'\n")
        while self.running:
            try:
                message = input("> ")
                if message.lower() == 'exit':
                    self.running = False
                    time.sleep(0.1)  # Brief delay to allow receive thread to exit
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
                        print(f"Message too long! Max {self.buffer_size} characters.")
            except Exception as e:
                print(f"Write error: {e}")
                break

    def run(self):
        self.receive_thread = threading.Thread(target=self.receive, daemon=True)
        self.receive_thread.start()
        self.write()

if __name__ == "__main__":
    server_ip = input("Enter server IP: ")
    nickname = input("Choose a nickname: ")
    client = ChatClient(server_ip, 12345, nickname)
    client.run()
