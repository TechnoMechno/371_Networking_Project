import socket
import threading

MAX_PLAYERS = 4
numOfPlayers = 1  # server is Player 1
clients = []      # list to store connected client sockets

def handle_client(client_socket, player_number):
    """
    Listens for messages from the client and prints them.
    """
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                print(f"Player {player_number} disconnected.")
                break
            print(f"Player {player_number}: {message}")
        except Exception as e:
            print(f"Error receiving data from Player {player_number}:", e)
            break
    client_socket.close()

def main():
    global numOfPlayers
    host = "localhost"
    port = 5555

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(MAX_PLAYERS)
    print("Server is running as Player 1. Waiting for connections...")

    def accept_connections():
        global numOfPlayers
        while True:
            client_socket, addr = server_socket.accept()
            # Check if maximum players have been reached.
            if numOfPlayers >= MAX_PLAYERS:
                client_socket.send("Game is full!".encode("utf-8"))
                client_socket.close()
                continue

            numOfPlayers += 1
            player_number = numOfPlayers
            print(f"Player {player_number} connected from {addr}")

            # lets the joining users which player they are
            client_socket.send(f"You are Player {player_number}!".encode("utf-8"))
            clients.append(client_socket)

            thread = threading.Thread(target=handle_client, args=(client_socket, player_number), daemon=True)
            thread.start()

    accept_thread = threading.Thread(target=accept_connections, daemon=True)
    accept_thread.start()

    while True:
        try:
            message = input()
            if message.lower() == "quit":
                for client in clients:
                    client.send(message.encode("utf-8"))
                break
            for client in clients:
                client.send(message.encode("utf-8"))
        except KeyboardInterrupt:
            for client in clients:
                client.send("quit".encode("utf-8"))
            break

    for client in clients:
        client.close()
    server_socket.close()

if __name__ == '__main__':
    main()
