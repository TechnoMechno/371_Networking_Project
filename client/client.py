import socket
import threading

HOST = 'localhost'
PORT = 5555

def receive_messages(client_socket):
    """Continuously listens for messages from the server."""
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break
            print(f"\n[Server]: {msg}")
        except:
            break

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Start a thread to receive messages
recv_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
recv_thread.start()

print("Connected to the server. Type 'quit' to disconnect.")

# Main loop for sending messages
while True:
    msg = input("You: ")
    client_socket.send(msg.encode())
    if msg.lower() == 'quit':
        break

client_socket.close()
print("Disconnected from the server.")
