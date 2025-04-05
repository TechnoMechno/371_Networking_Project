import socket
import json
from game_code.config import GameState

# -------------------------------------------------------------
# This module provides helper functions for UDP networking.
# It handles creating and binding UDP sockets, broadcasting messages to
# a list of client addresses, and continuously receiving messages on the UDP
# socket, delegating processing to the game state manager.
# -------------------------------------------------------------

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
    Continuously receives messages on the UDP socket.
    For handshake requests (JOIN_CHECK), if a client is new and the game is not in the LOBBY state,
    send a JSON response indicating that the game is in session.
    Otherwise, reply with a plain 'PONG'.
    All other messages are passed to the game manager.
    """
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            message = data.decode().strip()
            if message == "JOIN_CHECK":
                with game_manager.lock:
                    # If client is new and game is not in LOBBY, send game_in_session response.
                    if addr not in game_manager.client_addresses and game_manager.game_state != GameState.LOBBY:
                        response = json.dumps({
                            "type": "game_in_session",
                            "message": "Game is already in session. Cannot join."
                        })
                        sock.sendto(response.encode(), addr)
                    else:
                        sock.sendto("PONG".encode(), addr)
                continue  # Do not process further
            # Otherwise, delegate the message to the game manager.
            game_manager.handle_message(message, addr, sock)
        except socket.timeout:
            continue
        except Exception as e:
            print("Receive error:", e)
