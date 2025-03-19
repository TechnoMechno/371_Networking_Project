import socket
import threading

HOST = 'localhost'
PORT = 5555

def receive_messages(tcp_socket):
    """Continuously listens for messages from the server."""
    while True:
        try:
            msg = tcp_socket.recv(1024).decode()
            if not msg:
                break
            print(msg);
        except:
            break

# Connect to the tcp server
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.connect((HOST, PORT))

# Start a thread to receive messages
recv_thread = threading.Thread(target=receive_messages, args=(tcp_socket,), daemon=True)
recv_thread.start()

print("Connected to the server. Type 'quit' to disconnect.")

# Main loop for sending messages
while True:
    msg = input("You: ")
    tcp_socket.send(msg.encode())
    if msg.lower() == 'quit':
        break

tcp_socket.close()
print("Disconnected from the server.")