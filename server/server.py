import socket
import threading
from game_state import GameState

MAX_PLAYERS = 4
numOfPlayers = 1  # Server is Player 1
player_numbers = {}  # Maps client sockets to player numbers
connections = []  # List of active client sockets
game_state = GameState.WAITING

HOST = 'localhost'
PORT = 5555 

def broadcast(message, sender_conn=None):
    """Sends a message to all clients except the sender (if specified)."""
    for conn in connections:
        try:
            conn.send(message.encode())
        except:
            connections.remove(conn)  

def check_game_start():
    """ Check if the game should start """
    global game_state 
    if numOfPlayers == MAX_PLAYERS and game_state == GameState.WAITING:
        game_state = GameState.IN_PROGRESS
        broadcast("The game has started!")


def handle_client(conn, addr):
    """Handles communication with a single client."""
    global numOfPlayers

    numOfPlayers += 1
    player_numbers[conn] = numOfPlayers
    connections.append(conn)  # Store the connection
    print(f"Player {numOfPlayers} has joined! Total players: {numOfPlayers}")

    broadcast(f"Player {numOfPlayers} has joined the game!")

    try:
        while True:
            msg = conn.recv(1024).decode().strip()
            if not msg or msg.lower() == 'quit':
                break
            print(f"Player {player_numbers[conn]}: {msg}")
            broadcast(f"Player {player_numbers[conn]}: {msg}", sender_conn=conn)
    except ConnectionResetError:
        pass  # Handle abrupt disconnection

    # Remove player from the game
    print(f"Player {player_numbers[conn]} disconnected! Total players: {numOfPlayers - 1}")
    broadcast(f"Player {player_numbers[conn]} has left the game!")

    connections.remove(conn)
    del player_numbers[conn]
    numOfPlayers -= 1
    conn.close()

def server():
    """TCP Server for handling multiple clients."""
    global numOfPlayers
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(MAX_PLAYERS)
    
    print("Welcome, you are Player 1!")

    while True:
        conn, addr = server_socket.accept()
        if numOfPlayers < MAX_PLAYERS:
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
        else:
            conn.send("Server full! Try again later.".encode())
            conn.close()

if __name__ == '__main__':
    server()
