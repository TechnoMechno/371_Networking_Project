import socket
import threading
from shared import GameState, clients, game_state  # Assumes GameState has WAITING and IN_PROGRESS

MAX_PLAYERS = 4
HOST = 'localhost'
TCP_PORT = 5555    
UDP_PORT = 5556

# --- Global Variables
numOfPlayers = 1
connections = []        # List of TCP connections
udp_connections = {}    # Dictionary to store client UDP addresses
score = 0               # Global score


def broadcast_tcp(message):
    """Send a message to all players via TCP."""
    for conn in connections:
        try:
            conn.send(message.encode())
        except:
            connections.remove(conn)

def broadcast_udp(message):
    """Send a message to all players via UDP."""
    for addr in udp_connections.values():
        try:
            udp_socket.sendto(message.encode(), addr)
        except:
            pass

def handle_client(conn, addr):
    """Handles player connections in the TCP lobby."""
    global numOfPlayers
    player_id = f"player{numOfPlayers}"
    numOfPlayers += 1
    connections.append(conn)
    
    join_msg = f"{player_id} has joined the lobby."
    print(join_msg)
    broadcast_tcp(join_msg)

    try:
        while True:
            msg = conn.recv(1024).decode().strip()
            # If recv returns an empty string, the client has disconnected.
            if not msg or msg.lower() == 'quit':
                break
    except ConnectionResetError:
        # This exception occurs if the client disconnects unexpectedly.
        pass
    finally:
        numOfPlayers -= 1
        connections.remove(conn)
        conn.close()
        
        disconnect_msg = f"{player_id} has disconnected."
        print(disconnect_msg)
        broadcast_tcp(disconnect_msg)


def udp_server():
    """Handles UDP communication during game mode."""
    global udp_socket, game_state, score
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))

    while True:
        data, addr = udp_socket.recvfrom(1024)
        msg = data.decode().strip().lower()

        # If any UDP client sends 'quit', end game mode.
        if msg == "quit":
            print("Received UDP 'quit' – ending game, back to TCP lobby.")
            broadcast_tcp("Game ended. Back to lobby.")
            game_state = GameState.WAITING
            continue

        # If a "cookie" is received, update score and broadcast.
        elif msg == "cookie":
            score += 1
            print("Cookie collected! New score:", score)
            broadcast_udp(f"Score: {score}")
            continue

        # Register new UDP addresses if not already registered.
        if addr not in udp_connections.values():
            player_id = f"player{len(udp_connections) + 1}"
            udp_connections[player_id] = addr
            print(f"Added {player_id} with address {addr} to UDP connections.")

        # Relay any other UDP message normally.
        broadcast_udp(data.decode())

def accept_clients(server_socket):
    """Accepts TCP client connections; disconnects new clients if maximum reached."""
    while True:
        conn, addr = server_socket.accept()
        if numOfPlayers < MAX_PLAYERS:
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        else:
            print(f"Too many players connected! Disconnecting client {addr}")
            try:
                conn.send("Server is full. Please try again later.".encode())
            except Exception as e:
                print(f"Error sending full-server message: {e}")
            conn.close()

def server():
    global game_state, numOfPlayers, score
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, TCP_PORT))
    server_socket.listen(MAX_PLAYERS)
    
    print("Server is running. Waiting for players...")

    # Start the UDP thread.
    threading.Thread(target=udp_server, daemon=True).start()
    # Start accepting TCP clients.
    threading.Thread(target=accept_clients, args=(server_socket,), daemon=True).start()

    # Main loop: lobby (TCP) and game mode (UDP) control.
    while True:
        if game_state == GameState.WAITING:
            command = input("Type 'start' to begin the game: \n").strip().lower()
            if command == "start":
                if numOfPlayers < 2:
                    print("Minimum amount of players is 2!")
                else:
                    print("Game has started")
                    broadcast_tcp("Game has started")
                    game_state = GameState.IN_PROGRESS
        elif game_state == GameState.IN_PROGRESS:
            command = input("Game in progress. Type 'cookie' to increase score or 'quit' to end the game: \n").strip().lower()
            if command == "quit":
                print("Ending game, back to TCP lobby.")
                broadcast_udp("quit")  # Notify clients via UDP.
                broadcast_tcp("Game ended. Back to lobby.")
                game_state = GameState.WAITING
            elif command == "cookie":
                score += 1
                print("Cookie collected from server! New score:", score)
                broadcast_udp(f"Score: {score}")

if __name__ == '__main__':
    server()
