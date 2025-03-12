import socket
import threading

def handle_client(client_socket, addr):
    print(f"Connected to {addr}")
    try:
        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            print(f"Received from {addr}: {message.decode()}")
    finally:
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = '127.0.0.1'
    port = 12345
    server_socket.bind((host, port))

    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == '__main__':
    start_server()
