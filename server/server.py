import socket
import threading

MAX_PLAYERS = 4
numOfPlayers = 1  # Server is Player 1
player_numbers = {}  # Maps client sockets to player numbers

HOST = 'localhost'
PORT = 5555  # Any available port

def handle_client(conn, addr):
    """Handles communication with a single client."""
    global numOfPlayers

    # Assign a player number and announce the new player
    numOfPlayers += 1
    player_numbers[conn] = numOfPlayers
    print(f"Player {numOfPlayers} has joined! Total players: {numOfPlayers}")

    try:
        while True:
            msg = conn.recv(1024).decode().strip()
            if not msg or msg.lower() == 'quit':
                break
            print(f"Player {player_numbers[conn]}: {msg}")
            conn.send(f"Player {player_numbers[conn]} said: {msg}".encode())
    except ConnectionResetError:
        pass  # Handle abrupt disconnection

    # Remove player from the game
    print(f"Player {player_numbers[conn]} disconnected! Total players: {numOfPlayers - 1}")
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
