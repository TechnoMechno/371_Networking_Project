import socket
import threading

MAX_PLAYERS = 4
HOST = '0.0.0.0'
TCP_PORT = 5555
UDP_PORT = 5556

# --- Global Variables
numOfPlayers = 0
connections = []
udp_connections = {}
scores = {}
running = True

class GameState:
    WAITING = 0
    IN_PROGRESS = 1
    GAME_OVER = 2

game_state = GameState.WAITING

def broadcast_tcp(message):
    for conn in connections[:]:
        try:
            conn.send(message.encode())
        except Exception as e:
            print("TCP broadcast error:", e)
            if conn in connections:
                connections.remove(conn)

def broadcast_udp(message):
    for addr in list(udp_connections.keys()):
        try:
            udp_socket.sendto(message.encode(), addr)
        except Exception as e:
            print("UDP broadcast error:", e)

def handle_client(conn, addr):
    global numOfPlayers,  game_state
    numOfPlayers += 1
    player_id = numOfPlayers
    connections.append(conn)

    player_name = f"player{player_id}"
    if player_id == 1:
        conn.send(f"{player_name}:FIRST_PLAYER".encode())
    else:
        conn.send(f"{player_name}:WAITING_FOR_START".encode())

    print(f"{player_name} has joined the lobby.")
    broadcast_tcp(f"{player_name} has joined the lobby.")

    try:
        while True:
            msg = conn.recv(1024).decode().strip()
            if not msg:
                break

            if msg.lower() == 'quit':
                break

            if msg == "REQUEST_START":
                if player_id == 1 and game_state == GameState.WAITING:
                    if numOfPlayers >= 2:
                        print("Game has started by player1 (TCP)")
                        broadcast_tcp("GAME_START")
                        game_state = GameState.IN_PROGRESS
                    else:
                        conn.send(f"{player_name}:NEED_MORE_PLAYERS".encode())

    except Exception as e:
        print(f"Error with {player_name}: {e}")
    finally:
        numOfPlayers -= 1
        if conn in connections:
            connections.remove(conn)
        conn.close()

        print(f"{player_name} has disconnected.")
        broadcast_tcp(f"{player_name} has disconnected.")

        if game_state == GameState.IN_PROGRESS and numOfPlayers < 2:
            print("Not enough players, ending game...")
            broadcast_tcp("Game ended due to disconnection.")
            game_state = GameState.WAITING

def udp_server():
    global udp_socket, game_state, scores, running
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))
    udp_socket.settimeout(1.0)

    while running:
        try:
            data, addr = udp_socket.recvfrom(1024)
        except socket.timeout:
            continue
        except Exception as e:
            print("UDP server error:", e)
            break

        msg = data.decode().strip().lower()

        if addr not in udp_connections:
            if not udp_connections:
                player_id = "player1"
            else:
                player_id = f"player{len(udp_connections) + 1}"
            udp_connections[addr] = player_id
            scores[addr] = 0
            print(f"Added {player_id} with address {addr} to UDP connections.")

        if msg == "start":
            if udp_connections[addr] == "player1" and game_state == GameState.WAITING:
                if numOfPlayers >= 2:
                    print("Game has started by player1 (UDP)")
                    broadcast_tcp("GAME_START")
                    game_state = GameState.IN_PROGRESS
                else:
                    udp_socket.sendto("NEED_MORE_PLAYERS".encode(), addr)
            continue

        if msg == "quit":
            print("Received UDP 'quit'")
            broadcast_tcp("Game ended. Back to lobby.")
            game_state = GameState.WAITING
            continue

        if msg == "cookie":
            scores[addr] += 1
            print(f"Cookie collected from {udp_connections[addr]}! New score: {scores[addr]}")
            broadcast_udp(f"Score: {scores[addr]}")
            continue

        broadcast_udp(data.decode())

def accept_clients(server_socket):
    global running
    server_socket.settimeout(1.0)
    while running:
        try:
            conn, addr = server_socket.accept()
        except socket.timeout:
            continue
        except Exception as e:
            print("TCP accept error:", e)
            break
        if numOfPlayers < MAX_PLAYERS:
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        else:
            print(f"Too many players connected! Disconnecting {addr}")
            try:
                conn.send("Server is full. Please try again later.".encode())
            except:
                pass
            conn.close()

def server():
    global game_state, running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # <--- Add this line
    server_socket.bind((HOST, TCP_PORT))
    server_socket.listen(MAX_PLAYERS)

    print("Server is running. Waiting for players...")

    threading.Thread(target=udp_server, daemon=True).start()
    threading.Thread(target=accept_clients, args=(server_socket,), daemon=True).start()

    try:
        while running:
            pass
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        running = False
        for conn in connections:
            conn.close()
        server_socket.close()
        print("Server closed.")


if __name__ == '__main__':
    server()
