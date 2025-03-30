import socket
import json

def create_udp_socket(host, port):
    """Creates a UDP socket, binds it to (host, port), and returns it."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    sock.settimeout(1.0)  # Set timeout for periodic checks (optional)
    return sock

def broadcast_udp(sock, message, client_addresses):
    """Broadcasts a message (string) to a list of client addresses."""
    for addr in client_addresses:
        try:
            sock.sendto(message.encode(), addr)
        except Exception as e:
            print(f"Error broadcasting to {addr}: {e}")

def receive_messages(sock, game_manager):
    """
    Continuously receives messages on the UDP socket and delegates processing
    to the game_manager.
    """
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            message = data.decode()
            # Delegate message handling to game_manager
            game_manager.handle_message(message, addr, sock)
        except socket.timeout:
            continue
        except Exception as e:
            print("Receive error:", e)