import socket
import threading

HOST = 'localhost'
TCP_PORT = 5555
UDP_PORT = 5556

# We'll track the current communication mode.
mode = "TCP"

def tcp_receive(tcp_socket):
    """Listens for messages from the server over TCP."""
    global mode
    while True:
        try:
            msg = tcp_socket.recv(1024).decode().strip()
            if not msg:
                break
            print("TCP:", msg)
            # When the server signals game start, switch to UDP mode.
            if msg.lower() == "game has started":
                mode = "UDP"
                threading.Thread(target=udp_mode, daemon=True).start()
        except Exception as e:
            print("TCP error:", e)
            break

def udp_receive(udp_socket):
    """Continuously listens for UDP messages from the server."""
    while True:
        try:
            data, _ = udp_socket.recvfrom(1024)
            if not data:
                break
            print("UDP:", data.decode())
        except Exception as e:
            print("UDP receive error:", e)
            break

def udp_mode():
    """Handles game communication over UDP until 'quit' is sent."""
    # Create and bind a UDP socket (using an ephemeral port).
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('', 0))
    # Send an initial registration message.
    udp_socket.sendto("register".encode(), (HOST, UDP_PORT))
    
    # Start a thread to receive UDP messages.
    threading.Thread(target=udp_receive, args=(udp_socket,), daemon=True).start()

    print("Switched to UDP mode. Type 'cookie' to increase score or 'quit' to end game and return to TCP.")
    while True:
        msg = input("UDP You: ")
        udp_socket.sendto(msg.encode(), (HOST, UDP_PORT))
        if msg.lower() == "quit":
            break
    udp_socket.close()
    print("Exited UDP mode. Back to TCP lobby.")
    mode = "TCP"

# Create the TCP connection.
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.connect((HOST, TCP_PORT))

# Start a thread to listen for TCP messages.
threading.Thread(target=tcp_receive, args=(tcp_socket,), daemon=True).start()

print("Connected via TCP. Waiting in lobby...")

# Main loop for sending messages via TCP (lobby mode).
while True:
    # Only allow TCP input if we are in TCP mode.
    if mode == "TCP":
        msg = input("TCP You: ")
        tcp_socket.send(msg.encode())
        # Optionally, allow quitting the whole client from TCP mode.
        if msg.lower() == "quit":
            break
    else:
        # In UDP mode, the dedicated thread handles input.
        pass

tcp_socket.close()
print("Disconnected from the server.")
