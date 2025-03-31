# GameStateManager.py
import threading
import json
import math
import random
from game_code.player import Player
from game_code.cookie_refactored import Cookie
from game_code.config import SCREEN_WIDTH, SCREEN_HEIGHT, COOKIE_COUNT
from game_code.Plate import Plate

# -------------------------------------------------------------
# This module maintains the authoritative game state on the server.
# It manages players, cookies, and client addresses, processes incoming
# JSON messages from clients, and provides the full game state as a dictionary
# for broadcasting to connected clients.
# -------------------------------------------------------------

class GameState:
    MENU = 0
    LOBBY = 1
    PLAYING = 2
    GAME_OVER = 3

class GameStateManager:
    def __init__(self):
        # Dictionaries to hold game objects
        self.players = {}           # Format: {player_id: Player}
        self.cookies = {}           # Format: {cookie_id: Cookie}
        self.client_addresses = {}  # Format: {addr: player_id}
        self.game_state = GameState.MENU
        
        self.next_player_id = 1     # Incrementing player id
        self.lock = threading.Lock()  # For thread safety
        
        # Create the central plate (for example, centered in the screen)
        central_position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        central_plate_radius = 260  # or any value you choose
        self.central_plate = Plate(central_position, central_plate_radius)

        # # Initialize any initial game objects (example: create some cookies)
        # for i in range(5):
        #     self.cookies[i] = Cookie(cookie_id=i, position=[200 + i * 100, 300])
            
        # Randomly spawn cookies
        spread_radius = 150  # Increased spread for more dispersion
        for i in range(COOKIE_COUNT):
            r = spread_radius * math.sqrt(random.random())
            theta = random.uniform(0, 2 * math.pi)
            x = self.central_plate.position[0] + r * math.cos(theta)
            y = self.central_plate.position[1] + r * math.sin(theta)
            
            cookie_type = "star" if i % 2 == 0 else "regular"
            self.cookies[i] = Cookie(cookie_id=i, position=[x, y])

    def handle_message(self, message, addr, udp_socket):
        """
        Processes a JSON message from a client.
        - If addr is new, register a new Player.
        - Otherwise, update state based on the unified 'update' message.
        """
        try:
            data_obj = json.loads(message)
        except Exception as e:
            print("JSON error in handle_message:", e)
            return
        
        with self.lock:
            # Register new client if not present
            if addr not in self.client_addresses:
                if self.next_player_id <= 4:  # Limit to 4 players
                    player_id = self.next_player_id
                    self.next_player_id += 1
                    self.client_addresses[addr] = player_id
                    # Calculate plate position based on screen dimensions (you may refine this)
                    plate_position = self.calculate_plate_position(player_id, SCREEN_WIDTH, SCREEN_HEIGHT)
                    self.players[player_id] = Player(player_id, addr, plate_position, plate_radius=150)
                    # Send assign_id message to client
                    assign_msg = {"type": "assign_id", "player_id": player_id}
                    udp_socket.sendto(json.dumps(assign_msg).encode(), addr)
                    print(f"Registered new player {player_id} from {addr}")
                else:
                    # Server full, optionally send a "server_full" message.
                    udp_socket.sendto(json.dumps({"type": "server_full"}).encode(), addr)
                    return

            # Process a unified update message from a client.
            if data_obj.get("type") == "update":
                player_id = self.client_addresses[addr]
                # Update the player's mouse position
                self.players[player_id].mouse_pos = data_obj.get("position", self.players[player_id].mouse_pos)
                # Debug print: show the player's updated mouse position and dragged cookie value
                dragged = data_obj.get("dragged_cookie")
                print(f"Received update from player {player_id}: pos={self.players[player_id].mouse_pos}, dragged_cookie={dragged}")
                
                # Process dragging: 'dragged_cookie' might be null or a cookie id
                dragged = data_obj.get("dragged_cookie")
                if dragged is None:
                    # Release any cookie locked by this player.
                    for cookie in self.cookies.values():
                        if cookie.locked_by == player_id:
                            snapped = cookie.snap_to_player_plate(self.players[player_id])
                            if not snapped:
                                # If not snapped, revert to original position.
                                cookie.update_position(cookie.original_position)
                            cookie.locked_by = None
                else:
                    # The client is dragging a cookie.
                    dragged = int(dragged)
                    cookie = self.cookies.get(dragged)
                    
                    if cookie:
                        # For additional safety, check if the mouse is over the cookie.
                        if cookie.is_clicked(self.players[player_id].mouse_pos):
                            # Lock the cookie to this player and update its position.
                            if cookie.locked_by is None or cookie.locked_by == player_id:
                                cookie.locked_by = player_id
                                cookie.update_position(self.players[player_id].mouse_pos)
                                
                                
    def update_dragged_cookies(self):
        with self.lock:
            for cookie in self.cookies.values():
                if cookie.locked_by is not None and cookie.locked_by in self.players:
                    old_pos = cookie.position.copy()
                    cookie.update_position(self.players[cookie.locked_by].mouse_pos)

    def get_game_data(self):
        """
        Returns the full game state as a dictionary for broadcasting.
        """
        with self.lock:
            state = {
                "type": "update_state",
                "game_state": self.game_state,
                "central_plate": self.central_plate.to_dict(),
                "cookies": {str(cid): cookie.to_dict() for cid, cookie in self.cookies.items()},
                "players": {str(pid): player.to_dict() for pid, player in self.players.items()}
            }
        return state

    def get_all_client_addresses(self):
        """
        Returns a list of all client addresses.
        """
        with self.lock:
            return list(self.client_addresses.keys())
        
    @staticmethod
    def calculate_plate_position(player_index, screen_width, screen_height, margin=30, plate_radius=150):
        # For players 1 and 3, x is on the left; for 2 and 4, on the right.
        x = margin + plate_radius if player_index % 2 == 1 else screen_width - margin - plate_radius
        # For players 1 and 2, y is on the top; for 3 and 4, on the bottom.
        y = margin + plate_radius if player_index <= 2 else screen_height - margin - plate_radius
        return [x, y]