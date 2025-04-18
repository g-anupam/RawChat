#client 
import socket
import threading
import os

class ChatClient:
    def __init__(self, host, port, name):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host,port))
        self.name = name
        self.running = True
        self.buffer_size = 500

    def receive(self):
        while self.running:
            try:
                message = self.client.recv(1024)
                if not message:
                    break
                elif message.startswith(b'FILE:'):
                    try:
                        header, file_content = message.split(b':', 1)[1].split(b'|', 1)
                        filename = header.decode('utf-8')
                        with open(f"downloaded_{filename}","wb") as f:
                            f.write(file_content)
                        f.close()
                        print(f"\nFile saved as downloaded_file{filename}")
                    except Exception as e:
                        print(f"\nFile download error -> {e}")
                else:
                    print(f"\n{message.decode('utf-8')}")
            except Exception as e:
                print(f"\nConnection error -> {e}")
                self.running = False
                break

    def write(self):
        print("\nWlecome to the chat!")
        print("Commands: 'uplaod <filename>', 'download <filename>', 'exit'\n")
        while self.running:
            try:
                message = input("> ")
                if message.lower() == "exit":
                    self.running = False
                    self.client.close()
                    break
                elif message.startswith('upload'):
                    filename = message.split(' ',1)[1]
                    if os.path.exists(filename):
                        with open(filename, 'rb') as f:
                            content = f.read()
                        f.close()
                        self.client.send(f"FILE:{filename}|".encode('utf-8')+content)
                        print(f"Sent file:{filename}")
                    else:
                        print("File not found!")
                elif message.startswith('download'):
                    filename = message.split(' ',1)[1]
                    self.client.send(f"DOWNLAOD:{filename}".encode('utf-8'))
                else:
                    if len(message) <= self.buffer_size:
                        self.client.send(f'{self.name}:{message}'.encode('utf-8'))
                    else:
                        print(f"Message too long! Max size is {self.buffer_size} characters")
            except Exception as e:
                print(f"Write error -> {e}")
                break

    def run(self):
        threading.Thread(target = self. receive, daemon = True).start()
        self.write()

if __name__ == "__main__":
    server_ip = input("Enter server IP: ")
    name = input("Choose a nickname : ")
    client = ChatClient(server_ip,12345, name)
    client.run()

