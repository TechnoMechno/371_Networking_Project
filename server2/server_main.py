# server_main.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import socket
import threading
import time
import json

from game_code.config import HOST, UDP_PORT  # e.g., HOST = "127.0.0.1", UDP_PORT = 55555
from server2.networking import create_udp_socket, broadcast_udp
from server2.GameStateManager import GameStateManager

server_running = True

def receive_and_handle_messages(udp_socket, game_manager):
    """
    Continuously receives UDP messages.
    If a message is "JOIN_CHECK", it replies with "PONG" if the game is in LOBBY;
    otherwise, it sends a JSON error if the game is already in session.
    Other messages are passed to game_manager.handle_message.
    """
    global server_running 
    while server_running:
        try:
            data, addr = udp_socket.recvfrom(4096)
            message = data.decode().strip()
            if message == "JOIN_CHECK":
                with game_manager.lock:
                    # If the client is new and the game is not in LOBBY, reject the join.
                    if addr not in game_manager.client_addresses and game_manager.game_state != GameStateManager.LOBBY:
                        response = json.dumps({
                            "type": "game_in_session",
                            "message": "Game is already in session. Cannot join."
                        })
                        udp_socket.sendto(response.encode(), addr)
                    else:
                        udp_socket.sendto("PONG".encode(), addr)
                continue  # Skip normal message processing.
            else:
                try:
                    msg_obj = json.loads(message)
                    if msg_obj.get("type") == "shutdown":
                        print("Shutdown signal received from host.")
                        for addr in game_manager.client_addresses:
                            response = json.dumps({
                                "type": "shutdown",
                                "message": "shutdown"
                            })
                            udp_socket.sendto(response.encode(), addr)
                        # global server_running
                        server_running = False
                        break
                except json.JSONDecodeError:
                    pass

                game_manager.handle_message(message, addr, udp_socket)
        except socket.timeout:
            continue
        except Exception as e:
            print("Receive error:", e)

def main():
    global server_running
    server_running = True
    # Create the UDP socket and bind it.
    udp_socket = create_udp_socket(HOST, UDP_PORT)
    
    # Initialize the game state manager.
    game_manager = GameStateManager()
    
    # Start the receiver thread with handshake handling.
    receiver_thread = threading.Thread(target=receive_and_handle_messages, args=(udp_socket, game_manager), daemon=True)
    receiver_thread.start()
    
    # Main loop: update state and broadcast game state to all connected clients.
    try:
        while server_running:
            game_manager.update_state_transitions()
            data = game_manager.get_game_data()
            message = json.dumps(data)
            game_manager.update_dragged_cookies()
            broadcast_udp(udp_socket, message, game_manager.get_all_client_addresses())
            time.sleep(1/60)
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        print("Closing server socket.")
        udp_socket.close()

if __name__ == "__main__":
    main()
