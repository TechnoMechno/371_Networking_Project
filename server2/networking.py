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

def receive_messages(sock, game_manager):
    """
    Continuously receives messages on the UDP socket.
    For "JOIN_CHECK" messages, responds with "PONG" (or a JSON error if not allowed).
    Other messages are passed to game_manager.handle_message.
    """
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            message = data.decode().strip()
            if message == "JOIN_CHECK":
                with game_manager.lock:
                    if addr not in game_manager.client_addresses and game_manager.game_state != GameState.LOBBY:
                        response = json.dumps({
                            "type": "game_in_session",
                            "message": "Game is already in session. Cannot join."
                        })
                        sock.sendto(response.encode(), addr)
                    else:
                        sock.sendto("PONG".encode(), addr)
                continue
            game_manager.handle_message(message, addr, sock)
        except socket.timeout:
            continue
        except Exception as e:
            print("Receive error:", e)
