import socket
import threading

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT = 3001
server_address = ("localhost", PORT)
server_socket.bind(server_address)
server_socket.listen(5)
print('Server is listening on', server_address)

client_data = {}  # Dictionary to store client data
data_lock = threading.Lock()  # Lock for synchronizing access to client_data

def handle_client(client_socket, client_address):
    global client_data
    try:
        # Receive data from the client
        player_name = client_socket.recv(1024).decode()
        print('Connected to', client_address, 'Received:', player_name)

        # Store client data with thread-safe access
        with data_lock:
            client_data[client_address] = player_name

        # Additional server-client interaction can be added here

    except ConnectionResetError:
        pass
    finally:
        client_socket.close()
        with data_lock:
            if client_address in client_data:
                del client_data[client_address]
        print('Connection closed with', client_address)

def server_main():
    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    server_main()