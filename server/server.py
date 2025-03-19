import socket
import threading
from game_state import GameState

MAX_PLAYERS = 4
numOfPlayers = 1
connections = []  
game_state = GameState.WAITING

HOST = 'localhost'
PORT = 5555 

def broadcast(message):
    """Send a message to all players."""
    for conn in connections:
        try:
            conn.send(message.encode())
        except:
            connections.remove(conn)

def handle_client(conn, addr):
    """Handles player connections."""
    global numOfPlayers
    numOfPlayers += 1
    connections.append(conn)

    print(f"Player {numOfPlayers} joined! Waiting for game to start.")
    broadcast(f"Player {numOfPlayers} has joined!")

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

def server():
    global game_state
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(MAX_PLAYERS)
    
    print("Server is running. Waiting for players...")

    threading.Thread(target=accept_clients, args=(server_socket,), daemon=True).start()

    while True:
        if (game_state == game_state.WAITING):
            command = input("Type 'start' to begin the game: \n").strip().lower()
            if command == "start":
                if numOfPlayers == 1:
                    print("Minimum amount of players is 2!")
                else:
                    print("Game has started")  
                    broadcast("Game has started")  
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
