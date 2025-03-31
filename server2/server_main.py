# server.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import socket
import threading
import time
import json

from game_code.config import HOST, UDP_PORT  # e.g., HOST = "0.0.0.0", UDP_PORT = 5555
from networking import create_udp_socket, broadcast_udp, receive_messages
from GameStateManager import GameStateManager

# -------------------------------------------------------------
# This is the main entry point for the server.
# It initializes the UDP socket, creates the game state manager,
# starts the receiver thread to process incoming messages, and then
# continuously broadcasts the current game state to all connected clients.
# -------------------------------------------------------------

def main():
    # Create a UDP socket and bind it
    udp_socket = create_udp_socket(HOST, UDP_PORT)
    
    # Initialize the game state manager (holds players, cookies, etc.)
    game_manager = GameStateManager()
    
    # Start the receiver thread: it listens for incoming UDP messages and updates game state
    receiver_thread = threading.Thread(target=receive_messages, args=(udp_socket, game_manager), daemon=True)
    receiver_thread.start()
    
    game_manager
    
    # Main loop: broadcast the current game state at a fixed interval (e.g., 60 FPS)
    try:
        while True:
            # Get the current state as a dictionary
            data = game_manager.get_game_data()
            message = json.dumps(data)
            # Broadcast state to all connected clients
            broadcast_udp(udp_socket, message, game_manager.get_all_client_addresses())
            time.sleep(1/60)
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        udp_socket.close()

if __name__ == "__main__":
    main()