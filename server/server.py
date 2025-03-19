import socket
import threading
from shared import GameState, clients, game_state

MAX_PLAYERS = 4
numOfPlayers = 1
connections = []        # List of TCP connections
udp_connections = {}    # Dictionary to store client UDP addresses - map each client to UDP address

HOST = 'localhost'
TCP_PORT = 5555    
UDP_PORT = 5556

def broadcast_tcp(message):
    """Send a message to all players via TCP"""
    for conn in connections:
        try:
            conn.send(message.encode())
        except:
            connections.remove(conn)

def broadcast_udp(message):
    """ Send a message to all players via UDP """
    for addr in udp_connections.values():
        try:
            udp_socket.sendto(message.encode(), addr)
        except:
            pass

def handle_client(conn, addr):
    """Handles player connections."""
    global numOfPlayers
    player_id = f"player{numOfPlayers}"
    numOfPlayers += 1
    connections.append(conn)

    print(f"Player {numOfPlayers} joined! Waiting for game to start.")
    broadcast_tcp(f"Player {numOfPlayers} has joined!")

    try:
        while True:
            msg = conn.recv(1024).decode().strip()
            if not msg or msg.lower() == 'quit':
                break
    except ConnectionResetError:
        pass

    numOfPlayers -= 1
    connections.remove(conn)
    conn.close()

def udp_server():
    """ Handles UDP communication for real-time gameplay """
    global udp_socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))

    while True:
        data, addr = udp_socket.recvfrom(1024)

        if addr not in udp_connections.values():
            player_id = f"player{len(udp_connections) + 1}"
            udp_connections[player_id] = addr
            print(f"Added {player_id} with address {addr} to UDP connections.")


        broadcast_udp(data.decode())
    

def server():
    global game_state
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, TCP_PORT))
    server_socket.listen(MAX_PLAYERS)
    
    print("Server is running. Waiting for players...")

    threading.Thread(target=udp_server, daemon=True).start()

    threading.Thread(target=accept_clients, args=(server_socket,), daemon=True).start()

    while True:
        if (game_state == game_state.WAITING):
            command = input("Type 'start' to begin the game: \n").strip().lower()
            if command == "start":
                if numOfPlayers == 1:
                    print("Minimum amount of players is 2!")
                else:
                    print("Game has started")  
                    broadcast_tcp("Game has started")  
                    game_state = GameState.IN_PROGRESS

        # TODO: handle other game_states
            

def accept_clients(server_socket):
    """Accept multiple client connections and disconnect new clients if maximum reached."""
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

if __name__ == '__main__':
    server()