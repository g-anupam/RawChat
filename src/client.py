import socket
import threading

SERVER_IP = "127.0.0.1"  # Change this to the actual server IP
SERVER_PORT = 12345

def receive_messages(client_socket):
    """Continuously receives messages from the server."""
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(message)
        except ConnectionResetError:
            print("[Disconnected from server]")
            break

def start_client():
    """Connects to the chat server and starts messaging."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))

    print("Connected to the server. Type messages below:")

    # Start a thread to listen for incoming messages
    thread = threading.Thread(target=receive_messages, args=(client,))
    thread.start()

    try:
        while True:
            message = input()
            if message.lower() == 'exit':
                break
            client.send(message.encode('utf-8'))
    except KeyboardInterrupt:
        print("\n[Disconnected]")
    
    finally:
        client.close()

if __name__ == "__main__":
    start_client()
