import socket
import json
from game_code.config import GameState

def create_udp_socket(host, port):
    """Creates and binds a UDP socket to (host, port) with a timeout."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass
    sock.bind((host, port))
    sock.settimeout(1.0)
    return sock

def broadcast_udp(sock, message, client_addresses):
    """Broadcasts the message (string) to each address in client_addresses."""
    for addr in client_addresses:
        try:
            sock.sendto(message.encode(), addr)
        except Exception as e:
            print(f"Error broadcasting to {addr}: {e}")


