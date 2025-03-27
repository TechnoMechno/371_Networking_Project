import socket
import threading
import time
import json
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR
from player import Player   # Assumes Player is defined in player.py
from cookie_server import Cookie   # Assumes Cookie is defined in cookie_server.py

MAX_PLAYERS = 4
HOST = '0.0.0.0'
UDP_PORT = 5555  # Use a single UDP port for all communication

# --- Global Variables ---
numOfPlayers = 0
players = {}           # Format: {player_id: Player}
cookies = {}           # Format: {cookie_id: Cookie}
udp_connections = {}   # Format: {addr: player_id}
running = True
data_lock = threading.Lock()  # Lock for thread safety

# Define game states (simple enum)
class GameState:
    BEFORE_START = 0
    PLAYING = 1
    GAME_OVER = 2

game_state = GameState.BEFORE_START

# --- Helper Function for Plate Positioning ---
def calculate_plate_position(player_index, screen_width, screen_height, margin=30, plate_radius=150):
    positions = {
        1: [margin + plate_radius, margin + plate_radius],
        2: [screen_width - margin - plate_radius, margin + plate_radius],
        3: [margin + plate_radius, screen_height - margin - plate_radius],
        4: [screen_width - margin - plate_radius, screen_height - margin - plate_radius]
    }
    return positions.get(player_index, [screen_width // 2, screen_height // 2])

# --- UDP Broadcast Function ---
def broadcast_udp(message, udp_socket):
    """Send a message to all connected clients via UDP."""
    for addr in list(udp_connections.keys()):
        try:
            udp_socket.sendto(message.encode(), addr)
        except Exception as e:
            print("UDP broadcast error:", e)

# --- Message Handler ---
def handle_message(message, addr, udp_socket):
    """
    Process messages from clients over UDP.
    Assign new players if necessary and update game state.
    """
    global numOfPlayers, game_state
    try:
        data_obj = json.loads(message)
    except Exception as e:
        print(f"JSON error: {e}")
        return

    with data_lock:
        # Register new client if not seen before
        if addr not in udp_connections:
            if numOfPlayers >= MAX_PLAYERS:
                # Inform the client the server is full
                full_msg = json.dumps({'type': 'server_full'})
                udp_socket.sendto(full_msg.encode(), addr)
                return
            numOfPlayers += 1
            player_id = numOfPlayers
            udp_connections[addr] = player_id
            # Calculate player's plate position and create a Player object
            plate_pos = calculate_plate_position(player_id, SCREEN_WIDTH, SCREEN_HEIGHT)
            new_player = Player(player_id, addr, plate_position=plate_pos, plate_radius=150)
            players[player_id] = new_player
            # Send assign_id message to client
            assign_msg = json.dumps({'type': 'assign_id', 'player_id': player_id})
            udp_socket.sendto(assign_msg.encode(), addr)
            join_msg = f"Player {player_id} has joined."
            print(join_msg)
            broadcast_udp(json.dumps({'type': 'join', 'message': join_msg}), udp_socket)
        else:
            player_id = udp_connections[addr]

        # Process message types
        if data_obj['type'] == 'mouse_move':
            # Update player's mouse position
            players[player_id].mouse_pos = data_obj['position']
        elif data_obj['type'] == 'start_drag':
            cookie_id = data_obj['cookie_id']
            # If cookie exists and is not already locked, lock it for this player
            if cookie_id in cookies and cookies[cookie_id].locked_by is None:
                cookies[cookie_id].locked_by = player_id
        elif data_obj['type'] == 'stop_drag':
            # Unlock any cookie that this player was dragging
            for cookie in cookies.values():
                if cookie.locked_by == player_id:
                    cookie.locked_by = None
        elif data_obj['type'] == 'start_game':
            # Only allow player 1 (host) to start the game
            if player_id == 1:
                game_state = GameState.PLAYING
                broadcast_udp(json.dumps({'type': 'game_started'}), udp_socket)
        elif data_obj['type'] == 'quit':
            # Handle client quit: remove player from our records
            if addr in udp_connections:
                del udp_connections[addr]
            if player_id in players:
                del players[player_id]
            numOfPlayers -= 1
            leave_msg = f"Player {player_id} has left."
            print(leave_msg)
            broadcast_udp(json.dumps({'type': 'player_left', 'message': leave_msg}), udp_socket)

# --- UDP Server Loop ---
def udp_server():
    """Continuously receives messages from clients and updates game state."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))
    udp_socket.settimeout(1.0)

    while running:
        try:
            data, addr = udp_socket.recvfrom(4096)
        except socket.timeout:
            continue
        except Exception as e:
            print("UDP server error:", e)
            break
        message = data.decode()
        handle_message(message, addr, udp_socket)

        # Update positions of cookies if they are locked
        with data_lock:
            for cookie in cookies.values():
                if cookie.locked_by is not None and cookie.locked_by in players:
                    cookie.position = players[cookie.locked_by].mouse_pos

            # Prepare an update message with current state
            update_msg = {
                'type': 'update_state',
                'cookies': {str(cid): cookies[cid].to_dict() for cid in cookies},
                'players': {str(pid): players[pid].to_dict() for pid in players}
            }
            update_json = json.dumps(update_msg)
            broadcast_udp(update_json, udp_socket)
        time.sleep(1/60)

# --- Main Server Function with Pygame UI ---
def server():
    global running, game_state, numOfPlayers
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("UDP Server")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    # Create a UDP socket for the main thread (for broadcasting via UI events)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))
    udp_socket.settimeout(1.0)

    # Create initial cookies for the game
    with data_lock:
        for i in range(5):
            cookies[i] = Cookie(cookie_id=i, position=[200 + i * 100, 300])

    # Start the UDP server loop in a separate thread
    threading.Thread(target=udp_server, daemon=True).start()

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if game_state == GameState.BEFORE_START:
                        if event.key == pygame.K_s:
                            if numOfPlayers < 2:
                                print("Minimum number of players is 2!")
                            else:
                                print("Game has started.")
                                game_state = GameState.PLAYING
                                broadcast_udp(json.dumps({'type': 'game_started'}), udp_socket)
                    elif game_state == GameState.PLAYING:
                        if event.key == pygame.K_q:
                            print("Ending game, returning to lobby.")
                            game_state = GameState.BEFORE_START
                            broadcast_udp(json.dumps({'type': 'quit'}), udp_socket)
            
            # Update server UI
            screen.fill(BACKGROUND_COLOR)
            state_text = font.render(f"State: {game_state} | Players: {numOfPlayers}", True, (255, 255, 255))
            screen.blit(state_text, (20, 20))
            if game_state == GameState.BEFORE_START:
                instruct_text = font.render("Press 's' to start game (min 2 players)", True, (255, 255, 255))
            else:
                instruct_text = font.render("Game in progress. Press 'q' to quit game", True, (255, 255, 255))
            screen.blit(instruct_text, (20, 60))
            pygame.display.flip()
            clock.tick(60)
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        running = False
        pygame.quit()
        udp_socket.close()
        print("Server closed.")

if __name__ == '__main__':
    server()