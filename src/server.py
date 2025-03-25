import socket
import threading

HOST = '0.0.0.0' 
PORT = 12345
clients = []

def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected")
    clients.append(client_socket)
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"[{addr}] {message}")
            for client in clients:
                if client != client_socket:
                    client.send(f"{addr} : {message}".encode('utf-8'))
    except ConnectionResetError:
        print(f"[DISCONNECTED] {addr} left the chat")
    finally:
        clients.remove(client_socket)
        client_socket.close()

def start_server():
    """Starts the chat server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
