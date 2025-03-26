import socket
import threading
import pygame
from shared import GameState, game_state  # Assumes GameState and game_state are defined in shared.py

MAX_PLAYERS = 4
HOST = '0.0.0.0'
TCP_PORT = 5555    
UDP_PORT = 5556

# --- Global Variables
numOfPlayers = 0
connections = []        # List of TCP connections
udp_connections = {}    # Dictionary to store client UDP addresses corresponding to which player
scores = {}             # Dictionary that corresponds the (address, port) with each individual score
running = True          # Global flag to control loops

def broadcast_tcp(message):
    """Send a message to all players via TCP."""
    for conn in connections[:]:
        try:
            conn.send(message.encode())
        except Exception as e:
            print("TCP broadcast error:", e)
            if conn in connections:
                connections.remove(conn)

def broadcast_udp(message):
    """Send a message to all players via UDP."""
    for addr in list(udp_connections.keys()):
        try:
            udp_socket.sendto(message.encode(), addr)
        except Exception as e:
            print("UDP broadcast error:", e) 

def handle_client(conn, addr):
    """Handles player connections in the TCP lobby."""
    global numOfPlayers, game_state
    numOfPlayers += 1
    player_id = f"player{numOfPlayers}"
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
    except Exception as e:
        # Log any error (e.g., ConnectionResetError when client abruptly disconnects)
        print(f"Error with {player_id}: {e}")
    finally:
        numOfPlayers -= 1
        if conn in connections:
            connections.remove(conn)
        conn.close()
        
        disconnect_msg = f"{player_id} has disconnected."
        print(disconnect_msg)
        broadcast_tcp(disconnect_msg)

        # If the game is in progress and there are now fewer than 2 players, end the game.
        if game_state == GameState.IN_PROGRESS and numOfPlayers < 2:
            print("Not enough players, ending game...")
            broadcast_tcp("Game ended due to disconnection.")
            game_state = GameState.WAITING

def udp_server():
    """Handles UDP communication during game mode."""
    global udp_socket, game_state, scores, running
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))
    udp_socket.settimeout(1.0)  # Use a timeout to allow periodic checks of the running flag

    while running:
        try:
            data, addr = udp_socket.recvfrom(1024)
        except socket.timeout:
            continue
        except Exception as e:
            print("UDP server error:", e)
            break

        msg = data.decode().strip().lower()

        if msg == "quit":
            print("Received UDP 'quit' – ending game, back to TCP lobby.")
            broadcast_tcp("Game ended. Back to lobby.")
            game_state = GameState.WAITING
            continue

        elif msg == "cookie":
            print(f"Received data from ", udp_connections[addr])
            scores[addr] += 1   # Add score to the one who pressed it, so it's not a global score.
            print(f"Cookie collected from {udp_connections[addr]} ! New score:", scores[addr])
            broadcast_udp(f"Score: {scores[addr]}")
            continue

        # Register new UDP addresses if not already registered.
        if addr not in udp_connections.keys():
            player_id = f"player{len(udp_connections) + 2}"
            udp_connections[addr] = player_id
            scores[addr] = 0        # Initialize the score to be 0 first.
            print(f"Added {player_id} with address {addr} to UDP connections.")

        broadcast_udp(data.decode())

def accept_clients(server_socket):
    """Accepts TCP client connections; disconnects new clients if maximum reached."""
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
            print(f"Too many players connected! Disconnecting client {addr}")
            try:
                conn.send("Server is full. Please try again later.".encode())
            except Exception as e:
                print(f"Error sending full-server message: {e}")
            conn.close()

def server():
    global game_state, numOfPlayers, score, running
    # Initialize Pygame window for the server
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Server Game Window")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, TCP_PORT))
    server_socket.listen(MAX_PLAYERS)
    
    print("Server is running. Waiting for players...")

    # Start the UDP and TCP threads.
    threading.Thread(target=udp_server, daemon=True).start()
    threading.Thread(target=accept_clients, args=(server_socket,), daemon=True).start()

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # In the lobby mode, press 's' to start the game (if enough players are connected)
                    if game_state == GameState.WAITING:
                        if event.key == pygame.K_s:
                            if numOfPlayers < 2:
                                print("Minimum amount of players is 2!")
                            else:
                                print("Game has started")
                                broadcast_tcp("Game has started")
                                game_state = GameState.IN_PROGRESS
                    # In game mode, press SPACE to collect a cookie or 'q' to quit the game
                    elif game_state == GameState.IN_PROGRESS:
                        if event.key == pygame.K_SPACE:
                            score += 1
                            print("Cookie collected from server! New score:", score)
                            broadcast_udp(f"Score: {score}")
                        elif event.key == pygame.K_q:
                            print("Ending game, back to TCP lobby.")
                            broadcast_udp("quit")  # Notify clients via UDP.
                            broadcast_tcp("Game ended. Back to lobby.")
                            game_state = GameState.WAITING

            # Update the Pygame window with current state and score.
            screen.fill((50, 50, 50))
            state_text = font.render(f"State: {game_state.value} | Players: {numOfPlayers}", True, (255, 255, 255))
            screen.blit(state_text, (20, 20))
            if game_state == GameState.WAITING:
                instruct_text = font.render("Press 's' to start game (min 2 players)", True, (255, 255, 255))
            else:
                instruct_text = font.render("Press SPACE for cookie, 'q' to quit game", True, (255, 255, 255))
            screen.blit(instruct_text, (20, 60))
            pygame.display.flip()
            clock.tick(60)

    except KeyboardInterrupt:
        print("Server shutting down due to KeyboardInterrupt.")
    finally:
        running = False
        # Close all client connections and server socket
        for conn in connections:
            conn.close()
        server_socket.close()
        pygame.quit()
        print("Server closed.")

if __name__ == '__main__':
    server()
